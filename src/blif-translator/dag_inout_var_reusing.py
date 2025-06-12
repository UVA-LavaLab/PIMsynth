#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: dag_inout_var_reusing.py
Description: Reuse previous stage TRA inputs (inout) to reduce copies.
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Author: Deyuan Guo <guodeyuan@gmail.com>
Date: 2025-05-08
"""

from typing import Dict, List
from dag_transformer_base import DagTransformer


class InoutVarReusing(DagTransformer):
    """ InoutVarReusing class """

    def apply(self, dag):
        """ Apply the variable reuse transformation to the DAG """
        total_reuse = 0
        for gate_id in dag.get_topo_sorted_gate_id_list():
            if self.is_target_gate(dag, gate_id):
                total_reuse += self.run_xform_inout_var_reusing(dag, gate_id)
        if self.debug_level >= 1:
            print(f'DAG-Transform Summary: Reuse {total_reuse} inout wires')

    def is_target_gate(self, dag, gate_id):
        """ Check if the gate is a target for inout variable reuse """
        gate = dag.graph.nodes[gate_id]
        return gate['gate_func'] in ['and2', 'or2', 'maj3']

    def find_first_input_destroying_gate(self, dag, fanout_gate_ids):
        """ Find input-destroying gates in the given gate ID list """
        target_gate_id = None
        rest_gate_ids = fanout_gate_ids.copy()
        for gate_id in fanout_gate_ids:
            gate = dag.graph.nodes[gate_id]
            if gate['gate_func'] in ['and2', 'or2', 'maj3']:
                target_gate_id = gate_id
                rest_gate_ids.remove(gate_id)
                break
        return target_gate_id, rest_gate_ids

    def run_xform_inout_var_reusing(self, dag, gate_id):
        """ Transform: Reuse inout variables from the previous stage """
        gate = dag.graph.nodes[gate_id]
        if self.debug_level >= 2:
            print(f'DAG-Transform: Reuse inout variables of gate {gate_id} ({gate["gate_func"]})')

        # Check if the gate has reusable inputs
        reusable_inout_wires = dag.get_reusable_inout_wires(gate_id)
        if not reusable_inout_wires:
            return 0

        output_wires = gate['outputs']
        reuse_count = 0
        for output_wire in output_wires:
            output_gate_ids = dag.get_wire_fanout_gate_ids(output_wire)
            if len(output_gate_ids) <= 1:
                continue
            target_gate_id, rest_gate_ids = self.find_first_input_destroying_gate(dag, output_gate_ids)
            while target_gate_id is not None and reusable_inout_wires:
                if self.debug_level >= 2:
                    print(f'DAG-Transform: Reusing inout wire {reusable_inout_wires[0]} for gate {target_gate_id} (from {gate_id})')
                dag.remove_wire(gate_id, target_gate_id)
                new_wire = dag.uniqufy_wire_name(f"{reusable_inout_wires[0]} seg")
                dag.add_wire(new_wire, gate_id, target_gate_id)
                dag.replace_input_wire(target_gate_id, output_wire, new_wire)
                # If the reused input is inverted, need to invert the new wire as well
                is_inv = reusable_inout_wires[0] in dag.graph.nodes[gate_id]['inverted']
                if is_inv:
                    dag.invert_input_wire(target_gate_id, new_wire)
                reusable_inout_wires.pop(0)
                reuse_count += 1
                if len(rest_gate_ids) <= 1:
                    break
                target_gate_id, rest_gate_ids = self.find_first_input_destroying_gate(dag, rest_gate_ids)
                #print(dag)
        return reuse_count

