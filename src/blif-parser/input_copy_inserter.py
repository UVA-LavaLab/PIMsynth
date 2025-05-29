#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: input_copy_inserter.py
Description: Inserts copy gates for each input wire to isolate primary inputs from internal logic to avoid the input from getting destructed in analog PIM.
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Date: 2025-05-24
"""

from parser import *
from typing import Dict
from dag_transformer_base import DagTransformer
import networkx as nx

class InputCopyInserter(DagTransformer):
    def __init__(self):
        self.wireCopyCounter: Dict[str, int] = {}
        self.newWires = []

    def isPrimaryInput(self, signal: str) -> bool:
        return not signal.startswith("new")

    def renameInput(self, inputStr: str) -> str:
        return inputStr.replace('[', '_').replace(']', '_')

    def apply(self, dag):
        for gateId in list(dag.graph.nodes):
            gate = dag.gateInfo[gateId]
            updatedInputs = []

            for signal in gate.inputs:
                if self.isPrimaryInput(signal):
                    count = self.wireCopyCounter.get(signal, 0)
                    newSignal = f"{self.renameInput(signal)}_copy_{count}"
                    self.wireCopyCounter[signal] = count + 1
                    self.newWires.append(newSignal)

                    copyGateId = f"input_copy_{self.renameInput(signal)}_{count}"

                    copyGate = GateNode(
                        gateId=copyGateId,
                        gateType="copy",
                        inputs=[signal],
                        outputs=[newSignal]
                    )

                    dag.addGate(copyGate)
                    dag.graph.add_edge(copyGate.id, gateId)

                    updatedInputs.append(newSignal)
                else:
                    updatedInputs.append(signal)

            gate.inputs = updatedInputs

        return dag

