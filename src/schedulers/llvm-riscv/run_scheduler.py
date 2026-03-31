#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: run_scheduler.py
Description: LLVM RISC-V scheduler entry point.
    Pipeline: .pim_ir1 -> .c -> clang -> .s -> RISC-V asm parser/translator -> .hpp
Author: Deyuan Guo <guodeyuan@gmail.com>
"""

import os
import sys
import subprocess
import argparse

_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)
sys.path.insert(0, os.path.join(_script_dir, '..', '..', 'utils'))
sys.path.insert(0, os.path.join(_script_dir, '..', '..', 'code-gen'))

from pim_ir1_reader import read_pim_ir1
from pim_ir1_to_inline_asm_translator import translate_ir1_to_c
from riscv_asm_parser import Parser
from riscv_asm_translator import AsmTranslator
from stats_generator import StatsGenerator
from code_gen_pimeval_digital import PimEvalAPIDigitalCodeGenerator
from code_gen_pimeval_analog import PimEvalAPIAnalogCodeGenerator
from util import getFileLines, writeToFile


def run_clang(c_file, asm_file, clang_path, clang_g=True, llvm_args=''):
    """Compile C with RISC-V inline assembly to .s via clang.

    Returns the clang command list (for run script generation).
    """
    cmd = [clang_path, '-O3', '-target', 'riscv32-unknown-elf', '-S',
           c_file, '-o', asm_file]
    if clang_g:
        cmd.append('-g')
    if llvm_args:
        cmd += llvm_args.split()
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError('clang compilation failed')
    return cmd


def run_asm_to_hpp(asm_file, hpp_file, module_name, num_regs, pim_mode):
    """Parse RISC-V assembly and generate PIMeval HPP."""
    lines = getFileLines(asm_file)

    parser = Parser(moduleName=module_name)
    parser.parse(lines)

    asm_translator = AsmTranslator(
        parser.statementList,
        list(set(parser.inputList)),
        list(set(parser.outputList)),
        pimMode=pim_mode,
        numRegs=num_regs,
        debugLevel=0,
    )
    asm_translator.translate()
    asm_translator.post_translation_optimization()
    bit_serial_asm = asm_translator.getBitSerialAsm()

    stats = StatsGenerator(bit_serial_asm).generateStats()
    print("Info: ", stats)

    generator_map = {
        'analog': PimEvalAPIAnalogCodeGenerator,
        'digital': PimEvalAPIDigitalCodeGenerator,
    }
    if pim_mode not in generator_map:
        raise ValueError(f"Unsupported PIM mode: {pim_mode}")

    generator = generator_map[pim_mode](
        bit_serial_asm, module_name, asm_translator.ports)
    code = f"//{stats}\n" + generator.generateCode()
    writeToFile(hpp_file, code)


def _generate_run_script(cmd, outdir, output, filename):
    """Generate a shell script that reproduces a command."""
    run_file = os.path.join(outdir, filename)
    with open(run_file, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write('cd $(dirname "$0")/..\n')
        f.write(' '.join(cmd) + '\n')
    os.chmod(run_file, 0o755)
    print("INFO: Created run script:", run_file)


def run(ir1_file, outdir, output, module_name, num_regs, pim_mode,
        clang_path, clang_g=True, llvm_args='', **_kwargs):
    """Run the full LLVM RISC-V scheduler pipeline: .pim_ir1 -> .c -> .s -> .hpp

    Args:
        ir1_file: Input PIM IR-1 file (pre-scheduling).
    """
    c_file = os.path.join(outdir, output + '.c')
    asm_file = os.path.join(outdir, output + '.s')
    hpp_file = os.path.join(outdir, output + '.hpp')

    print("INFO: Translating PIM IR-1 to inline assembly C ...")
    ir1_data = read_pim_ir1(ir1_file)
    c_code = translate_ir1_to_c(ir1_data)
    writeToFile(c_file, c_code)
    print("INFO: Generated C file:", c_file)

    print("INFO: Compiling C to RISC-V ASM ...")
    clang_cmd = run_clang(c_file, asm_file, clang_path, clang_g, llvm_args)
    _generate_run_script(clang_cmd, outdir, output, output + '.run_clang.sh')
    print("INFO: Generated ASM file:", asm_file)

    print("INFO: Compiling RISC-V ASM to PIM API ...")
    run_asm_to_hpp(asm_file, hpp_file, module_name, num_regs, pim_mode)
    print("INFO: Generated HPP file:", hpp_file)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description='LLVM RISC-V scheduler: .pim_ir1 -> .c -> .s -> .hpp')
    ap.add_argument('--ir1-file', '-i', required=True, help='Input PIM IR-1 file')
    ap.add_argument('--module-name', '-m', required=True, help='Module name')
    ap.add_argument('--num-regs', '-r', type=int, default=4, help='Num regs')
    ap.add_argument('--pim-mode', '-p', default='digital',
                    choices=['digital', 'analog'], help='PIM mode')
    ap.add_argument('--clang-path', required=True, help='Path to clang')
    ap.add_argument('--clang-g', action='store_true', default=True,
                    help='Pass -g to clang')
    ap.add_argument('--llvm-args', default='', help='Extra LLVM args')
    ap.add_argument('--outdir', default='.', help='Output directory')
    ap.add_argument('--output', default='tmp', help='Output name prefix')
    args = ap.parse_args()

    run(ir1_file=args.ir1_file,
        module_name=args.module_name, num_regs=args.num_regs,
        pim_mode=args.pim_mode, clang_path=args.clang_path,
        clang_g=args.clang_g, llvm_args=args.llvm_args,
        outdir=args.outdir, output=args.output)
