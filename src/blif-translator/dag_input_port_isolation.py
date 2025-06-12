#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: dag_input_port_isolation.py
Description: Inserts copy gates for each input wire to isolate primary inputs from internal logic to avoid the input from getting destructed in analog PIM.
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Author: Deyuan Guo <guodeyuan@gmail.com>
Date: 2025-05-24
"""

from typing import Dict
from dag_transformer_base import DagTransformer


class InputPortIsolation(DagTransformer):
    """ Inserts copy gates for each input wire to isolate primary inputs from internal logic """

    def apply(self, dag):
        """ Apply the input copy inserter transformation to the DAG """
        total_copy = 0
        for gate_id in dag.get_topo_sorted_gate_id_list():
            if dag.is_in_port(gate_id):
                total_copy += self.run_xform_copy_input_port(dag, gate_id)
        if self.debug_level >= 1:
            print(f'DAG-Transform Summary: Total {total_copy} copy gates inserted for input ports')

    def sanitize_name(self, input_str: str) -> str:
        """ Sanitize bus port or wire name """
        return input_str.replace('[', '').replace(']', '')

    def run_xform_copy_input_port(self, dag, in_port_gate_id):
        """ Transform: Insert copy gates for an input port """
        orig_gate = dag.graph.nodes[in_port_gate_id]
        orig_wire = orig_gate['outputs'][0]
        # Handle all fanouts of the input port
        fanouts = dag.get_wire_fanout_gate_ids(orig_wire)
        for fanout_gate_id in fanouts:
            # Add a new copy gate
            copy_gate_id = dag.uniqufy_gate_id(f"cp_{self.sanitize_name(in_port_gate_id)}")
            if self.debug_level >= 2:
                print(f'DAG-Transform: Copy input port: {in_port_gate_id} -> {copy_gate_id} (fanout {fanout_gate_id})')
            new_wire = dag.uniqufy_wire_name(f"cp_{self.sanitize_name(in_port_gate_id)}")
            dag.add_gate(gate_id=copy_gate_id, gate_func="copy", inputs=[orig_wire], outputs=[new_wire])
            # Update wires
            dag.remove_wire(in_port_gate_id, fanout_gate_id)
            dag.add_wire(orig_wire, in_port_gate_id, copy_gate_id)
            dag.add_wire(new_wire, copy_gate_id, fanout_gate_id)
            dag.replace_input_wire(fanout_gate_id, orig_wire, new_wire)
        return len(fanouts)

