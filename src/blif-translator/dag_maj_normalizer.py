#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: dag_maj_normalizer.py
Description: Normalizes other gates to majority gates in the DAG
Author: Deyuan Guo <guodeyuan@gmail.com>
Date: 2025-06-03
"""

from typing import Dict
from dag_transformer_base import DagTransformer


class MajNormalizer(DagTransformer):
    """ Normalizes other gates to majority gates in the DAG """

    def __init__(self):
        """ Initialize """
        self.solution = 0  # 0: separate zero/one gates; 1: single zero/one gate

    def apply(self, dag):
        """ Apply the majority normalization transformation to the DAG """
        total_and = 0
        total_or = 0
        for gate_id in dag.get_topo_sorted_gate_id_list():
            gate = dag.graph.nodes[gate_id]
            if gate['gate_func'] == "and2":
                total_and += self.run_xform_and_to_maj(dag, gate_id)
            elif gate['gate_func'] == "or2":
                total_or += self.run_xform_or_to_maj(dag, gate_id)
        if self.debug_level >= 1:
            print(f'DAG-Transform Summary: Total {total_and} AND gates and {total_or} OR gates transformed to MAJ gates')

    def run_xform_and_to_maj(self, dag, gate_id):
        """ Transform: AND gate to MAJ gate """
        orig_gate = dag.graph.nodes[gate_id]
        # Add a zero gate and a wire
        if self.solution == 0:
            zero_gate_id = dag.uniqufy_gate_id("zero")
            zero_wire = dag.uniqufy_wire_name("zero")
            dag.add_gate(gate_id=zero_gate_id, gate_func="zero", inputs=[], outputs=[zero_wire])
            dag.add_wire(zero_wire, zero_gate_id, gate_id)
        elif self.solution == 1:
            zero_gate_id = "zero"
            zero_wire = "zero"
            if not dag.graph.has_node(zero_gate_id):
                dag.add_gate(gate_id=zero_gate_id, gate_func="zero", inputs=[], outputs=[zero_wire])
            dag.add_wire(zero_wire, zero_gate_id, gate_id)
        else:
            raise ValueError("Invalid solution option for zero gate creation")
        if self.debug_level >= 2:
            print(f'DAG-Transform: AND to MAJ: {gate_id} -> {zero_gate_id}, {gate_id}')
        # Update the original gate
        orig_gate['gate_func'] = "maj3"
        orig_gate['inputs'].append(zero_wire)
        return 1

    def run_xform_or_to_maj(self, dag, gate_id):
        """ Transform: OR gate to MAJ gate """
        gate = dag.graph.nodes[gate_id]
        # Add a one gate and a wire
        if self.solution == 0:
            one_gate_id = dag.uniqufy_gate_id("one")
            one_wire = dag.uniqufy_wire_name("one")
            dag.add_gate(gate_id=one_gate_id, gate_func="one", inputs=[], outputs=[one_wire])
            dag.add_wire(one_wire, one_gate_id, gate_id)
        elif self.solution == 1:
            one_gate_id = "one"
            one_wire = "one"
            if not dag.graph.has_node(one_gate_id):
                dag.add_gate(gate_id=one_gate_id, gate_func="one", inputs=[], outputs=[one_wire])
            dag.add_wire(one_wire, one_gate_id, gate_id)
        else:
            raise ValueError("Invalid solution option for one gate creation")
        if self.debug_level >= 2:
            print(f'DAG-Transform: OR to MAJ: {gate_id} -> {one_gate_id}, {gate_id}')
        # Update the original gate
        gate['gate_func'] = "maj3"
        gate['inputs'].append(one_wire)
        return 1

