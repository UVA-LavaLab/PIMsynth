#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: input_copy_inserter.py
Description: Inserts copy gates for each input wire to isolate primary inputs from internal logic to avoid the input from getting destructed in analog PIM.
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Date: 2025-05-24
"""

from typing import Dict
from dag_transformer_base import DagTransformer
from blif_dag import GateNode


class InputCopyInserter(DagTransformer):
    """ Inserts copy gates for each input wire to isolate primary inputs from internal logic """

    def __init__(self):
        """ Initialize the InputCopyInserter """
        self.wire_copy_count: Dict[str, int] = {}
        self.new_wires = []

    def is_primary_input(self, wire: str) -> bool:
        """ Check if a wire is a primary input """
        return not wire.startswith("new")

    def rename_input(self, input_str: str) -> str:
        """ Rename input wire to a sanitized version for C variable names """
        return input_str.replace('[', '_').replace(']', '_')

    def apply(self, dag):
        """ Apply the input copy inserter transformation to the DAG """
        for gate_id in list(dag.graph.nodes):
            gate = dag.gate_info[gate_id]
            updated_inputs = []

            for signal in gate.inputs:
                if self.is_primary_input(signal):
                    count = self.wire_copy_count.get(signal, 0)
                    new_signal = f"{self.rename_input(signal)}_copy_{count}"
                    self.wire_copy_count[signal] = count + 1
                    self.new_wires.append(new_signal)

                    copy_gate_id = f"input_copy_{self.rename_input(signal)}_{count}"

                    copy_gate = GateNode(
                        gate_id=copy_gate_id,
                        gate_func="copy",
                        inputs=[signal],
                        outputs=[new_signal]
                    )

                    dag.add_gate(copy_gate)
                    dag.graph.add_edge(copy_gate.gate_id, gate_id)

                    updated_inputs.append(new_signal)
                else:
                    updated_inputs.append(signal)

            gate.inputs = updated_inputs

        # Temp: Track wire list separately for now
        dag.wire_list.extend(self.new_wires)
