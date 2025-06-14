#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: bit_serial_compiler.py
Description: Bit-Serial Compiler Main Flow
Author: Deyuan Guo <guodeyuan@gmail.com>
Date: 2024-09-20
"""

import argparse
import os
import sys
import subprocess
import textwrap


class bitSerialCompiler:
    """
    Bit-Serial Compiler
    """

    def __init__(self, args=[]):
        """ Init """
        self.args = args.copy()
        self.verilog = []
        self.genlib = ''
        self.aig = ''
        self.blif = ''
        self.c = ''
        self.asm = ''
        self.output = ''
        self.outdir = ''
        self.num_regs = 0
        self.from_stage = ''
        self.to_stage = ''
        self.stages = {'verilog':1, 'blif':2, 'c':3, 'asm':4, 'pim':5, 'test':6}
        self.abc_path = ''
        self.yosys_path = ''
        self.clang_path = ''
        self.yosys_fe = True
        self.clang_g = False
        self.llvm_args = ''
        self.top_module = ''
        self.gen_run_sh = False
        self.gen_bitwise = False
        self.pim_mode = ''
        self.impl_type = None
        self.parser = self.create_argparse()
        self.hbar = "============================================================"

    def run(self):
        """ Run bit-serial compiler """
        print(" ---------------------")
        print("| Bit-Serial Compiler |")
        print(" ---------------------")
        if not self.args:
            print("No input. Run with -h or --help to see more options.")
            return True

        success = self.parse_args()
        if not success:
            return False

        if not self.locate_abc_path():
            return False
        if not self.locate_yosys_path():
            return False
        if not self.locate_clang_path():
            return False

        self.report_params()

        if not self.create_outdir_if_needed():
            return False

        if self.stages[self.from_stage] <= self.stages['verilog'] and self.stages[self.to_stage] >= self.stages['blif']:
            success = self.run_verilog_to_blif()
            if not success:
                return False

        if self.stages[self.from_stage] <= self.stages['blif'] and self.stages[self.to_stage] >= self.stages['c']:
            success = self.run_blif_to_c()
            if not success:
                return False

        if self.stages[self.from_stage] <= self.stages['c'] and self.stages[self.to_stage] >= self.stages['asm']:
            success = self.run_c_to_asm()
            if not success:
                return False

        if self.stages[self.from_stage] <= self.stages['asm'] and self.stages[self.to_stage] >= self.stages['pim']:
            success = self.run_asm_to_pim()
            if not success:
                return False

        if self.stages[self.from_stage] <= self.stages['pim'] and self.stages[self.to_stage] >= self.stages['test']:
            success = self.run_pim_to_test()
            if not success:
                return False


        print("INFO: Bit-serial compilation completed.")
        return True

    def create_argparse(self):
        """ Create argparse """
        extra_help_msg = textwrap.dedent("""
        how to use:
          Input requirements:
            --from-stage verilog    require --verilog and --genlib
            --from-stage blif       require --blif
            --from-stage c          require --c
            --from-stage asm        require --asm
        """)
        parser = argparse.ArgumentParser(epilog=extra_help_msg, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('--verilog', metavar='[files]', type=str, default='', help='Input Verilog files', nargs='+')
        parser.add_argument('--genlib', metavar='[file]', type=str, default='', help='Input GenLib file')
        parser.add_argument('--blif', metavar='[file]', type=str, default='', help='Input BLIF file')
        parser.add_argument('--c', metavar='[file]', type=str, default='', help='Input C file')
        parser.add_argument('--asm', metavar='[file]', type=str, default='', help='Input ASM file')
        parser.add_argument('--num-regs', metavar='N', type=int, default=4, help='Number of registers 2~19', choices=range(2, 20))
        parser.add_argument('--output', metavar='[filename]', type=str, default='tmp', help='Output filename without suffix')
        parser.add_argument('--outdir', metavar='[path]', type=str, default='.', help='Output location, default current dir')
        parser.add_argument('--from-stage', metavar='[stage]', type=str,
                help='From stage: verilog (default), blif, c, asm, pim',
                choices=self.stages, default='verilog')
        parser.add_argument('--to-stage', metavar='[stage]', type=str,
                help='To stage: verilog, blif, c, asm, pim (default)',
                choices=self.stages, default='test')
        parser.add_argument('--clang-g', action='store_false', help='Toggle clang -g, default true')
        parser.add_argument('--llvm-args', type=str, default='', help='Extra arguments passed to LLVM')
        parser.add_argument('--top-module', metavar='[name]', type=str, default='', help='Specify Verilog top module')
        parser.add_argument('--num-tests', '-n', type=int, default=100, help='Number of test cases.')
        parser.add_argument('--gen-run-sh', action='store_false', help='Generate intermediate run scripts, default true')
        parser.add_argument('--gen-bitwise', action='store_false', help='Generate bit-wise C code, default true')
        parser.add_argument('--pim-mode', type=str, default='digital', choices=['digital', 'analog'], help='The PIM architecture mode (analog/digital).')
        parser.add_argument('--impl-type', type=int, help='Override the IMPL_TYPE Verilog parameter')
        parser.add_argument('--golden-function-path', '-g', type=str, default=None, help='The path to the golden function file hpp file.')
        return parser

    def parse_args(self):
        """ Parse command line arguments """
        args = self.parser.parse_args(self.args)
        self.verilog = args.verilog
        self.genlib = args.genlib
        self.blif = args.blif
        self.c = args.c
        self.asm = args.asm
        for file in self.verilog:
            if not self.sanity_check_input_file(file, 'Verilog'):
                return False
        if (not self.sanity_check_input_file(self.genlib, 'GenLib')
                or not self.sanity_check_input_file(self.blif, 'BLIF')
                or not self.sanity_check_input_file(self.c, 'C')
                or not self.sanity_check_input_file(self.asm, 'ASM')):
            return False
        self.output = args.output
        if not self.output or ' ' in self.output:
            print("Error: Invalid output filename '%s'" % (self.output))
            return False
        self.outdir = args.outdir
        self.from_stage = args.from_stage
        self.to_stage = args.to_stage
        self.num_tests = args.num_tests
        # from/to rule checks
        if self.stages[self.from_stage] >= self.stages[self.to_stage]:
            print("Error: Invalid from-to range: %s -> %s" % (self.from_stage, self.to_stage))
            return False
        if (not self.sanity_check_from_to(self.verilog, 'verilog')
                or not self.sanity_check_from_to(self.genlib, 'genlib', 'verilog')
                or not self.sanity_check_from_to(self.blif, 'blif')
                or not self.sanity_check_from_to(self.c, 'c')
                or not self.sanity_check_from_to(self.asm, 'asm')):
            return False
        self.num_regs = args.num_regs
        self.clang_g = args.clang_g
        self.llvm_args = args.llvm_args
        self.top_module = args.top_module
        self.gen_run_sh = args.gen_run_sh
        self.gen_bitwise = args.gen_bitwise
        self.pim_mode = args.pim_mode
        self.impl_type = args.impl_type
        self.golden_function_path = args.golden_function_path
        return True

    def sanity_check_input_file(self, input_file, tag):
        """ Sanity check for an input file """
        if input_file and not os.path.isfile(input_file):
            print("Error: Cannot find %s file '%s'" % (tag, input_file))
            return False
        return True

    def sanity_check_from_to(self, input_file, arg_name, req_stage=''):
        """ Sanity check for an input file given from-to range """
        is_required = False
        if not req_stage:
            req_stage = arg_name # stage name same as arg name
        if isinstance(req_stage, str):
            is_required = (self.from_stage == req_stage)
        else:
            is_required = (self.stages[self.from_stage] <= self.stages[req_stage[0]] and self.stages[self.to_stage] >= self.stages[req_stage[1]])
        if not input_file and is_required:
            print("Error: Missing required input parameter --%s" % (arg_name))
            return False
        elif input_file and not is_required:
            print("Warning: Ignored input parameter --%s %s" % (arg_name, input_file))
        return True

    def locate_abc_path(self):
        """ Locate abc location """
        script_location = os.path.dirname(os.path.abspath(__file__))
        # TODO: executable path
        self.abc_path = os.path.join(script_location, 'abc/abc')
        if not os.path.isfile(self.abc_path):
            print("Error: Cannot find abc executable at", self.abc_path)
            return False
        return True

    def locate_yosys_path(self):
        """ Locate yosys location """
        script_location = os.path.dirname(os.path.abspath(__file__))
        # TODO: executable path
        self.yosys_path = os.path.join(script_location, 'yosys/yosys')
        if not os.path.isfile(self.yosys_path):
            print("Error: Cannot find yosys executable at", self.yosys_path)
            return False
        return True

    def locate_clang_path(self):
        """ Locate clang location """
        script_location = os.path.dirname(os.path.abspath(__file__))
        # TODO: executable path
        self.clang_path = os.path.join(script_location, 'llvm-build/bin/clang')
        if not os.path.isfile(self.clang_path):
            print("Error: Cannot find clang executable at", self.clang_path)
            return False
        return True

    def report_params(self):
        """ Report input parameters """
        print(self.hbar)
        print("From-to Stage: %s -> %s" % (self.from_stage, self.to_stage))
        if self.verilog:
            print("Input Verilog Files:", self.verilog)
        if self.genlib:
            print("Input GenLib File:", self.genlib)
        if self.blif:
            print("Input BLIF File:", self.blif)
        if self.c:
            print("Input C File:", self.c)
        if self.asm:
            print("Input ASM File:", self.asm)
        if self.output:
            print("Output Filename (without suffix):", self.output)
        if self.outdir:
            print("Output Directory:", self.outdir)
        print("ABC Path:", self.abc_path)
        print("CLANG Path:", self.clang_path)
        print("CLANG -g:", self.clang_g)
        if self.llvm_args:
            print("LLVM args:", self.llvm_args)
        print("Number of Registers:", self.num_regs)
        print(self.hbar)

    def create_outdir_if_needed(self):
        """ Create output directory if needed """
        if os.path.isdir(self.outdir):
            return True
        try:
            os.makedirs(self.outdir)
            if os.path.isdir(self.outdir):
                print("INFO: Create outdir '%s'" % self.outdir)
            else:
                print("Error: Failed to create outdir '%s'" % self.outdir)
                return False
        except Exception as e:
            print("Error: Failed to create outdir '%s': %s" % (self.outdir, e))
            return False
        return True

    def generate_run_script(self, cmd, filename):
        """ Generate run script """
        if not self.gen_run_sh:
            return
        run_file = os.path.join(self.outdir, filename)
        with open(run_file, 'w') as file:
            file.write("#!/bin/bash\n")
            file.write('cd $(dirname "$0")/..\n')
            file.write(' '.join(cmd) + '\n')
        os.chmod(run_file, 0o755)
        print("INFO: Created run script:", run_file)

    def run_verilog_to_blif(self):
        """ Compile Verilog to BLIF """
        print("INFO: Compiling Verilog to BLIF ...")
        if self.yosys_fe:
            return self.run_verilog_to_blif_yosys()
        else:
            return self.run_verilog_to_blif_abc()

    def run_verilog_to_blif_yosys(self):
        """ Compile Verilog to BLIF using yosys verilog frontend and abc tech mapper """
        print("INFO: Creating yosys script (Verilog->Tech-Independent-BLIF)")
        yosys_blif_file = os.path.join(self.outdir, self.output + '.yosys.blif')
        # determine top module
        top_module_opt = ''
        if self.top_module:
            top_module_opt = '-top ' + self.top_module
        elif len(self.verilog) > 1: # use the last file name as top module if not specified
            top_module_opt = '-top ' + os.path.splitext(os.path.basename(self.verilog[-1]))[0]
        else:
            top_module_opt = '-auto-top'
        print("INFO: Identified Verilog top module as:", top_module_opt)
        if self.impl_type is None:
            if self.pim_mode == 'digital':
                impl_type = 0
            elif self.pim_mode == 'analog':
                impl_type = 1
            else:
                raise ValueError(f"Unhandled PIM mode {self.pim_mode} when determining IMPL_TYPE.")
        else:
            impl_type = self.impl_type
        print("INFO: Identified Verilog IMPL_TYPE as:", impl_type)
        yosys_tmpl = textwrap.dedent("""
            # Auto Generated by Bit-Serial Compiler: Verilog to Tech-Independent-BLIF
            log "INFO: Read Verilog"
            read -sv %s
            log "INFO: Set Hierarchy"
            hierarchy %s -chparam IMPL_TYPE %d
            stat
            log "INFO: Optmization"
            proc
            flatten
            opt_expr
            opt_clean
            check
            opt
            stat
            log "INFO: Map Arithmetic Operations"
            # booth
            alumacc
            opt
            opt_clean
            stat
            log "INFO: Tech Independent Mapping"
            techmap
            stat
            write_blif %s
        """ % (" ".join(self.verilog), top_module_opt, impl_type, yosys_blif_file))
        yosys_file = os.path.join(self.outdir, self.output + '.yosys')
        with open(yosys_file, 'w') as file:
            file.write(yosys_tmpl)
        print("INFO: Created yosys script:", yosys_file)

        print("INFO: Running yosys to synthesize Verilog to Tech-Independent-BLIF")
        yosys_log_file = os.path.join(self.outdir, self.output + '.yosys.log')
        cmd = [self.yosys_path, '-s', yosys_file, '-l', yosys_log_file]
        self.generate_run_script(cmd, self.output + '.run_yosys.sh')
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print('Error: yosys synthesizer failed.')
            return False
        print("INFO: Generated Tech-Independent-BLIF file:", yosys_blif_file)

        print(self.hbar)
        print("INFO: Creating ABC script (Tech-Independent-BLIF->BLIF)")
        blif_file = os.path.join(self.outdir, self.output + '.blif')
        abc_tmpl = textwrap.dedent("""
            # Auto Generated by Bit-Serial Compiler: Tech-Independent-BLIF to BLIF
            echo "INFO: Reading Tech-Independent-BLIF"
            read_blif %s
            echo "INFO: Structural Hashing"
            strash
            echo "INFO: Reading GenLib"
            read_genlib %s
            echo "INFO: Tech Mapping"
            map -v
            print_stats
            echo "INFO: Writing BLIF"
            write_blif %s
        """ % (yosys_blif_file, self.genlib, blif_file))
        abc_file = os.path.join(self.outdir, self.output + '.abc')
        with open(abc_file, 'w') as file:
            file.write(abc_tmpl)
        print("INFO: Created ABC script:", abc_file)

        print("INFO: Running ABC to synthesize Tech-Independent-BLIF to BLIF")
        cmd = [self.abc_path, '-f', abc_file]
        self.generate_run_script(cmd, self.output + '.run_abc.sh')
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print('Error: ABC synthesizer failed.')
            return False
        print("INFO: Generated BLIF file:", blif_file)

        print(self.hbar)
        return True

    def run_verilog_to_blif_abc(self):
        """ Compile Verilog to BLIF using abc verilog frontend """
        print("INFO: Creating ABC script (Verilog->BLIF)")
        blif_file = os.path.join(self.outdir, self.output + '.blif')
        abc_tmpl = textwrap.dedent("""
            # Auto Generated by Bit-Serial Compiler: Verilog to BLIF
            echo "INFO: Reading Verilog"
            read_verilog %s
            echo "INFO: Structural Hashing"
            strash
            echo "INFO: Reading GenLib"
            read_genlib %s
            echo "INFO: Tech Mapping"
            map -v
            echo "INFO: Writing BLIF"
            write_blif %s
        """ % (" ".join(self.verilog), self.genlib, blif_file))
        abc_file = os.path.join(self.outdir, self.output + '.abc')
        with open(abc_file, 'w') as file:
            file.write(abc_tmpl)
        print("INFO: Created ABC script:", abc_file)

        print("INFO: Running ABC to synthesize Verilog to BLIF")
        result = subprocess.run([self.abc_path, '-f', abc_file])
        if result.returncode != 0:
            print('Error: ABC synthesizer failed.')
            return False
        print("INFO: Generated BLIF file:", blif_file)

        print(self.hbar)
        return True

    def run_blif_to_c(self):
        """ Compile BLIF to C """
        print("INFO: Compiling BLIF to C ...")

        script_location = os.path.dirname(os.path.abspath(__file__))
        blif_translator = os.path.join(script_location, 'src/blif-translator/main.py')
        blif_file = self.blif if self.blif else os.path.join(self.outdir, self.output + '.blif')
        output_file_prefix = os.path.join(self.outdir, self.output)
        output_formats = 'asm,bitwise' if self.gen_bitwise else 'asm'
        cmd = ['python3', blif_translator, '-f', output_formats, '-i', blif_file, '-m', self.output, '-o', output_file_prefix, '-r', str(self.num_regs), '-p', self.pim_mode]
        self.generate_run_script(cmd, self.output + '.run_blif2c.sh')
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print('Error: BLIF to C parser failed.')
            return False
        print("INFO: Generated C file:", self.output + '.c')
        print("INFO: Allowed number of registers:", self.num_regs)
        if self.gen_bitwise:
            print("INFO: Generated bit-wise C file:", self.output + '.bitwise.c')

        print(self.hbar)
        return True

    def run_c_to_asm(self):
        """ Compile C to ASM """
        print("INFO: Compiling C to RISC-V ASM ...")

        c_file = self.c if self.c else os.path.join(self.outdir, self.output + '.c')
        asm_file = os.path.join(self.outdir, self.output + '.s')
        cmd = [self.clang_path, '-O3', '-target', 'riscv32-unknown-elf', '-S', c_file, '-o', asm_file]
        if self.clang_g:
            cmd.append('-g')
        if self.llvm_args:
            cmd += self.llvm_args.split()
        self.generate_run_script(cmd, self.output + '.run_clang.sh')
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print('Error: CLANG/LLVM failed.')
            return False
        print("INFO: Generated ASM file:", self.output + '.s')

        print(self.hbar)
        return True

    def run_asm_to_pim(self):
        """ Compile ASM to PIM """
        print("INFO: Compiling RISC-V ASM to PIM API ...")

        script_location = os.path.dirname(os.path.abspath(__file__))
        asm_parser = os.path.join(script_location, 'src/asm-parser/main.py')
        asm_file = os.path.join(self.outdir, self.output + '.s')
        cpp_file = os.path.join(self.outdir, self.output + '.hpp')
        cmd = ['python3', asm_parser, '-f', 'cpp', '-i', asm_file, '-m', self.output, '-o', cpp_file, '-p', self.pim_mode]
        self.generate_run_script(cmd, self.output + '.run_asm2pim.sh')
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print('Error: CLANG/LLVM failed.')
            return False
        print("INFO: Generated C++ file:", self.output + '.hpp')

        print(self.hbar)
        return True

    def run_pim_to_test(self):
        """Generate PIMeval test"""
        print("INFO: Generating Test for PIM API ...")

        script_location = os.path.dirname(os.path.abspath(__file__))
        test_gen = os.path.join(script_location, 'src/test-gen/main.py')
        cmd = ['python3', test_gen, '-m', self.output, '-o', self.outdir, '-n', str(self.num_tests), '-p', self.pim_mode]
        if not self.golden_function_path is None:
            cmd.extend(['-g', self.golden_function_path])
        self.generate_run_script(cmd, self.output + '.run_test_gen.sh')
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print('Error: Test Gen failed.')

        print(self.hbar)
        return True

if __name__ == '__main__':
    args = sys.argv[1:]
    compiler = bitSerialCompiler(args)
    success = compiler.run()
    if not success:
        print("Error: Bit-serial compilation failed.")
        sys.exit(1)

