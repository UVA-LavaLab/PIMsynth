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

    def apply(self, dag):
        """ Apply the majority normalization transformation to the DAG """
        for gate_id in dag.get_topo_sorted_gate_id_list():
            gate = dag.graph.nodes[gate_id]
            if gate['gate_func'] == "and2":
                self.run_xform_and_to_maj(dag, gate_id)
            elif gate['gate_func'] == "or2":
                self.run_xform_or_to_maj(dag, gate_id)
        dag.sanity_check()

    def run_xform_and_to_maj(self, dag, gate_id):
        """ Transform: AND gate to MAJ gate """
        orig_gate = dag.graph.nodes[gate_id]
        # Add a zero gate and a wire
        zero_gate_id = dag.uniqufy_gate_id("zero")
        print(f'DAG-Transform: AND to MAJ: {gate_id} -> {zero_gate_id}, {gate_id}')
        new_wire = dag.uniqufy_wire_name("zero")
        dag.add_gate(gate_id=zero_gate_id, gate_func="zero", inputs=[], outputs=[new_wire])
        dag.add_wire(new_wire, zero_gate_id, gate_id)
        # Update the original gate
        orig_gate['gate_func'] = "maj3"
        orig_gate['inputs'].append(new_wire)

    def run_xform_or_to_maj(self, dag, gate_id):
        """ Transform: OR gate to MAJ gate """
        gate = dag.graph.nodes[gate_id]
        # Add a one gate and a wire
        one_gate_id = dag.uniqufy_gate_id("one")
        print(f'DAG-Transform: OR to MAJ: {gate_id} -> {one_gate_id}, {gate_id}')
        new_wire = dag.uniqufy_wire_name("one")
        dag.add_gate(gate_id=one_gate_id, gate_func="one", inputs=[], outputs=[new_wire])
        dag.add_wire(new_wire, one_gate_id, gate_id)
        # Update the original gate
        gate['gate_func'] = "maj3"
        gate['inputs'].append(new_wire)

