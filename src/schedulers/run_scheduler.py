#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: run_scheduler.py
Description: Common scheduler dispatcher.
    Selects and delegates to the appropriate scheduler implementation.

    Scheduler contract (target interface):
        run(ir1_file, ir2_file, module_name, num_regs, pim_mode, **kwargs)
    Input: IR-1 file (pre-scheduling)
    Output: IR-2 file (post-scheduling)

Author: Deyuan Guo <guodeyuan@gmail.com>
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
"""

import importlib.util
import os
import sys

_script_dir = os.path.dirname(os.path.abspath(__file__))

AVAILABLE_SCHEDULERS = ['llvm-riscv']

_scheduler_cache = {}


def _get_llvm_riscv_scheduler():
    """Lazy import of the llvm-riscv scheduler module."""
    if 'llvm-riscv' not in _scheduler_cache:
        mod_path = os.path.join(_script_dir, 'llvm-riscv', 'run_scheduler.py')
        spec = importlib.util.spec_from_file_location('llvm_riscv_scheduler', mod_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _scheduler_cache['llvm-riscv'] = mod
    return _scheduler_cache['llvm-riscv']


def run(scheduler_name, **kwargs):
    """Dispatch to the selected scheduler."""
    if scheduler_name == 'llvm-riscv':
        scheduler = _get_llvm_riscv_scheduler()
        scheduler.run(**kwargs)
    else:
        raise ValueError(f"Unknown scheduler: {scheduler_name}. "
                         f"Available: {AVAILABLE_SCHEDULERS}")
