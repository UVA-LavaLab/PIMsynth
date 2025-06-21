#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: blif_dag.py
Description: DAG representation for BLIF translator
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Author: Deyaun Guo <guodeyuan@gmail.com>
Date: 2025-05-28
"""

import json
import copy
from collections import defaultdict, deque
from networkx.readwrite import json_graph
from pyvis.network import Network
import networkx as nx
from blif_dag_verification import DagVerifier


class DAG:
    """ Directed Acyclic Graph (DAG) representation of a circuit """

    def __init__(self, module_name='', in_ports=None, out_ports=None, gate_info_list=None, pim_mode='digital', debug_level=0):
        """
        DAG description:
        * Node
            - Represents a gate or an input/output port in the circuit
            - Attributes:
                - gate_id: Unique string identifier for the gate
                - gate_func: Function of the gate (e.g., inv1, and2, maj3, copy, in_port, out_port)
                - inputs: List of input wires with order preserved
                - outputs: List of output wires with order preserved
                - inverted: Set of input/output wires that are inverted
            - APIs:
                - graph.add_node(gate_id): Add a gate node to the DAG
                - graph.nodes[gate_id]: Access gate information dictionary by gate ID
        * Edge
            - Represents a wire in the circuit
                - A wire may have multiple segaments because of in-out behavior of analog PIM
            - Attributes:
                - wire_name: Name of the wire
            - APIs:
                - graph.add_edge(fanin_gate_id, gate_id): Add an edge from fanin gate to gate
                - graph[fanin_gate_id][gate_id]: Access edge information dictionary by fanin and fanout gate IDs
        * Input parameters:
            - module_name: Name of the module
            - in_ports: List of input ports. Each port has a gate and a wire of the same name
            - out_ports: List of output ports. Each port has a gate and a wire of the same name
            - gate_info_list: List of gate info from BlifParser to initialize the DAG
        """
        self.graph = nx.DiGraph()
        self.module_name = module_name
        self.__in_ports = []  # To preserve order of input ports
        self.__out_ports = []  # To preserve order of output ports
        self.pim_mode = pim_mode
        self.debug_level = debug_level
        self.wire_segment_marker = '_$'
        self.topo_sort_algorithm = 1
        self.initialize(in_ports, out_ports, gate_info_list)
        self.verifier = DagVerifier(dag=self, debug_level=debug_level)

    def raise_exception(self, message):
        """ Helper function to raise an exception with a message """
        # Enable breakpoint for debugging
        if self.debug_level >= 1:
            print(f"DEBUG: {message}")
            breakpoint()
        raise ValueError(message)

    def __deepcopy__(self, memo):
        """ Create a deep copy of the DAG """
        new_dag = DAG(module_name=self.module_name,
                      in_ports=[], out_ports=[], gate_info_list=[],
                      debug_level=self.debug_level)
        new_dag.graph = copy.deepcopy(self.graph, memo)
        new_dag.__in_ports = self.get_in_ports()
        new_dag.__out_ports = self.get_out_ports()
        return new_dag

    def initialize(self, in_ports, out_ports, gate_info_list):
        """ Initialize DAG nodes and edges """
        if in_ports is None or out_ports is None or gate_info_list is None:
            self.raise_exception("Input ports, output ports, and gate info list cannot be None.")
        # Add input ports
        self.__in_ports = in_ports.copy()
        for port in self.__in_ports:
            self.add_gate(gate_id=port, gate_func='in_port')
        # Add output ports
        self.__out_ports = out_ports.copy()
        for port in self.__out_ports:
            self.add_gate(gate_id=port, gate_func='out_port')
        # Add gates
        for gate_info in gate_info_list:
            gate_id = gate_info.gate_id
            gate_func = gate_info.gate_func
            gate_inputs = gate_info.inputs
            gate_outputs = gate_info.outputs
            self.add_gate(gate_id=gate_id, gate_func=gate_func, inputs=gate_inputs, outputs=gate_outputs)
        # Connect wires
        wire_fanins = defaultdict(set)
        wire_fanouts = defaultdict(set)
        for gate_info in gate_info_list:
            gate_id = gate_info.gate_id
            gate_inputs = gate_info.inputs
            gate_outputs = gate_info.outputs
            for wire in gate_inputs:
                wire_fanouts[wire].add(gate_id)
            for wire in gate_outputs:
                wire_fanins[wire].add(gate_id)
        for wire in set(wire_fanins.keys()).union(wire_fanouts.keys()):
            fanins = wire_fanins.get(wire, [])
            fanouts = wire_fanouts.get(wire, [])
            #if not fanins and not fanouts:
            #    self.raise_exception(f"Wire '{wire}' has no fanins and fanouts")
            if not fanins:
                if not fanouts:
                    self.raise_exception(f"Wire '{wire}' has no fanins and fanouts")
                if wire not in self.__in_ports:
                    self.raise_exception(f"Wire '{wire}' has no fanins and is not an input port.")
                fanin_gate_id = wire
                self.graph.nodes[fanin_gate_id]['outputs'].append(wire)
                for gate_id in fanouts:
                    self.add_wire(wire_name=wire, fanin_gate_id=fanin_gate_id, fanout_gate_id=gate_id)
            else:
                if len(fanins) != 1:
                    self.raise_exception(f"Wire '{wire}' has multiple fanins: {fanins}. Expected a single fanin.")
                fanin_gate_id = next(iter(fanins))
                # Special case: If wire is with an output port name, connect it to the port gate first
                # It is legal to use such wire as inputs of internal logic, so it can have multiple fanouts
                if wire in self.__out_ports:
                    fanout_gate_id = wire
                    self.graph.nodes[fanout_gate_id]['inputs'].append(wire)
                    self.add_wire(wire_name=wire, fanin_gate_id=fanin_gate_id, fanout_gate_id=fanout_gate_id)
                # Connect regular fanouts
                for fanout_gate_id in fanouts:
                    self.add_wire(wire_name=wire, fanin_gate_id=fanin_gate_id, fanout_gate_id=fanout_gate_id)

    def add_gate(self, gate_id='', gate_func='', inputs=None, outputs=None):
        """ Add a gate to the DAG """
        if gate_id in self.graph:
            self.raise_exception(f"Gate ID '{gate_id}' already exists in the DAG.")
        if inputs is None:
            inputs = []
        if outputs is None:
            outputs = []
        self.graph.add_node(gate_id,
                            gate_id=gate_id,
                            gate_func=gate_func,
                            inputs=inputs.copy(),
                            outputs=outputs.copy(),
                            inverted=set())
        if self.debug_level >= 4:
            print(f"INFO: Added gate '{gate_id}' with function '{gate_func}' | Inputs: {inputs} | Outputs: {outputs}")

    def remove_gate(self, gate_id):
        """ Remove a gate from the DAG """
        if not self.graph.has_node(gate_id):
            self.raise_exception(f"Gate ID '{gate_id}' does not exist in the DAG.")
        if self.graph.in_degree(gate_id) > 0 or self.graph.out_degree(gate_id) > 0:
            for u, v, edge_data in self.graph.in_edges(gate_id, data=True):
                print(f'Edge: {u} -> {v} | Attr: {edge_data}')
            for u, v, edge_data in self.graph.out_edges(gate_id, data=True):
                print(f'Edge: {u} -> {v} | Attr: {edge_data}')
            self.raise_exception(f"Cannot remove gate '{gate_id}': it has connected wires.")
        self.graph.remove_node(gate_id)
        if self.debug_level >= 4:
            print(f"INFO: Removed gate '{gate_id}' from the DAG")

    def add_wire(self, wire_name, fanin_gate_id, fanout_gate_id):
        """ Add a wire to the DAG """
        if not self.graph.has_node(fanin_gate_id) or not self.graph.has_node(fanout_gate_id):
            self.raise_exception(f"Cannot add wire '{wire_name}': fanin or fanout gate does not exist.")
        if self.graph.has_edge(fanin_gate_id, fanout_gate_id):
            self.raise_exception(f"Wire '{wire_name}' already exists between {fanin_gate_id} and {fanout_gate_id}.")
        self.graph.add_edge(fanin_gate_id, fanout_gate_id, wire_name=wire_name)
        if self.debug_level >= 4:
            print(f"INFO: Added wire '{wire_name}' from {fanin_gate_id} to {fanout_gate_id}")

    def remove_wire(self, fanin_gate_id, fanout_gate_id):
        """ Remove a wire (single edge only) from the DAG """
        if not self.graph.has_edge(fanin_gate_id, fanout_gate_id):
            self.raise_exception(f"Wire does not exist between {fanin_gate_id} and {fanout_gate_id}.")
        wire_name = self.graph[fanin_gate_id][fanout_gate_id]['wire_name']
        self.graph.remove_edge(fanin_gate_id, fanout_gate_id)
        if self.debug_level >= 4:
            print(f"INFO: Removed wire '{wire_name}' from {fanin_gate_id} to {fanout_gate_id}")

    def replace_output_wire(self, gate_id, old_wire_name, new_wire_name):
        """ Replace an output wire of a gate with a new wire name """
        if not self.graph.has_node(gate_id):
            self.raise_exception(f"Gate ID '{gate_id}' does not exist in the DAG.")
        if old_wire_name not in self.graph.nodes[gate_id]['outputs']:
            self.raise_exception(f"Old wire '{old_wire_name}' is not an output of gate '{gate_id}'.")
        if new_wire_name in self.graph.nodes[gate_id]['outputs']:
            self.raise_exception(f"New wire '{new_wire_name}' already exists as an output of gate '{gate_id}'.")

        # Update outputs
        outputs = self.graph.nodes[gate_id]['outputs']
        outputs[outputs.index(old_wire_name)] = new_wire_name
        self.graph.nodes[gate_id]['outputs'] = outputs

    def replace_input_wire(self, gate_id, old_wire_name, new_wire_name):
        """ Replace an input wire of a gate with a new wire name """
        if not self.graph.has_node(gate_id):
            self.raise_exception(f"Gate ID '{gate_id}' does not exist in the DAG.")
        if old_wire_name not in self.graph.nodes[gate_id]['inputs']:
            self.raise_exception(f"Old wire '{old_wire_name}' is not an input of gate '{gate_id}'.")
        if new_wire_name in self.graph.nodes[gate_id]['inputs']:
            self.raise_exception(f"New wire '{new_wire_name}' already exists as an input of gate '{gate_id}'.")

        # Update inputs
        inputs = self.graph.nodes[gate_id]['inputs']
        inputs[inputs.index(old_wire_name)] = new_wire_name
        self.graph.nodes[gate_id]['inputs'] = inputs
        if old_wire_name in self.graph.nodes[gate_id]['inverted']:
            self.graph.nodes[gate_id]['inverted'].remove(old_wire_name)
            self.graph.nodes[gate_id]['inverted'].add(new_wire_name)

        # Rename downstream wire segments recursively
        # segments of old wire -> segments of new wire
        # Note: wire segments is from in-out pin and not tracked as gate['outputs']
        for _, to_gate_id, edge_data in self.graph.out_edges(gate_id, data=True):
            wire_name = edge_data.get('wire_name', None)
            if self.is_same_wire(wire_name, old_wire_name):
                next_wire_name = self.generate_unique_wire_segment_name(new_wire_name)
                self.graph[gate_id][to_gate_id]['wire_name'] = next_wire_name
                self.replace_input_wire(to_gate_id, wire_name, next_wire_name)

    def invert_input_wire(self, gate_id, target_wire_name):
        """ Invert an input of a gate and trace downstream wire segments """
        if not self.graph.has_node(gate_id):
            self.raise_exception(f"Gate ID '{gate_id}' does not exist in the DAG.")
        if target_wire_name not in self.graph.nodes[gate_id]['inputs']:
            self.raise_exception(f"Wire '{target_wire_name}' is not an input of gate '{gate_id}'.")
        # Invert the input wire
        if target_wire_name in self.graph.nodes[gate_id]['inverted']:
            self.graph.nodes[gate_id]['inverted'].remove(target_wire_name)
        else:
            self.graph.nodes[gate_id]['inverted'].add(target_wire_name)
        # Update downstream wire segments recursively
        for _, to_gate_id, edge_data in self.graph.out_edges(gate_id, data=True):
            wire_name = edge_data.get('wire_name', '')
            if self.is_same_wire(wire_name, target_wire_name):
                self.invert_input_wire(to_gate_id, wire_name)

    def is_input_wire_inverted(self, gate_id, wire_name):
        """ Check if an input wire of a gate is inverted """
        if not self.graph.has_node(gate_id):
            self.raise_exception(f"Gate ID '{gate_id}' does not exist in the DAG.")
        if wire_name not in self.graph.nodes[gate_id]['inputs']:
            self.raise_exception(f"Wire '{wire_name}' is not an input of gate '{gate_id}'.")
        return wire_name in self.graph.nodes[gate_id]['inverted']

    def uniqufy_gate_id(self, new_gate_id):
        """ Ensure the new gate ID is unique by appending a suffix """
        suffix = 1
        while f"{new_gate_id}_{suffix}" in self.graph:
            suffix += 1
        return f"{new_gate_id}_{suffix}"

    def uniqufy_wire_name(self, new_wire_name):
        """ Ensure the new wire name is unique by appending a suffix """
        # TODO: Improve efficiency
        wire_names = set()
        for _, _, edge_data in self.graph.edges(data=True):
            wire_name = edge_data.get('wire_name', None)
            wire_names.add(wire_name)
        suffix = 1
        while f'{new_wire_name}_{suffix}' in wire_names:
            suffix += 1
        if self.debug_level >= 4:
            print(f"INFO: Generated unique wire name: {new_wire_name}_{suffix}")
        return f"{new_wire_name}_{suffix}"

    def generate_unique_wire_segment_name(self, wire_name):
        """ Generate a unique wire segment name based on the base wire name """
        base_name = self.get_wire_base_name(wire_name)
        new_name = self.uniqufy_wire_name(f"{base_name}{self.wire_segment_marker}")
        if self.debug_level >= 4:
            print(f"INFO: Generated unique wire segment: {new_name} from wire: {wire_name}")
        return new_name

    def is_same_wire(self, wire_name1, wire_name2):
        """ Check if two wire names refer to the same wire """
        if wire_name1 is None or wire_name2 is None:
            return False
        if wire_name1 == wire_name2:
            return True
        tokens1 = wire_name1.split(self.wire_segment_marker)
        tokens2 = wire_name2.split(self.wire_segment_marker)
        return tokens1[0] == tokens2[0]

    def is_wire_segment(self, wire_name):
        """ Check if a wire name is a segment of a wire (contains wire segment marker) """
        return self.wire_segment_marker in wire_name

    def get_wire_base_name(self, wire_name):
        """ Get the base name of a wire, removing any segment suffix """
        if not self.is_wire_segment(wire_name):
            return wire_name
        return wire_name.split(self.wire_segment_marker)[0]

    def debug_print(self, enable_breakpoint=False):
        """ Print debug information about the DAG """
        print(self)
        if enable_breakpoint:
            breakpoint()

    def get_gate_info_str(self, gate_id):
        """ Get gate information as a string by gate ID """
        node = self.graph.nodes.get(gate_id)
        output_str = ''
        for output in node['outputs']:
            output_str += ' [~]' if output in node['inverted'] else ' '
            output_str += f"{output}"
        input_str = ''
        for input in node['inputs']:
            input_str += ' [~] ' if input in node['inverted'] else '     '
            input_str += f"{input:<10}"
        input_str = input_str.rstrip()
        return f"{node['gate_func']:<10} | {node['gate_id']:<15} | OUT:{output_str:<25} | IN:{input_str}"

    def __repr__(self):
        """ String representation of the DAG """
        repr_str = ""
        repr_str += "--------\n"
        print(f"DEBUG: Input Ports = {self.__in_ports}")
        print(f"DEBUG: Output Ports = {self.__out_ports}")
        repr_str += "--------\n"
        for from_gate_id, to_gate_id, edge_data in self.graph.edges(data=True):
            wire_name = edge_data.get('wire_name', None)
            if wire_name is None:
                self.raise_exception(f"Edge without wire_name found between {from_gate_id} and {to_gate_id}.")
            repr_str += f"Edge: {from_gate_id} -> {to_gate_id} | Wire: {wire_name}\n"
        repr_str += "--------\n"
        for gate_id in self.get_topo_sorted_gate_id_list():
            repr_str += self.get_gate_info_str(gate_id) + "\n"
        repr_str += "--------\n"
        return repr_str

    def get_in_ports(self):
        """ Get the input ports of the DAG """
        return self.__in_ports.copy()

    def get_out_ports(self):
        """ Get the output ports of the DAG """
        return self.__out_ports.copy()

    def is_in_port(self, wire_name_or_gate_id):
        """ Check if a wire name or gate id is an input port """
        return self.graph.has_node(wire_name_or_gate_id) and \
               self.graph.nodes[wire_name_or_gate_id]['gate_func'] == 'in_port'

    def is_out_port(self, wire_name_or_gate_id):
        """ Check if a wire name or gate id is an output port """
        return self.graph.has_node(wire_name_or_gate_id) and \
               self.graph.nodes[wire_name_or_gate_id]['gate_func'] == 'out_port'

    def get_wire_fanin_gate_ids(self, wire_name):
        """ Get the fanin gate IDs for a given wire name """
        gate_ids = set()
        for from_gate_id, _, edge_data in self.graph.edges(data=True):
            if wire_name == edge_data.get('wire_name', None):
                gate_ids.add(from_gate_id)
        return sorted(list(gate_ids))

    def get_wire_fanout_gate_ids(self, wire_name):
        """ Get the fanout gate IDs for a given wire name """
        gate_ids = set()
        for _, to_gate_id, edge_data in self.graph.edges(data=True):
            if wire_name == edge_data.get('wire_name', None):
                gate_ids.add(to_gate_id)
        return sorted(list(gate_ids))

    def get_wire_name(self, from_gate_id, to_gate_id):
        """ Get the wire name connecting two gates """
        if not self.graph.has_edge(from_gate_id, to_gate_id):
            self.raise_exception(f"No wire exists between {from_gate_id} and {to_gate_id}.")
        return self.graph[from_gate_id][to_gate_id]['wire_name']

    def priority_khan_topo_sort(self):
        """ Perform priority-aware topological sort based on Kahn's algorithm """
        if self.debug_level >= 1:
            print("DEBUG: Performing priority-aware topological sort based on Khan's algorithm.")
        orig_indeg = dict(self.graph.in_degree(self.graph))
        indeg = dict(self.graph.in_degree(self.graph))
        # Treat zero-degree and port-copy gates as sources
        def is_port_copy(gate_id):
            if self.graph.nodes[gate_id]['gate_func'] in ['copy', 'copy_inout']:
                preds = list(self.graph.predecessors(gate_id))
                if len(preds) == 1 and preds[0] in self.__in_ports:
                    return True
            return False
        is_source = {gate_id: indeg[gate_id] == 0 or is_port_copy(gate_id) for gate_id in self.graph.nodes}
        ready_int = deque()
        ready_src = deque(self.__in_ports)  # add in ports first
        ready_src += deque([gate_id for gate_id, degree in indeg.items() if degree == 0 and not gate_id in self.__in_ports])
        order = []

        def can_unlock_successor(gate_id):
            return any(indeg[succ] == 1 for succ in self.graph.successors(gate_id))
        def gate_score(gate_id):
            score = 0
            for succ in self.graph.successors(gate_id):
                if indeg[succ] == 1:
                    score += 1
                    # Optimization: Prioritize in_ports that drive ready multi-output successors
                    if orig_indeg[succ] > 1 and self.is_in_port(gate_id):
                        score += orig_indeg[succ]
            return score
        def pick_most_critical(ready_list):
            return max(ready_list, key=gate_score)

        while ready_int or ready_src:
            if ready_int:
                # Prioritize INT1: non-copy gates
                crit_int1 = [gate_id for gate_id in ready_int if self.graph.nodes[gate_id]['gate_func'] not in ['copy', 'copy_inout']]
                if crit_int1:
                    gate_id = pick_most_critical(crit_int1)
                else:
                    # Prioritize INT2: Gates on critical paths
                    crit_int2 = [gate_id for gate_id in ready_int if can_unlock_successor(gate_id)]
                    if crit_int2:
                        gate_id = pick_most_critical(crit_int2)
                    else:
                        # Prioritize INT3: Rest non-source gates
                        gate_id = ready_int[0]
                ready_int.remove(gate_id)
            else:
                # Prioritize SRC1: In ports or port-copy gates on critical paths 
                crit_src1 = [gate_id for gate_id in ready_src if (gate_id in self.__in_ports or is_port_copy(gate_id)) and can_unlock_successor(gate_id)]
                if crit_src1:
                    gate_id = pick_most_critical(crit_src1)
                else:
                    # Prioritize SRC2: Source gates on critical paths
                    crit_src2 = [gate_id for gate_id in ready_src if is_source[gate_id] and can_unlock_successor(gate_id)]
                    if crit_src2:
                        gate_id = pick_most_critical(crit_src2)
                    else:
                        # Prioritize SRC3: Rest in ports or port-copy gates
                        crit_src3 = [gate_id for gate_id in ready_src if gate_id in self.__in_ports or is_port_copy(gate_id)]
                        if crit_src3:
                            gate_id = pick_most_critical(crit_src3)
                        else:
                            # Prioritize SRC4: Rest source gates
                            gate_id = ready_src[0]
                ready_src.remove(gate_id)
            order.append(gate_id)
            for succ in self.graph.successors(gate_id):
                indeg[succ] -= 1
                if indeg[succ] == 0:
                    if is_source[succ]:
                        ready_src.append(succ)
                    else:
                        ready_int.append(succ)
        if len(order) != len(self.graph):
            self.raise_exception("Topological sort failed: not all nodes were processed.")
        return order
 
    def source_insertion_topo_sort(self):
        """ Perform topological sort then insert sources right before first use """
        if self.debug_level >= 1:
            print("DEBUG: Performing topological sort with source insertion.")
        indeg = dict(self.graph.in_degree(self.graph))
        # Treat zero-degree non-in-port and port-copy gates as sources
        def is_port_copy(gate_id):
            if self.graph.nodes[gate_id]['gate_func'] in ['copy', 'copy_inout']:
                preds = list(self.graph.predecessors(gate_id))
                if len(preds) == 1 and preds[0] in self.__in_ports:
                    return True
            return False
        is_source = {gate_id: (indeg[gate_id] == 0 and not self.is_in_port(gate_id)) or is_port_copy(gate_id) for gate_id in self.graph.nodes}
        # Create original topological order
        order = list(nx.topological_sort(self.graph))
        # Split into sources and internal gates
        src_gate_buffer = set()
        for gate_id in order:
            if is_source[gate_id]:
                src_gate_buffer.add(gate_id)
        new_order = []
        for gate_id in order:
            if not is_source[gate_id]:
                preds = list(self.graph.predecessors(gate_id))
                for pred in preds:
                    if pred in src_gate_buffer:
                        new_order.append(pred)
                        src_gate_buffer.remove(pred)
                new_order.append(gate_id)
            else:
                pass
        if src_gate_buffer:
            self.raise_exception(f"Source insertion failed: remaining sources {src_gate_buffer} not inserted.")
        return new_order

    def alsp_topo_sort(self):
        """ Perform topological sort using ALSP algorithm """
        if self.debug_level >= 1:
            print("DEBUG: Performing topological sort with ALAP scheduling.")
        # Compute duration
        dur = {}
        for v in self.graph.nodes:
            dur[v] = 1
        # Compute ASAP
        asap = {}
        for v in nx.topological_sort(self.graph):
            preds = list(self.graph.predecessors(v))
            asap[v] = 0 if not preds else max(asap[p] + 1 for p in preds)
        # Compute ALAP
        t_max = max(asap.values())
        alap = {}
        for v in reversed(list(nx.topological_sort(self.graph))):
            succs = list(self.graph.successors(v))
            alap[v] = t_max if not succs else min(alap[s] - 1 for s in succs)
        # Compute slack
        slack = {n: alap[n] - asap[n] for n in self.graph.nodes}
        # Compute ALAP order
        alap_order = sorted(alap, key=lambda n: (alap[n], slack[n]))
        if self.debug_level >= 3:
            print("DEBUG: ASAP, ALAP, Slack")
            for v in alap_order:
                print(f"    ASAP={asap[v]}, ALAP={alap[v]}, Slack={slack[v]}, Dur={dur[v]} : Gate {self.get_gate_info_str(v)}")
        return alap_order

    def register_pressure_topo_sort(self):
        """ Topological sort based on register pressure """
        if self.debug_level >= 1:
            print("DEBUG: Performing topological sort with register pressure aware list scheduling.")
        # Compute duration
        dur = {}
        for v in self.graph.nodes:
            dur[v] = 1
        # Compute ASAP
        asap = {}
        for v in nx.topological_sort(self.graph):
            preds = list(self.graph.predecessors(v))
            asap[v] = 0 if not preds else max(asap[p] + dur[v] for p in preds)
        # Compute ALAP
        t_max = max(asap.values())
        alap = {}
        for v in reversed(list(nx.topological_sort(self.graph))):
            succs = list(self.graph.successors(v))
            alap[v] = t_max if not succs else min(alap[s] - dur[v] for s in succs)
        # Compute slack
        slack = {n: alap[n] - asap[n] for n in self.graph.nodes}
        # Run register pressure aware list scheduling
        indeg = dict(self.graph.in_degree(self.graph))
        ready = deque([gate_id for gate_id in self.graph.nodes if indeg[gate_id] == 0])
        scheduled, live, order = set(), set(), []
        t = 0
        while ready:
            def cost(n):
                #if self.graph.nodes[n]['gate_func'] in ['in_port']:
                #    return (-10000, -10000)  # schedule in_port first
                urgency = alap[n] - t
                urgency = 0
                delta = 1
                delta -= sum(1 for p in self.graph.predecessors(n) if p in live)
                return (delta, urgency)
            best = min(ready, key=cost)
            ready.remove(best)
            order.append(best)
            scheduled.add(best)
            for p in self.graph.predecessors(best):
                live.discard(p)
            live.add(best)
            for succ in self.graph.successors(best):
                if all(pred in scheduled for pred in self.graph.predecessors(succ)):
                    ready.append(succ)
            t += dur[best]
        if self.debug_level >= 3:
            print("DEBUG: New order")
            for i, v in enumerate(order):
                print(f"    ASAP={asap[v]}, ALAP={alap[v]}, Slack={slack[v]}, Dur={dur[v]} : Gate {self.get_gate_info_str(v)}")
        return order

    def register_pressure_topo_sort2(self):
        """ Topological sort based on register pressure """
        if self.debug_level >= 1:
            print("DEBUG: Performing topological sort with register pressure aware list scheduling.")
        # Compute duration
        dur = {}
        for v in self.graph.nodes:
            dur[v] = 1
        # Compute ASAP
        asap = {}
        for v in nx.topological_sort(self.graph):
            preds = list(self.graph.predecessors(v))
            asap[v] = 0 if not preds else max(asap[p] + dur[v] for p in preds)
        # Compute ALAP
        t_max = max(asap.values())
        alap = {}
        for v in reversed(list(nx.topological_sort(self.graph))):
            succs = list(self.graph.successors(v))
            alap[v] = t_max if not succs else min(alap[s] - dur[v] for s in succs)
        # Compute slack
        slack = {n: alap[n] - asap[n] for n in self.graph.nodes}
        # Run register pressure aware list scheduling
        indeg = dict(self.graph.in_degree(self.graph))
        ready = deque([gate_id for gate_id in self.graph.nodes if indeg[gate_id] == 0])
        scheduled, live, order = set(), set(), []
        t = 0
        while ready:
            def cost(n):
                if self.graph.nodes[n]['gate_func'] in ['in_port']:
                    return (-10000, -10000)  # schedule in_port first
                urgency = alap[n] - t
                urgency = 0
                delta = 1
                delta -= sum(1 for p in self.graph.predecessors(n) if p in live)
                return (delta, urgency)
            best = min(ready, key=cost)
            ready.remove(best)
            order.append(best)
            scheduled.add(best)
            for p in self.graph.predecessors(best):
                live.discard(p)
            live.add(best)
            for succ in self.graph.successors(best):
                if all(pred in scheduled for pred in self.graph.predecessors(succ)):
                    ready.append(succ)
            t += dur[best]
        # Pospone in-ports
        new_order = []
        added_in_ports = set()
        for gate_id in order:
            if self.is_in_port(gate_id):
                continue
            else:
                for pred in self.graph.predecessors(gate_id):
                    if self.is_in_port(pred) and pred not in added_in_ports:
                        new_order.append(pred)
                        added_in_ports.add(pred)
                new_order.append(gate_id)
        if self.debug_level >= 3:
            print("DEBUG: New order")
            for i, v in enumerate(new_order):
                print(f"    ASAP={asap[v]}, ALAP={alap[v]}, Slack={slack[v]}, Dur={dur[v]} : Gate {self.get_gate_info_str(v)}")
        return new_order

    def get_topo_sorted_gate_id_list(self):
        """ Get a list of all gates in topological order """
        if self.topo_sort_algorithm == 1:
            return self.priority_khan_topo_sort()
        elif self.topo_sort_algorithm == 2:
            return self.source_insertion_topo_sort()
        elif self.topo_sort_algorithm == 3:
            return self.alsp_topo_sort()
        elif self.topo_sort_algorithm == 4:
            return self.register_pressure_topo_sort()
        elif self.topo_sort_algorithm == 5:
            return self.register_pressure_topo_sort2()
        else:
            return list(nx.topological_sort(self.graph))

    def get_wire_name_list(self, skip_port=True, merge_segments=True):
        """ Get a list of internal wires in sorted gate order """
        wire_names = set()
        gate_ids = self.get_topo_sorted_gate_id_list()
        for gate_id in gate_ids:
            for _, _, edge_data in self.graph.out_edges(gate_id, data=True):
                wire_name = edge_data.get('wire_name', None)
                if wire_name is None:
                    self.raise_exception(f"Edge without wire_name found for gate {gate_id}.")
                if merge_segments:
                    wire_name = self.get_wire_base_name(wire_name)
                if skip_port and (self.is_in_port(wire_name) or self.is_out_port(wire_name)):
                    continue  # skip ports
                wire_names.add(wire_name)
        return list(wire_names)

    def get_reusable_inout_wires(self, gate_id):
        """ Get reusable inout wires for a given gate ID """
        gate = self.graph.nodes[gate_id]
        if gate['gate_func'] not in ['and2', 'or2', 'maj3']:
            return []
        segmented_wires = []
        for _, _, edge_data in self.graph.out_edges(gate_id, data=True):
            wire_name = edge_data.get('wire_name', None)
            if wire_name is None:
                continue
            if self.is_wire_segment(wire_name):
                segmented_wires.append(self.get_wire_base_name(wire_name))
        reusable_inout_wires = []
        for wire_name in gate['inputs']:
            # Skip input that already has a segment
            if wire_name in segmented_wires:
                continue
            # Skip input if it is an in/out port
            if self.is_in_port(wire_name) or self.is_out_port(wire_name):
                continue
            reusable_inout_wires.append(wire_name)
        return reusable_inout_wires

    def sanitize_name(self, wire_name):
        """ Sanitize wire/port/gate name by removing segment suffix """
        wire_name = wire_name.replace("[", "_").replace("]", "_")
        return self.get_wire_base_name(wire_name)

    def sanity_check(self):
        """ Perform sanity checks on the DAG """
        self.sanity_check_ports()
        wire_fanins, wire_fanouts = self.sanity_check_wires()
        self.sanity_check_gates(wire_fanins, wire_fanouts)
        self.sanity_check_analog_pim(wire_fanins, wire_fanouts)

    def sanity_check_ports(self):
        """ Sanity check for ports """
        if self.debug_level >= 2:
            print("INFO: Input/output port sanity check...")
        for in_port in self.__in_ports:
            gate_node = self.graph.nodes.get(in_port)
            if gate_node['gate_func'] != 'in_port':
                self.raise_exception(f"Input port '{in_port}' is not correctly set as an input port.")
        for out_port in self.__out_ports:
            gate_node = self.graph.nodes.get(out_port)
            if gate_node['gate_func'] != 'out_port':
                self.raise_exception(f"Output port '{out_port}' is not correctly set as an output port.")
        for gate_id in self.graph.nodes:
            gate_node = self.graph.nodes[gate_id]
            if gate_node['gate_func'] in ['in_port', 'zero', 'one']:
                if gate_node['inputs']:
                    self.raise_exception(f"Gate '{gate_id}' should not have inputs.")
            if gate_node['gate_func'] == 'in_port':
                if not gate_id in self.__in_ports:
                    self.raise_exception(f"Input port '{gate_id}' is not in the input ports list.")
            if gate_node['gate_func'] == 'out_port':
                if gate_node['outputs']:
                    self.raise_exception(f"Output port '{gate_id}' should not have outputs.")
                if not gate_id in self.__out_ports:
                    self.raise_exception(f"Output port '{gate_id}' is not in the output ports list.")

    def sanity_check_wires(self):
        """ Sanity check for wires"""
        if self.debug_level >= 2:
            print("INFO: Wire connection sanity check...")
        wire_fanins = {}
        wire_fanouts = {}
        for from_gate_id, to_gate_id, edge_data in self.graph.edges(data=True):
            wire_name = edge_data.get('wire_name', None)
            if wire_name is None:
                self.raise_exception(f"Edge without wire_name found between {from_gate_id} and {to_gate_id}.")
            wire_fanins.setdefault(wire_name, set()).add(from_gate_id)
            wire_fanouts.setdefault(wire_name, set()).add(to_gate_id)
        for wire_name in set(wire_fanins.keys()).union(wire_fanouts.keys()):
            fanins = wire_fanins.get(wire_name, set())
            fanouts = wire_fanouts.get(wire_name, set())
            if len(fanins) != 1:
                self.raise_exception(f"Wire '{wire_name}' has multiple fanins: {fanins}. Expected a single fanin.")
            if not fanouts:
                self.raise_exception(f"Wire '{wire_name}' has no fanouts: {fanouts}. Expected at least one fanout.")
        # Check wire segments branching
        # Wire segments should form a chain, not a tree
        for gate_id in self.graph.nodes:
            fanout_wire_segments = {}  # base_name -> set of segments
            for from_gate_id, to_gate_id, edge_data in self.graph.out_edges(gate_id, data=True):
                wire_name = edge_data.get('wire_name', '')
                wire_base_name = self.get_wire_base_name(wire_name)
                fanout_wire_segments.setdefault(wire_base_name, [])
                fanout_wire_segments[wire_base_name].append(wire_name)
            for wire_base_name, segments in fanout_wire_segments.items():
                total = len(segments)
                num_segments = len([s for s in segments if self.is_wire_segment(s)])
                if num_segments > 1 or (total > 1 and num_segments > 0):
                    self.raise_exception(f"Gate '{gate_id}' has multiple segments for wire '{wire_base_name}': {segments}.")
        return wire_fanins, wire_fanouts

    def sanity_check_gates(self, wire_fanins, wire_fanouts):
        """ Sanity check for gates """
        if self.debug_level >= 2:
            print("INFO: Gate input/output sanity check...")
        for gate_id in self.graph.nodes:
            gate_node = self.graph.nodes[gate_id]
            input_wires = gate_node['inputs']
            output_wires = gate_node['outputs']
            input_base_names = set([self.get_wire_base_name(wire) for wire in input_wires])
            # Note: Until the final step, it's possible that multiple segments of the same wire are used as inputs of
            #       the same gate, e.g., from different paths driving different input pins
            if self.debug_level >= 2:
                if len(input_base_names) != len(input_wires):
                    print(f"Warning: Gate '{gate_id}' has multiple input segments of the same wire: {input_wires}.")
            for input_wire in input_wires:
                if gate_id not in wire_fanouts[input_wire]:
                    self.raise_exception(f"Gate '{gate_id}' not found in fanouts of input wire '{input_wire}'.")
            for output_wire in output_wires:
                if gate_id not in wire_fanins[output_wire]:
                    self.raise_exception(f"Gate '{gate_id}' not found in fanins of output wire '{output_wire}'.")
            if gate_node['gate_func'] == 'in_port':
                if input_wires:
                    self.raise_exception(f"Input port '{gate_id}' should not have any input wires.")
                if len(output_wires) > 1: # some input port may have no output wires
                    self.raise_exception(f"Input port '{gate_id}' should have at most one output wire.")
                if output_wires and output_wires[0] != gate_id:
                    self.raise_exception(f"Output wire '{output_wires[0]}' of input port '{gate_id}' should match the gate ID.")
                if gate_node['inverted']:
                    self.raise_exception(f"Input port '{gate_id}' should not have any inverted wires.")
            if gate_node['gate_func'] == 'out_port':
                if output_wires:
                    self.raise_exception(f"Output port '{gate_id}' should not have any output wires.")
                if len(input_wires) != 1:
                    self.raise_exception(f"Output port '{gate_id}' should have exactly one input wire.")
                if input_wires[0] != gate_id:
                    self.raise_exception(f"Input wire '{input_wires[0]}' of output port '{gate_id}' should match the gate ID.")
                if gate_node['inverted']:
                    self.raise_exception(f"Output port '{gate_id}' should not have any inverted wires.")
            for wire_name in gate_node['inverted']:
                if wire_name not in input_wires:
                    self.raise_exception(f"Inverted wire '{wire_name}' of gate '{gate_id}' is not in its input wires.")
                if wire_name in output_wires:
                    self.raise_exception(f"Inverted wire '{wire_name}' of gate '{gate_id}' should not be in its output wires.")
                # Note: An output port wire can be used to drive internal logic.
                # If it drives an inverter then another gate, it hits this condition after inverter elimination.
                if self.debug_level >= 2:
                    if self.is_out_port(wire_name):
                        print(f"Warning: Inverted wire '{wire_name}' of gate '{gate_id}' is an output port wire.")

    def sanity_check_analog_pim(self, wire_fanins, wire_fanouts):
        """ Perform sanity checks specific to analog PIM mode """
        if self.pim_mode != 'analog':
            return
        num_analog_pim_violations = 0
        for wire_name in set(wire_fanins.keys()).union(wire_fanouts.keys()):
            fanins = wire_fanins.get(wire_name, set())
            fanouts = wire_fanouts.get(wire_name, set())
            num_input_destroying_gates = 0
            for fanout in fanouts:
                if self.graph.nodes[fanout]['gate_func'] in ['and2', 'or2', 'maj3']:
                    num_input_destroying_gates += 1
            if num_input_destroying_gates > 1 or (num_input_destroying_gates == 1 and len(fanins) > 1):
                num_analog_pim_violations += 1
                if self.debug_level >= 4:
                    print(f"Warning: Wire '{wire_name}' violates analog PIM input-destroying gate rule")
        print(f"INFO: Found {num_analog_pim_violations} analog PIM violations in the DAG.")

    def verify_dag(self, pim_mode='digital'):
        """ Verify the DAG with input/output simulation """
        self.verifier.verify(pim_mode=pim_mode)

    @staticmethod
    def save_dag_as_json(dag, file_path):
        """ Save the DAG as a JSON file """
        # Export graph with embedded attributes
        dag = copy.deepcopy(dag)  # Avoid modifying the original DAG
        for node, data in dag.graph.nodes(data=True):
            # Ensure all attributes are serializable
            data['inverted'] = list(data.get('inverted', set()))
        data = json_graph.node_link_data(dag.graph, edges="links")
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_dag_from_json(file_path):
        """ Load a DAG from a JSON file """
        with open(file_path) as f:
            data = json.load(f)
        dag = DAG()
        dag.graph = json_graph.node_link_graph(data, edges="links")

        # Note: in_ports and out_port are not in exact order as in the original DAG
        for node, data in dag.graph.nodes(data=True):
            if data.get('gate_func') == 'in_port':
                dag.__in_ports.append(node)
            elif data.get('gate_func') == 'out_port':
                dag.__out_ports.append(node)
            dag.graph.nodes[node]['inverted'] = set(data.get('inverted', []))

        return dag

    @staticmethod
    def draw_interactive_circuit(dag, output_file="circuit.html"):
        """ Draw an interactive circuit using PyVis """
        network = Network(height='800px', width='100%', directed=True, notebook=False, filter_menu=True, cdn_resources='remote')

        for gate_id, data in dag.graph.nodes(data=True):
            gate_func = data.get('gate_func', 'unknown')
            if gate_func == 'in_port':
                label = f"{gate_id} ({gate_func[:-5]})"
                color = "#F9E79F"
            elif gate_func == 'out_port':
                label = f"{gate_id} ({gate_func[:-5]})"
                color = "#F5B7B1"
            elif gate_func == 'copy':
                label = f"{gate_id} ({gate_func})"
                color = "#A9DFBF"
            else:
                label = f"{gate_id} ({gate_func})"
                color = "#AED6F1"
            network.add_node(gate_id, label=label, shape="box", color=color)

        for u, v, edge_data in dag.graph.edges(data=True):
            label = edge_data.get('wire_name', 'unknown')
            network.add_edge(u, v, label=label)

        network.show_buttons(filter_=['physics'])
        # Save to html file instead of popup with show()
        network.save_graph(output_file)
        print(f"Interactive graph saved to: {output_file}")
