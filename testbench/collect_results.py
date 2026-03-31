#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: collect_results.py
Description: Parse regression output logs and print summary table.
Author: Deyuan Guo <guodeyuan@gmail.com>
"""

import os
import re
import sys


def parse_log(log_path):
    """Parse a log file and extract #R/#W/#L stats and test status."""
    reads, writes, logic = '', '', ''
    pim_test = ''
    bitwise_test = ''

    try:
        with open(log_path, 'r') as f:
            for line in f:
                m = re.search(r'Info:\s+#R/#W/#L:\s*(\d+),\s*(\d+),\s*(\d+)', line)
                if m:
                    reads, writes, logic = m.group(1), m.group(2), m.group(3)

                if 'PIM test: ALL PASSED' in line:
                    pim_test = 'PASS'
                elif 'PIM test: SOME FAILED' in line:
                    pim_test = 'FAIL'

                if 'Bitwise test: OK' in line:
                    bitwise_test = 'PASS'
                elif 'Bitwise test: NOT OK' in line:
                    bitwise_test = 'FAIL'
    except FileNotFoundError:
        pass

    if not reads:
        status = 'ERROR'
    elif pim_test == 'FAIL' or bitwise_test == 'FAIL':
        status = 'FAIL'
    elif pim_test == '' and bitwise_test == '':
        status = 'COMPILED'
    else:
        status = 'PASS'

    return {
        'reads': reads,
        'writes': writes,
        'logic': logic,
        'status': status,
    }


def parse_target_name(target):
    """Parse 'isa__regs__mode__benchmark' into components."""
    parts = target.split('__')
    if len(parts) != 4:
        return None
    return {
        'isa': parts[0],
        'num_regs': parts[1],
        'mode': parts[2],
        'benchmark': parts[3],
    }


def collect_results(output_root, targets):
    """Collect results for the given list of target names."""
    results = []
    for target in targets:
        info = parse_target_name(target)
        if info is None:
            continue
        log_path = os.path.join(output_root, target, f"{target}.log")
        stats = parse_log(log_path)
        info.update(stats)
        results.append(info)
    return results


def format_table(results):
    """Format results as an aligned text table."""
    header = f"{'ISA':<18} | {'Regs':>4} | {'Mode':<7} | {'Benchmark':<17} | {'#R':>6} | {'#W':>6} | {'#L':>6} | Status"
    sep = '-' * len(header)
    lines = [sep, header, sep]

    for r in results:
        reads = r['reads'] if r['reads'] else '-'
        writes = r['writes'] if r['writes'] else '-'
        logic = r['logic'] if r['logic'] else '-'
        lines.append(
            f"{r['isa']:<18} | {r['num_regs']:>4} | {r['mode']:<7} | {r['benchmark']:<17} | {reads:>6} | {writes:>6} | {logic:>6} | {r['status']}"
        )

    lines.append(sep)
    return '\n'.join(lines)


def print_summary(results):
    """Print a one-line summary of pass/fail counts."""
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    compiled = sum(1 for r in results if r['status'] == 'COMPILED')
    total = len(results)
    parts = [f"{passed}/{total} passed"]
    if failed:
        parts.append(f"{failed} failed")
    if errors:
        parts.append(f"{errors} errors")
    if compiled:
        parts.append(f"{compiled} compile-only")
    print(f"Results: {', '.join(parts)}")


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <output_root> <target1> [target2] ...")
        sys.exit(1)

    output_root = sys.argv[1]
    targets = sys.argv[2:]

    results = collect_results(output_root, targets)
    if not results:
        print("No results found.")
        return

    print(format_table(results))
    print_summary(results)


if __name__ == '__main__':
    main()
