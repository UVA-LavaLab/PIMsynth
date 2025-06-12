#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: dag_wire_copy_inserter.py
Description: Copy a wire if it drives more than one input-destroying gates for analog PIM.
Author: Deyuan Guo <guodeyuan@gmail.com>
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Date: 2025-06-05
"""

from typing import Dict, List
from dag_transformer_base import DagTransformer
from collections import deque


class WireCopyInserter(DagTransformer):
    """ FanoutNormalizer class """

    def apply(self, dag):
        """ Apply the wire copy insertion transformation to the DAG """
        total_copy = 0
        wire_queue = deque(dag.get_wire_name_list(merge_segments=False))
        while wire_queue:
            wire = wire_queue.popleft()
            if self.is_target_wire(dag, wire):
                new_wire = self.run_xform_copy_wire(dag, wire)
                total_copy += 1
                wire_queue.appendleft(new_wire)
        if self.debug_level >= 1:
            print(f'DAG-Transform Summary: Total {total_copy} wire copies inserted for input-destroying gates')

    def is_target_wire(self, dag, wire):
        """ Check if the wire is a target for wire copy insertion """
        fanin_gate_ids = dag.get_wire_fanin_gate_ids(wire)
        fanout_gate_ids = dag.get_wire_fanout_gate_ids(wire)
        # Valid case 1: One input-destroying gate with other regular gates
        # Valid case 2: More than one input-destroying gates
        if len(fanin_gate_ids) != 1 or len(fanout_gate_ids) <= 1:
            return False
        anchor_gate_id, rest_gate_ids = self.find_first_input_destroying_gate(dag, fanout_gate_ids)
        return anchor_gate_id is not None and len(rest_gate_ids) > 0

    def find_first_input_destroying_gate(self, dag, fanout_gate_ids):
        """ Find input-destroying gates in the given gate ID list """
        anchor_gate_id = None
        rest_gate_ids = fanout_gate_ids.copy()
        for gate_id in fanout_gate_ids:
            gate = dag.graph.nodes[gate_id]
            if gate['gate_func'] in ['and2', 'or2', 'maj3']:
                anchor_gate_id = gate_id
                rest_gate_ids.remove(gate_id)
                break
        return anchor_gate_id, rest_gate_ids

    def run_xform_copy_wire(self, dag, target_wire):
        """ Transform: Copy a wire for handling input-destroying gates """
        fanin_gate_ids = dag.get_wire_fanin_gate_ids(target_wire)
        fanout_gate_ids = dag.get_wire_fanout_gate_ids(target_wire)
        fanin_gate_id = fanin_gate_ids[0]
        anchor_gate_id, rest_gate_ids = self.find_first_input_destroying_gate(dag, fanout_gate_ids)
        assert anchor_gate_id is not None
        assert rest_gate_ids

        # Create a copy gate
        copy_gate_id = dag.uniqufy_gate_id("copy_inout")
        new_wire = dag.uniqufy_wire_name("copy_inout")
        if self.debug_level >= 2:
            print(f'DAG-Transform: Copy wire: {target_wire} -> {copy_gate_id} (for {anchor_gate_id})')
        dag.add_gate(gate_id=copy_gate_id, gate_func="copy_inout", inputs=[target_wire], outputs=[new_wire])

        # Move the rest gates under the copy gate
        dag.add_wire(target_wire, fanin_gate_id, copy_gate_id)
        for fanout_gate_id in rest_gate_ids:
            dag.remove_wire(fanin_gate_id, fanout_gate_id)
            dag.add_wire(new_wire, copy_gate_id, fanout_gate_id)
            dag.replace_input_wire(fanout_gate_id, target_wire, new_wire)

        # Handle implicit dependency
        # The copy_inout gate needs to be done before the anchor gate
        # This is done by:
        # 1. Let the new copy gate drive the anchor gate (new wire segment)
        # 2. Use '+r' in ineline assembly IR so that LLVM knows the dependency
        target_wire_segment = dag.uniqufy_wire_name(f"{target_wire} seg")
        dag.remove_wire(fanin_gate_id, anchor_gate_id)
        dag.add_wire(target_wire_segment, copy_gate_id, anchor_gate_id)
        dag.replace_input_wire(anchor_gate_id, target_wire, target_wire_segment)

        # For recursive processing
        return new_wire

