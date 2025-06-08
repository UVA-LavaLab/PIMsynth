#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: dag_fanout_normalizer.py
Description: Eliminates multi-fanout wires by inserting dedicated copy gates for all but one consumer.
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Author: Deyuan Guo <guodeyuan@gmail.com>
Date: 2025-05-08
"""

from typing import Dict, List
from dag_transformer_base import DagTransformer


class FanoutNormalizer(DagTransformer):
    """ FanoutNormalizer class """

    def __init__(self, enable_input_reuse: bool = False):
        """ Initialize the FanoutNormalizer """
        self.copy_count = 0
        self.enable_input_reuse = enable_input_reuse

    def apply(self, dag):
        """ Apply the fanout normalizer transformation to the DAG """
        for wire in dag.get_wire_name_list():
            fanin_gate_ids = dag.get_wire_fanin_gate_ids(wire)
            fanout_gate_ids = dag.get_wire_fanout_gate_ids(wire)
            if len(fanin_gate_ids) != 1:
                raise Exception(f"Error: Wire {wire} has multiple fanin gates: {fanin_gate_ids}. This is unexpected.")
            if len(fanout_gate_ids) <= 1:
                continue

            from_gate_id = fanin_gate_ids[0]
            from_gate = dag.graph.nodes[from_gate_id]
            has_reusable_inputs = from_gate['gate_func'] in ['and2', 'or2', 'maj3']
            to_gate_ids = fanout_gate_ids
            remaining_to_gate_ids = to_gate_ids[1:]
            if has_reusable_inputs:
                if self.enable_input_reuse:
                    remaining_to_gate_ids = self.replace_with_inputs(dag, wire, from_gate_id, remaining_to_gate_ids)
            else:
                raise Exception("Error: Unexpected behaivior happened.")


    def replace_with_inputs(self, dag, target_wire: str, from_gate_id: str, to_gate_ids: List[str]):
        """ Replace fanout inputs with reusable inputs from the previous stage """
        from_gate = dag.get_gate_info(from_gate_id)
        reusable_inputs = []
        for wire in from_gate.inputs:
            # TODO: double check zero, one, and * wires
            if "*" in wire:
                continue  # Skip wires that are already reused
            reusable_inputs.append(wire)

        num_replace = min(len(reusable_inputs), len(to_gate_ids))
        for idx in range(num_replace):
            reuse_wire = reusable_inputs[idx]
            to_gate_id = to_gate_ids[idx]
            to_gate = dag.get_gate_info(to_gate_id)

            # Update DAG
            if not dag.graph.has_edge(from_gate_id, to_gate_id):
                raise Exception(f"Error: Edge from {from_gate_id} to {to_gate_id} does not exist.")
            dag.graph.remove_edge(from_gate_id, to_gate_id)
            from_gate.has_deps = True
            to_gate.has_deps = True

            # Create a dependency edge to maintain topological order
            # The from-gate needs to be done before the to-gate
            dag.graph.add_edge(from_gate_id, to_gate_id, wire_label='dep-reuse')

            # Update gate inputs
            to_gate.inputs = [reuse_wire + "*" if wire == target_wire else wire for wire in to_gate.inputs]

        remaining_to_gate_ids = to_gate_ids[num_replace:]
        return remaining_to_gate_ids

    @staticmethod
    def remove_trailing_stars(wire_list):
        """ Remove trailing stars from a list of strings """
        return [w[:-1] if w.endswith('*') else w for w in wire_list]

    @staticmethod
    def remove_trailing_stars_from_gate_list(dag):
        """ Remove trailing stars from all gate inputs in a gate list """
        for gate in dag.get_gate_list():
            gate.inputs = FanoutNormalizer.remove_trailing_stars(gate.inputs)

