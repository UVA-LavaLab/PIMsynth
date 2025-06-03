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
from blif_dag import GateNode


class MajNormalizer(DagTransformer):
    """ Normalizes other gates to majority gates in the DAG """

    def __init__(self):
        """ Initialize """
        pass

    def apply(self, dag):
        """ Apply the majority normalization transformation to the DAG """
        wire_copy_count: Dict[str, int] = {}
        for gate_id in list(dag.graph.nodes):
            gate = dag.gate_info[gate_id]
            if gate.gate_func == "and2":
                # Replace AND gate with a majority gate
                new_wire = f"net_zero_{gate_id}"
                gate.inputs += [new_wire]
                gate.gate_func = "maj3"
                # Add a zero gate
                zero_gate_id = f"zero_{gate_id}"
                zero_gate = GateNode(
                    gate_id=zero_gate_id,
                    gate_func="zero",
                    inputs=[],
                    outputs=[new_wire]
                )
                # Update DAG
                dag.add_gate(zero_gate)
                dag.graph.add_edge(zero_gate.gate_id, gate_id)
            elif gate.gate_func == "or2":
                # Replace OR gate with a majority gate
                new_wire = f"net_one_{gate_id}"
                gate.inputs += [new_wire]
                gate.gate_func = "maj3"
                # Add a one gate
                one_gate_id = f"one_{gate_id}"
                one_gate = GateNode(
                    gate_id=one_gate_id,
                    gate_func="one",
                    inputs=[],
                    outputs=[new_wire]
                )
                # Update DAG
                dag.add_gate(one_gate)
                dag.graph.add_edge(one_gate.gate_id, gate_id)
