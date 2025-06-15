#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: dag_port_isolation.py
Description: Inserts copy gates for input ports and output ports used as inputs to internal logic
Author: Deyuan Guo <guodeyuan@gmail.com>
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Date: 2025-05-24
"""

from typing import Dict
from dag_transformer_base import DagTransformer


class PortIsolation(DagTransformer):
    """ Inserts copy gates for input ports and output ports """

    def apply(self, dag):
        """ Apply the port isolation transformation to the DAG """
        num_in_copy = 0
        num_out_copy = 0
        for gate_id in dag.get_topo_sorted_gate_id_list():
            if dag.is_in_port(gate_id):
                num_in_copy += self.run_xform_copy_input_port(dag, gate_id)
            elif dag.is_out_port(gate_id):
                num_out_copy += self.run_xform_copy_output_port(dag, gate_id)
        if self.debug_level >= 1:
            print(f'DAG-Transform Summary: Inserted {num_in_copy} and {num_out_copy} copy gates for input and output ports.')

    def sanitize_name(self, input_str: str) -> str:
        """ Sanitize bus port or wire name """
        return input_str.replace('[', '').replace(']', '')

    def run_xform_copy_input_port(self, dag, in_port_gate_id):
        """ Transform: Insert copy gates for an input port """
        orig_gate = dag.graph.nodes[in_port_gate_id]
        if orig_gate['inputs']:
            raise ValueError(f"Input port {in_port_gate_id} should not have inputs: {orig_gate['inputs']}")
        if not orig_gate['outputs']:
            return 0  # no outputs, skip
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

    def run_xform_copy_output_port(self, dag, out_port_gate_id):
        """ Transform: Insert copy gates for an output port if it drives internal logic """
        orig_gate = dag.graph.nodes[out_port_gate_id]
        if orig_gate['outputs']:
            raise ValueError(f"Output port {out_port_gate_id} should not have outputs: {orig_gate['outputs']}")
        if not orig_gate['inputs']:
            return 0  # no inputs, skip
        if len(orig_gate['inputs']) > 1:
            raise ValueError(f"Output port {out_port_gate_id} should not have multiple inputs: {orig_gate['inputs']}")
        orig_wire = orig_gate['inputs'][0]
        fanouts = dag.get_wire_fanout_gate_ids(orig_wire)
        # If the output port wire has only one fanout, no need to insert a copy gate
        if len(fanouts) == 1:
            return 0
        fanins = dag.get_wire_fanin_gate_ids(orig_wire)
        if len(fanins) != 1:
            raise ValueError(f"Output port {out_port_gate_id} should have exactly one fanin: {fanins}")

        # Rename the existing wire to a new name
        fanin_gate_id = fanins[0]
        new_wire = dag.uniqufy_wire_name(f"cp_{self.sanitize_name(out_port_gate_id)}")
        dag.replace_output_wire(fanin_gate_id, orig_wire, new_wire)
        for fanout_gate_id in fanouts:
            dag.graph[fanin_gate_id][fanout_gate_id]['wire_name'] = new_wire
            dag.replace_input_wire(fanout_gate_id, orig_wire, new_wire)

        # Then insert a copy gate to isolate the output port
        copy_gate_id = dag.uniqufy_gate_id(f"cp_{self.sanitize_name(out_port_gate_id)}")
        if self.debug_level >= 2:
            print(f'DAG-Transform: Insert a copy gate {copy_gate_id} for output port {out_port_gate_id} (fanin {fanin_gate_id})')
        dag.add_gate(gate_id=copy_gate_id, gate_func="copy", inputs=[new_wire], outputs=[orig_wire])
        dag.remove_wire(fanin_gate_id, out_port_gate_id)
        dag.add_wire(new_wire, fanin_gate_id, copy_gate_id)
        dag.add_wire(orig_wire, copy_gate_id, out_port_gate_id)
        dag.replace_input_wire(out_port_gate_id, new_wire, orig_wire)

        return 1

