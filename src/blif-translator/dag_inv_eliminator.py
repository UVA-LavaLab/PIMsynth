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

    def is_target_gate(self, dag, gate_id):
        """ Check if a gate is a target for inverter elimination """
        gate = dag.graph.nodes[gate_id]
        return gate['gate_func'] == "inv1"

    def run_xform_inv_elimination(self, dag, inv_gate_id):
        """ Transform: Eliminate an inverter gate and invert fanout gate inputs """
        inv_gate = dag.graph.nodes[inv_gate_id]
        in_wire = inv_gate['inputs'][0]
        out_wire = inv_gate['outputs'][0]

        # Note: Skip inverters that are connected to input or output ports for now
        # It's possible that the input wire is an output port if port isolation is not applied
        if dag.is_in_port(in_wire) or dag.is_out_port(in_wire) or dag.is_out_port(out_wire):
            return 0

        if self.debug_level >= 2:
            print(f'DAG-Transform: Remove INV gate: {inv_gate_id}')

        driver_gate_ids = dag.get_wire_fanin_gate_ids(in_wire)
        assert len(driver_gate_ids) == 1, "Inverter should have exactly one driver gate"
        driver_gate_id = driver_gate_ids[0]
        load_gate_ids = dag.get_wire_fanout_gate_ids(out_wire)

        # Check if any load gate already has in_wire as an input
        # If so, we need to duplicate the driver gate to handle both direct and inverted connections
        loads_with_direct_wire = []
        loads_without_direct_wire = []
        
        for load_gate_id in load_gate_ids:
            if in_wire in dag.graph.nodes[load_gate_id]['inputs']:
                loads_with_direct_wire.append(load_gate_id)
            else:
                loads_without_direct_wire.append(load_gate_id)

        # If some loads already have the direct wire, we need to duplicate the driver
        if loads_with_direct_wire:
            if self.debug_level >= 2:
                print(f'DAG-Transform: Duplicating driver gate {driver_gate_id} for inverted connections')
            
            # Create a copy of the driver gate with a unique ID
            new_driver_id = dag.uniqufy_gate_id(f"{driver_gate_id}_inv_dup")
            driver_gate = dag.graph.nodes[driver_gate_id]
            dag.add_gate(
                gate_id=new_driver_id,
                gate_func=driver_gate['gate_func'],
                inputs=driver_gate['inputs'].copy(),
                outputs=[]  # Will add output wire below
            )
            
            # Copy the inverted set
            dag.graph.nodes[new_driver_id]['inverted'] = driver_gate['inverted'].copy()
            
            # Connect the new driver to the same inputs as the original driver
            for pred_id in dag.graph.predecessors(driver_gate_id):
                wire_name = dag.get_wire_name(pred_id, driver_gate_id)
                dag.add_wire(wire_name, pred_id, new_driver_id)
            
            # Create a new wire from the duplicated driver
            new_wire = dag.uniqufy_wire_name(in_wire)
            dag.graph.nodes[new_driver_id]['outputs'].append(new_wire)
            
            # Remove the inverter gate and wires
            dag.remove_wire(driver_gate_id, inv_gate_id)
            for load_gate_id in load_gate_ids:
                dag.remove_wire(inv_gate_id, load_gate_id)
            dag.remove_gate(inv_gate_id)
            
            # Connect loads that already have the direct wire to the new duplicated driver
            for load_gate_id in loads_with_direct_wire:
                dag.add_wire(new_wire, new_driver_id, load_gate_id)
                dag.replace_input_wire(load_gate_id, out_wire, new_wire)
                dag.invert_input_wire(load_gate_id, new_wire)
            
            # Connect loads that don't have the direct wire to the original driver
            for load_gate_id in loads_without_direct_wire:
                if not dag.graph.has_edge(driver_gate_id, load_gate_id):
                    dag.add_wire(in_wire, driver_gate_id, load_gate_id)
                dag.replace_input_wire(load_gate_id, out_wire, in_wire)
                dag.invert_input_wire(load_gate_id, in_wire)
        else:
            # Standard case: no loads have the direct wire, so we can eliminate normally
            # Remove the inverter gate and wires
            dag.remove_wire(driver_gate_id, inv_gate_id)
            for load_gate_id in load_gate_ids:
                dag.remove_wire(inv_gate_id, load_gate_id)
            dag.remove_gate(inv_gate_id)

            # Reconnect and invert the fanout gate inputs
            for load_gate_id in load_gate_ids:
                # Only add wire if it doesn't already exist
                if not dag.graph.has_edge(driver_gate_id, load_gate_id):
                    dag.add_wire(in_wire, driver_gate_id, load_gate_id)
                dag.replace_input_wire(load_gate_id, out_wire, in_wire)
                dag.invert_input_wire(load_gate_id, in_wire)
        
        return 1

