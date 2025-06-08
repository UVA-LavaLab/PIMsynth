#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: dag_inv_eliminator.py
Description: Eliniminates inverters in the DAG
Author: Deyuan Guo <guodeyuan@gmail.com>
Date: 2025-06-04
"""

from dag_transformer_base import DagTransformer


class InvEliminator(DagTransformer):
    """ Eliminates inverters in the DAG for analog PIM with dual-contact cells (DCC) capability """

    def apply(self, dag):
        """ Apply inverter elimination in the DAG """
        total_inv = 0
        for gate_id in dag.get_topo_sorted_gate_id_list():
            if self.is_target_gate(dag, gate_id):
                total_inv += self.run_xform_inv_elimination(dag, gate_id)
        if self.debug_level >= 1:
            print(f'DAG-Transform Summary: Total {total_inv} inverter gates eliminated')
        dag.sanity_check()

    def is_target_gate(self, dag, gate_id):
        """ Check if a gate is a target for inverter elimination """
        gate = dag.graph.nodes[gate_id]
        return gate['gate_func'] == "inv1"

    def run_xform_inv_elimination(self, dag, inv_gate_id):
        """ Transform: Eliminate an inverter gate and negate the edges """
        if self.debug_level >= 2:
            print(f'DAG-Transform: Remove INV gate: {inv_gate_id}')
        inv_gate = dag.graph.nodes[inv_gate_id]
        in_wire = inv_gate['inputs'][0]
        out_wire = inv_gate['outputs'][0]

        # Note: Skip inverters that are connected to input or output ports for now
        if dag.is_in_port(in_wire) or dag.is_out_port(out_wire):
            return 0

        driver_gate_ids = dag.get_wire_fanin_gate_ids(in_wire)
        assert len(driver_gate_ids) == 1, "Inverter should have exactly one driver gate"
        driver_gate_id = driver_gate_ids[0]
        load_gate_ids = dag.get_wire_fanout_gate_ids(out_wire)

        # Handle negation of wires
        # If the in wire is negated, keep all out wires as is after inverter elimination
        # If the in wire is not negated, negate all out wires after inverter elimination
        is_in_wire_negated = dag.is_wire_negated(driver_gate_id, inv_gate_id)
        is_out_wire_negated = []
        for load_gate_id in load_gate_ids:
            is_negated = dag.is_wire_negated(inv_gate_id, load_gate_id)
            if not is_in_wire_negated:
                is_negated = not is_negated
            is_out_wire_negated.append(is_negated)

        # Remove the inverter and update wires in DAG
        dag.remove_wire(driver_gate_id, inv_gate_id)
        for load_gate_id in load_gate_ids:
            dag.remove_wire(inv_gate_id, load_gate_id)
        dag.remove_gate(inv_gate_id)
        for load_gate_id, is_negated in zip(load_gate_ids, is_out_wire_negated):
            dag.add_wire(in_wire, driver_gate_id, load_gate_id)
            dag.set_wire_negated(driver_gate_id, load_gate_id, is_negated)
            dag.replace_input_wire(load_gate_id, out_wire, in_wire)
        return 1

