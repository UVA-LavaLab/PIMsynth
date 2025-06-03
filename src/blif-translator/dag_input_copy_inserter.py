#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: dag_input_copy_inserter.py
Description: Inserts copy gates for each input wire to isolate primary inputs from internal logic to avoid the input from getting destructed in analog PIM.
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Author: Deyuan Guo <guodeyuan@gmail.com>
Date: 2025-05-24
"""

from typing import Dict
from dag_transformer_base import DagTransformer
from blif_dag import GateNode


class InputCopyInserter(DagTransformer):
    """ Inserts copy gates for each input wire to isolate primary inputs from internal logic """

    def __init__(self):
        """ Initialize the InputCopyInserter """
        pass

    def rename_input(self, input_str: str) -> str:
        """ Sanitize bus wire name """
        return input_str.replace('[', '_').replace(']', '_')

    def apply(self, dag):
        """ Apply the input copy inserter transformation to the DAG """
        wire_copy_count: Dict[str, int] = {}
        for gate_id in list(dag.graph.nodes):
            gate = dag.gate_info[gate_id]
            for i, wire in enumerate(gate.inputs):
                if dag.is_in_port(wire):
                    count = wire_copy_count.get(wire, 0)
                    wire_copy_count[wire] = count + 1
                    new_wire = f"{self.rename_input(wire)}_copy_{count}"
                    copy_gate_id = f"input_copy_{self.rename_input(wire)}_{count}"
                    copy_gate = GateNode(
                        gate_id=copy_gate_id,
                        gate_func="copy",
                        inputs=[wire],
                        outputs=[new_wire]
                    )

                    # Update DAG
                    dag.add_gate(copy_gate)
                    dag.graph.add_edge(copy_gate.gate_id, gate_id)
                    # Update gate inputs
                    gate.inputs[i] = new_wire
