#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: run_code_gen.py
Description: Code generation dispatcher.
    Translates PIM IR-2 to backend-specific microprogram files.

    Current backend contract:
        run(ir2_file, hpp_file)
    Input: PIM IR-2 file (post-scheduling, generic rN register names)
    Output: HPP file (PIMeval microprogram)

Author: Deyuan Guo <guodeyuan@gmail.com>
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
"""

import os
import sys

_script_dir = os.path.dirname(os.path.abspath(__file__))

AVAILABLE_BACKENDS = ['pimeval']


def run(ir2_file, hpp_file, backend='pimeval', **_kwargs):
    """Dispatch to the selected code-gen backend."""
    if backend == 'pimeval':
        from pim_ir2_to_pimeval_hpp_translator import translate_ir2_to_hpp
        translate_ir2_to_hpp(ir2_file, hpp_file)
    else:
        raise ValueError(f"Unknown code-gen backend: {backend}. "
                         f"Available: {AVAILABLE_BACKENDS}")


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(
        description='Code generation: .pim_ir2 -> .hpp')
    ap.add_argument('--ir2-file', '-i', required=True,
                    help='Input PIM IR-2 file')
    ap.add_argument('--hpp-file', '-o', required=True,
                    help='Output HPP file')
    ap.add_argument('--backend', default='pimeval',
                    choices=AVAILABLE_BACKENDS,
                    help='Code-gen backend (default: pimeval)')
    args = ap.parse_args()

    # Ensure code-gen modules are importable
    if _script_dir not in sys.path:
        sys.path.insert(0, _script_dir)

    run(ir2_file=args.ir2_file, hpp_file=args.hpp_file,
        backend=args.backend)
