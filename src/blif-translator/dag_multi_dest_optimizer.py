#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: dag_multi_dest_optimizer.py
Description: Apply multi-destination of Triple-Row Activation (TRA) to the DAG.
Author: Deyuan Guo <guodeyuan@gmail.com>
Date: 2025-06-10
"""

from typing import Dict, List
from dag_transformer_base import DagTransformer


class MultiDestOptimizer(DagTransformer):
    """ MultiDestOptimizer class """

    def __init__(self, num_regs):
        """ Initialize """
        self.num_regs = num_regs  # Determine the max number of packing
        self.max_outputs = 3  # Max number of outputs for AAP

    def apply(self, dag):
        """ Apply the multi-destination optimization to the DAG """
        total_packed = 0
        for gate_id in dag.get_topo_sorted_gate_id_list():
            if self.is_target_gate(dag, gate_id):
                total_packed += self.run_xform_multi_dest_opt(dag, gate_id)
        if self.debug_level >= 1:
            print(f'DAG-Transform Summary: Packed {total_packed} wires using multi-destination optimization')

    def is_target_gate(self, dag, gate_id):
        """ Check if the gate is a target for inout variable reuse """
        gate = dag.graph.nodes[gate_id]
        return gate['gate_func'] in ['maj3']

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

    def run_xform_multi_dest_opt(self, dag, driver_gate_id):
        """ Transform: Apply multi-destination optimization to the gate """
        driver_gate = dag.graph.nodes[driver_gate_id]
        if self.debug_level >= 2:
            print(f'DAG-Transform: Reuse inout variables of gate {driver_gate_id} ({driver_gate["gate_func"]})')

        output_wires = driver_gate['outputs']
        if len(output_wires) >= 3 or len(output_wires) == 0:
            return 0
        num_slots = min(self.max_outputs - len(output_wires), self.num_regs - 3 - 1) # ensure enough registers for scheduling
        pack_count = 0
        for target_wire in output_wires:
            while pack_count < num_slots:
                output_gate_ids = dag.get_wire_fanout_gate_ids(target_wire)
                if len(output_gate_ids) <= 1:
                    break
                target_gate_id, rest_gate_ids = self.find_first_input_destroying_gate(dag, output_gate_ids)
                if target_gate_id is None or len(rest_gate_ids) == 0:
                    break
                if self.debug_level >= 2:
                    print(f'DAG-Transform: Creating new output wire for gate {target_gate_id} (from {driver_gate_id})')

                # Update wires
                dag.remove_wire(driver_gate_id, target_gate_id)
                new_wire = dag.uniqufy_wire_name(f"{target_wire}_dup")
                dag.add_wire(new_wire, driver_gate_id, target_gate_id)
                dag.graph.nodes[driver_gate_id]['outputs'].append(new_wire)
                dag.replace_input_wire(target_gate_id, target_wire, new_wire)
                pack_count += 1

        return pack_count

