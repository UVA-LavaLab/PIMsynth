#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: memir_driver.py
Description: Driver for the memir scheduler (linear-scan and CP-SAT).
    Invokes the memirc binary on a .pim_ir1 file and produces a .pim_ir2 file.

    memir reads .pim_ir1 natively and outputs .pim_ir2-compatible format,
    so no IR translation is needed.

Author: Deyuan Guo <guodeyuan@gmail.com>
"""

import argparse
import os
import subprocess
import sys


_script_dir = os.path.dirname(os.path.abspath(__file__))


def _generate_run_script(cmd, outdir, filename):
    """Generate a shell script that reproduces a command."""
    run_file = os.path.join(outdir, filename)
    with open(run_file, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write('cd $(dirname "$0")/..\n')
        f.write(' '.join(cmd) + '\n')
    os.chmod(run_file, 0o755)
    print("INFO: Created run script:", run_file)


ALGO_MAP = {
    'memir-lscan': 'linear-scan',
    'memir-cp': 'cp',
}


def _find_memirc():
    """Locate the memirc binary under the memir submodule."""
    release = os.path.join(_script_dir, 'memir', 'target', 'release', 'memirc')
    debug = os.path.join(_script_dir, 'memir', 'target', 'debug', 'memirc')
    if os.path.isfile(release):
        return release
    if os.path.isfile(debug):
        return debug
    return None


def run(scheduler_name, ir1_file, outdir, output, module_name, num_regs,
        pim_mode, timeout=100, time_backoff=False, **_kwargs):
    """Run the memir scheduler: .pim_ir1 -> memirc -> .pim_ir2

    Args:
        scheduler_name: 'memir-lscan' or 'memir-cp'
        ir1_file: Input PIM IR-1 file path.
        outdir: Output directory.
        output: Output filename prefix.
        module_name: Module name (unused -- memir reads it from the file).
        num_regs: Number of registers.
        pim_mode: PIM mode ('digital' or 'analog').
        timeout: Solver timeout in seconds (CP-SAT only).
        time_backoff: Double timeout on solver failure.
    """
    memirc = _find_memirc()
    if memirc is None:
        raise FileNotFoundError(
            "Cannot find memirc binary. Run 'make memir' from the project root.")

    algo = ALGO_MAP.get(scheduler_name)
    if algo is None:
        raise ValueError(f"Unknown memir scheduler: {scheduler_name}. "
                         f"Available: {list(ALGO_MAP.keys())}")

    ir2_file = os.path.join(outdir, output + '.pim_ir2')

    cmd = [memirc, '-a', algo, '-r', str(num_regs)]
    if algo == 'cp':
        cmd += ['-t', str(timeout)]
        if time_backoff:
            cmd.append('-b')
    cmd += [ir1_file, ir2_file]

    _generate_run_script(cmd, outdir, output + '.run_memir.sh')

    print(f"INFO: Running memirc ({algo}): {ir1_file} -> {ir2_file}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stderr:
        for line in result.stderr.strip().splitlines():
            print(f"  memirc: {line}")

    if result.returncode != 0:
        raise RuntimeError(
            f"memirc failed (exit {result.returncode}):\n{result.stderr}")

    if not os.path.isfile(ir2_file):
        raise FileNotFoundError(f"memirc did not produce output: {ir2_file}")

    print(f"INFO: Generated PIM IR-2 file: {ir2_file}")

    toml_file = os.path.splitext(ir2_file)[0] + '.toml'
    if os.path.isfile(toml_file):
        print(f"INFO: memir report: {toml_file}")


if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description='memir scheduler driver: .pim_ir1 -> memirc -> .pim_ir2')
    ap.add_argument('--ir1-file', '-i', required=True, help='Input PIM IR-1 file')
    ap.add_argument('--scheduler', '-s', default='memir-cp',
                    choices=list(ALGO_MAP.keys()), help='Scheduler variant')
    ap.add_argument('--module-name', '-m', default='top', help='Module name')
    ap.add_argument('--num-regs', '-r', type=int, default=4, help='Num regs')
    ap.add_argument('--pim-mode', '-p', default='digital',
                    choices=['digital', 'analog'], help='PIM mode')
    ap.add_argument('--timeout', '-t', type=int, default=100,
                    help='Solver timeout in seconds')
    ap.add_argument('--time-backoff', '-b', action='store_true',
                    help='Double timeout on solver failure')
    ap.add_argument('--outdir', default='.', help='Output directory')
    ap.add_argument('--output', default='tmp', help='Output name prefix')
    args = ap.parse_args()

    run(scheduler_name=args.scheduler,
        ir1_file=args.ir1_file,
        outdir=args.outdir,
        output=args.output,
        module_name=args.module_name,
        num_regs=args.num_regs,
        pim_mode=args.pim_mode,
        timeout=args.timeout,
        time_backoff=args.time_backoff)
