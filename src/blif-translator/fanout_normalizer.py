#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: fanout_normalizer.py
Description: Eliminates multi-fanout wires by inserting dedicated copy gates for all but one consumer.
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Author: Deyuan Guo <guodeyuan@gmail.com>
Date: 2025-05-08
"""

from typing import Dict, List
from dag_transformer_base import DagTransformer
from blif_parser import GateNode


class FanoutNormalizer(DagTransformer):
    """ FanoutNormalizer class """

    def __init__(self):
        """ Initialize the FanoutNormalizer """
        self.copy_count = 0

    def apply(self, dag):
        """ Apply the fanout normalizer transformation to the DAG """
        wire_fanouts: Dict[str, List[str]] = self.get_wire_fanouts(dag)
        wire_fanin: Dict[str, str] = self.get_wire_fanin(dag)

        for wire, to_gate_ids in wire_fanouts.items():
            fanout = len(to_gate_ids)
            if fanout <= 1:
                continue

            from_gate_id = wire_fanin.get(wire)
            if from_gate_id is None:
                continue

            from_gate = dag.gate_info[from_gate_id]
            is_inv_gate = from_gate.gate_func == "inv1"
            is_copy_gate = from_gate.gate_func == "copy"
            has_reusable_inputs = not (is_inv_gate or is_copy_gate)
            first_to_gate_id = to_gate_ids[0]
            remaining_to_gate_ids = to_gate_ids[1:]
            if has_reusable_inputs:
                remaining_to_gate_ids = self.replace_with_inputs(dag, wire, from_gate_id, remaining_to_gate_ids)
                self.insert_copy_nodes(dag, wire, from_gate_id, remaining_to_gate_ids, first_to_gate_id)
            elif is_inv_gate:
                self.insert_copy_nodes(dag, wire, from_gate_id, remaining_to_gate_ids, first_to_gate_id)
            else:
                raise Exception("Error: Unexpected behaivior happened.")


    def replace_with_inputs(self, dag, target_wire: str, from_gate_id: str, to_gate_ids: List[str]):
        """ Replace fanout inputs with reusable inputs from the previous stage """
        from_gate = dag.gate_info[from_gate_id]
        reusable_inputs = []
        for wire in from_gate.inputs:
            if not "*" in wire:
                reusable_inputs.append(wire)

        num_replace = min(len(reusable_inputs), len(to_gate_ids))
        for idx in range(num_replace):
            reuse_wire = reusable_inputs[idx]
            to_gate_id = to_gate_ids[idx]
            to_gate = dag.gate_info[to_gate_id]

            # Update DAG
            if not dag.graph.has_edge(from_gate_id, to_gate_id):
                raise Exception(f"Error: Edge from {from_gate_id} to {to_gate_id} does not exist.")
            dag.graph.remove_edge(from_gate_id, to_gate_id)
            from_gate.has_deps = True
            to_gate.has_deps = True

            # Create a dependency edge to maintain topological order
            # The from-gate needs to be done before the to-gate
            dag.graph.add_edge(from_gate_id, to_gate_id, label='dep')

            # Update gate inputs
            to_gate.inputs = [reuse_wire + "*" if wire == target_wire else wire for wire in to_gate.inputs]

        remaining_to_gate_ids = to_gate_ids[num_replace:]
        return remaining_to_gate_ids

    def get_wire_fanouts(self, dag) -> Dict[str, List[str]]:
        """ Get the fanouts for each wire in the DAG """
        wire_fanouts: Dict[str, List[str]] = {}
        for gate_id in dag.graph.nodes:
            gate = dag.gate_info[gate_id]
            for wire in gate.inputs:
                wire_fanouts.setdefault(wire, []).append(gate_id)
        return wire_fanouts

    def get_wire_fanin(self, dag) -> Dict[str, str]:
        """ Get the fanin for each wire in the DAG """
        wire_fanin: Dict[str, str] = {}
        for gate_id in dag.graph.nodes:
            gate = dag.gate_info[gate_id]
            for wire in gate.outputs:
                wire_fanin[wire] = gate_id
        return wire_fanin

    def insert_copy_nodes(self, dag, target_wire: str, orig_from_gate_id: str, to_gate_ids: List[str], first_to_gate_id: str):
        """ Insert copy nodes to handle input-destroying gates """
        prev_wire = target_wire
        prev_from_gate_id = orig_from_gate_id
        prev_to_gate_id = first_to_gate_id
        orig_from_gate = dag.gate_info[orig_from_gate_id]

        for to_gate_id in to_gate_ids:
            new_wire = f"{target_wire}_copy_{self.copy_count}"
            copy_gate_id = f"copy_{self.copy_count}"
            copy_gate = GateNode(
                gate_id=copy_gate_id,
                gate_func="copy",
                inputs=[prev_wire],
                outputs=[new_wire]
            )
            self.copy_count += 1

            # Update DAG
            if not dag.graph.has_edge(orig_from_gate_id, to_gate_id):
                raise Exception(f"Error: Edge from {orig_from_gate_id} to {to_gate_id} does not exist.")
            dag.graph.remove_edge(orig_from_gate_id, to_gate_id)
            orig_from_gate.has_deps = True
            copy_gate.has_deps = True

            dag.add_gate(copy_gate)
            dag.graph.add_edge(prev_from_gate_id, copy_gate_id)
            dag.graph.add_edge(copy_gate_id, to_gate_id)

            # Create a dependency edge to maintain topological order
            # The copy needs to be done before the previous to-gate
            dag.graph.add_edge(copy_gate_id, prev_to_gate_id, label='dep')

            # Update gate inputs
            to_gate = dag.gate_info[to_gate_id]
            to_gate.inputs = [new_wire if wire == target_wire else wire for wire in to_gate.inputs]

            prev_wire = new_wire
            prev_from_gate_id = copy_gate_id
            prev_to_gate_id = to_gate_id


    @staticmethod
    def remove_trailing_stars(wire_list):
        """ Remove trailing stars from a list of strings """
        return [w[:-1] if w.endswith('*') else w for w in wire_list]

    @staticmethod
    def remove_trailing_stars_from_gate_list(dag):
        """ Remove trailing stars from all gate inputs in a gate list """
        for gate in dag.get_gate_list():
            gate.inputs = FanoutNormalizer.remove_trailing_stars(gate.inputs)
