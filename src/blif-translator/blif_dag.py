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
from networkx.readwrite import json_graph
from pyvis.network import Network
import networkx as nx


class DAG:
    """ Directed Acyclic Graph (DAG) representation of a circuit """

    def __init__(self, module_name='', in_ports=[], out_ports=[], gate_info_list=[], debug_level=0):
        """
        DAG description:
        * Node
            - Represents a gate or an input/output port in the circuit
            - Attributes:
                - gate_id: Unique string identifier for the gate
                - gate_func: Function of the gate (e.g., inv1, and2, maj3, copy, in_port, out_port)
                - inputs: List of input wires with order preserved
                - outputs: List of output wires with order preserved
                - has_deps: Boolean indicating if the gate has dependencies (for scheduling)
            - APIs:
                - graph.add_node(gate_id): Add a gate node to the DAG
                - graph.nodes[gate_id]: Access gate information dictionary by gate ID
        * Edge
            - Represents a wire in the circuit
                - A wire may have multiple segaments because of in-out behavior of analog PIM
            - Attributes:
                - wire_name: Name of the wire
                - is_negated: False: not negated, True: negated (for analog PIM with dual-contact cells)
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
        self.debug_level = debug_level
        self.initialize(in_ports, out_ports, gate_info_list)

    def initialize(self, in_ports, out_ports, gate_info_list):
        """ Initialize DAG nodes and edges """
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
            gate_id = gate_info['gate_id']
            gate_func = gate_info['gate_func']
            gate_inputs = gate_info['inputs']
            gate_outputs = gate_info['outputs']
            self.add_gate(gate_id=gate_id, gate_func=gate_func, inputs=gate_inputs, outputs=gate_outputs)
        # Connect wires
        wire_fanins = {}
        wire_fanouts = {}
        for gate_info in gate_info_list:
            gate_id = gate_info['gate_id']
            gate_inputs = gate_info['inputs']
            gate_outputs = gate_info['outputs']
            for wire in gate_inputs:
                if wire not in wire_fanouts:
                    wire_fanouts[wire] = set()
                wire_fanouts[wire].add(gate_id)
            for wire in gate_outputs:
                if wire not in wire_fanins:
                    wire_fanins[wire] = set()
                wire_fanins[wire].add(gate_id)
        for wire in set(wire_fanins.keys()).union(wire_fanouts.keys()):
            fanins = wire_fanins.get(wire, [])
            fanouts = wire_fanouts.get(wire, [])
            if not fanins and not fanouts:
                raise ValueError(f"Wire '{wire}' has no fanins and fanouts")
            elif not fanins:  # input port
                assert wire in self.__in_ports, f"Wire '{wire}' has no fanins and is not an input port."
                self.graph.nodes[wire]['outputs'].append(wire)
                for gate_id in fanouts:
                    self.add_wire(wire_name=wire, fanin_gate_id=wire, fanout_gate_id=gate_id)
            elif not fanouts:  # output port
                assert wire in self.__out_ports, f"Wire '{wire}' has no fanouts and is not an output port."
                self.graph.nodes[wire]['inputs'].append(wire)
                for gate_id in fanins:
                    self.add_wire(wire_name=wire, fanin_gate_id=gate_id, fanout_gate_id=wire)
            else:
                assert wire not in self.__in_ports and wire not in self.__out_ports
                assert len(fanins) == 1, f"Wire '{wire}' has multiple fanins: {fanins}. Expected a single fanin."
                fanin_gate_id = next(iter(fanins))
                for gate_id in fanouts:
                    self.add_wire(wire_name=wire, fanin_gate_id=fanin_gate_id, fanout_gate_id=gate_id)

    def add_gate(self, gate_id='', gate_func='', inputs=[], outputs=[], has_deps=False):
        """ Add a gate to the DAG """
        if gate_id in self.graph:
            raise ValueError(f"Gate ID '{gate_id}' already exists in the DAG.")
        self.graph.add_node(gate_id,
                            gate_id=gate_id,
                            gate_func=gate_func,
                            inputs=inputs.copy(),
                            outputs=outputs.copy(),
                            has_deps=has_deps)

    def remove_gate(self, gate_id):
        """ Remove a gate from the DAG """
        if not self.graph.has_node(gate_id):
            raise ValueError(f"Gate ID '{gate_id}' does not exist in the DAG.")
        if self.graph.in_degree(gate_id) > 0 or self.graph.out_degree(gate_id) > 0:
            for u, v, edge_data in self.graph.in_edges(gate_id, data=True):
                print(f'Edge: {u} -> {v} | Attr: {edge_data}')
            for u, v, edge_data in self.graph.out_edges(gate_id, data=True):
                print(f'Edge: {u} -> {v} | Attr: {edge_data}')
            raise ValueError(f"Cannot remove gate '{gate_id}': it has connected wires.")
        self.graph.remove_node(gate_id)

    def add_wire(self, wire_name, fanin_gate_id, fanout_gate_id):
        """ Add a wire to the DAG """
        if not self.graph.has_node(fanin_gate_id) or not self.graph.has_node(fanout_gate_id):
            raise ValueError(f"Cannot add wire '{wire_name}': fanin or fanout gate does not exist.")
        if self.graph.has_edge(fanin_gate_id, fanout_gate_id):
            raise ValueError(f"Wire '{wire_name}' already exists between {fanin_gate_id} and {fanout_gate_id}.")
        self.graph.add_edge(fanin_gate_id, fanout_gate_id, wire_name=wire_name, is_negated=False)

    def remove_wire(self, fanin_gate_id, fanout_gate_id):
        """ Remove a wire (single edge only) from the DAG """
        if not self.graph.has_edge(fanin_gate_id, fanout_gate_id):
            raise ValueError(f"Wire does not exist between {fanin_gate_id} and {fanout_gate_id}.")
        wire_name = self.graph[fanin_gate_id][fanout_gate_id]['wire_name']
        self.graph.remove_edge(fanin_gate_id, fanout_gate_id)

    def set_wire_negated(self, fanin_gate_id, fanout_gate_id, is_negated):
        """ Set a wire (single edge only) as negated or not """
        if not self.graph.has_edge(fanin_gate_id, fanout_gate_id):
            raise ValueError(f"Wire does not exist between {fanin_gate_id} and {fanout_gate_id}.")
        self.graph[fanin_gate_id][fanout_gate_id]['is_negated'] = is_negated

    def is_wire_negated(self, fanin_gate_id, fanout_gate_id):
        """ Check if a wire (single edge only) is negated """
        if not self.graph.has_edge(fanin_gate_id, fanout_gate_id):
            raise ValueError(f"Wire does not exist between {fanin_gate_id} and {fanout_gate_id}.")
        return self.graph[fanin_gate_id][fanout_gate_id].get('is_negated', False)

    def replace_input_wire(self, gate_id, old_wire_name, new_wire_name):
        """ Replace an input wire of a gate with a new wire name """
        if not self.graph.has_node(gate_id):
            raise ValueError(f"Gate ID '{gate_id}' does not exist in the DAG.")
        if old_wire_name not in self.graph.nodes[gate_id]['inputs']:
            raise ValueError(f"Old wire '{old_wire_name}' is not an input of gate '{gate_id}'.")
        if new_wire_name in self.graph.nodes[gate_id]['inputs']:
            raise ValueError(f"New wire '{new_wire_name}' already exists as an input of gate '{gate_id}'.")

        # Update inputs
        inputs = self.graph.nodes[gate_id]['inputs']
        inputs[inputs.index(old_wire_name)] = new_wire_name
        self.graph.nodes[gate_id]['inputs'] = inputs

    def uniqufy_gate_id(self, new_gate_id):
        """ Ensure the new gate ID is unique by appending a suffix if necessary """
        if new_gate_id not in self.graph:
            return new_gate_id
        suffix = 1
        while f"{new_gate_id}_{suffix}" in self.graph:
            suffix += 1
        return f"{new_gate_id}_{suffix}"

    def uniqufy_wire_name(self, new_wire_name):
        """ Ensure the new wire name is unique by appending a suffix if necessary """
        # TODO: Improve efficiency
        wire_names = set()
        for from_gate_id, to_gate_id, edge_data in self.graph.edges(data=True):
            wire_name = edge_data.get('wire_name', None)
            wire_names.add(wire_name)
        suffix = 1
        while f'{new_wire_name}_{suffix}' in wire_names:
            suffix += 1
        return f"{new_wire_name}_{suffix}"

    def debug_print(self, enable_breakpoint=False):
        """ Print debug information about the DAG """
        print(f"DEBUG: Input Ports = {self.__in_ports}")
        print(f"DEBUG: Output Ports = {self.__out_ports}")
        print(self)
        if enable_breakpoint:
            breakpoint()

    def get_gate_info_str(self, gate_id):
        """ Get gate information as a string by gate ID """
        node = self.graph.nodes.get(gate_id)
        return f"{node['gate_func']:<10} {node['gate_id']:<10} | outputs: {str(node['outputs']):<20} | inputs: {str(node['inputs'])}"

    def __repr__(self):
        """ String representation of the DAG """
        repr_str = ""
        repr_str += "--------\n"
        for from_gate_id, to_gate_id, edge_data in self.graph.edges(data=True):
            wire_name = edge_data.get('wire_name', None)
            if wire_name is not None:
                is_negated = edge_data.get('is_negated', False)
                repr_str += f"Edge: {from_gate_id} -> {to_gate_id} | Wire: {wire_name}"
                repr_str += " | >>>>>>>>>> Negated\n" if is_negated else "\n"
            else:
                wire_label = edge_data.get('wire_label', None)
                if wire_label is None:
                    raise ValueError(f"Edge without wire_name or wire_label found between {from_gate_id} and {to_gate_id}.")
                repr_str += f"Edge: {from_gate_id} -> {to_gate_id} | Label: {wire_label} >>>>>>>>>>>>>>> <dep> \n"
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
        for from_gate_id, to_gate_id, edge_data in self.graph.edges(data=True):
            if wire_name == edge_data.get('wire_name', None):
                gate_ids.add(from_gate_id)
        return sorted(list(gate_ids))

    def get_wire_fanout_gate_ids(self, wire_name):
        """ Get the fanout gate IDs for a given wire name """
        gate_ids = set()
        for from_gate_id, to_gate_id, edge_data in self.graph.edges(data=True):
            if wire_name == edge_data.get('wire_name', None):
                gate_ids.add(to_gate_id)
        return sorted(list(gate_ids))

    def get_wire_name(self, from_gate_id, to_gate_id):
        """ Get the wire name connecting two gates """
        if not self.graph.has_edge(from_gate_id, to_gate_id):
            raise ValueError(f"No wire exists between {from_gate_id} and {to_gate_id}.")
        return self.graph[from_gate_id][to_gate_id]['wire_name']

    def get_topo_sorted_gate_id_list(self):
        """ Get a list of all gates in topological order """
        return [gate_id for gate_id in nx.topological_sort(self.graph)]

    def get_wire_name_list(self, skip_port=True, merge_segments=True):
        """ Get a list of internal wires in sorted gate order """
        wire_names = set()
        gate_ids = self.get_topo_sorted_gate_id_list()
        for gate_id in gate_ids:
            for u, v, edge_data in self.graph.out_edges(gate_id, data=True):
                wire_name = edge_data.get('wire_name', None)
                if wire_name is None:
                    continue  # skip dep edges
                if skip_port and (self.is_in_port(wire_name) or self.is_out_port(wire_name)):
                    continue  # skip ports
                if merge_segments:
                    wire_name = wire_name.split(' seg')[0]
                wire_names.add(wire_name)
        return list(wire_names)

    def get_reusable_inout_wires(self, gate_id):
        """ Get reusable inout wires for a given gate ID """
        gate = self.graph.nodes[gate_id]
        if gate['gate_func'] not in ['and2', 'or2', 'maj3']:
            return []
        segmented_wires = []
        for u, v, edge_data in self.graph.out_edges(gate_id, data=True):
            wire_name = edge_data.get('wire_name', None)
            if wire_name is None:
                continue
            if ' seg' in wire_name:
                segmented_wires.append(wire_name.split(' seg')[0])
        reusable_inout_wires = []
        for wire_name in gate['inputs']:
            if wire_name in segmented_wires:
                continue
            reusable_inout_wires.append(wire_name)
        return reusable_inout_wires

    @staticmethod
    def sanitize_name(wire_name):
        """ Sanitize wire/port/gate name by removing segment suffix """
        return wire_name.replace("[", "_").replace("]", "_").split(' seg')[0]

    def sanity_check(self):
        """ Perform sanity checks on the DAG """
        # Check if in_ports and out_ports are correct
        #print(self)
        if self.debug_level >= 2:
            print("INFO: Input/output port sanity check...")
        for in_port in self.__in_ports:
            gate_node = self.graph.nodes.get(in_port)
            assert gate_node['gate_func'] == 'in_port', f"Input port '{in_port}' is not correctly set as an input port."
        for out_port in self.__out_ports:
            gate_node = self.graph.nodes.get(out_port)
            assert gate_node['gate_func'] == 'out_port', f"Output port '{out_port}' is not correctly set as an output port."
        for gate_id in self.graph.nodes:
            gate_node = self.graph.nodes[gate_id]
            if gate_node['gate_func'] in ['in_port', 'zero', 'one']:
                assert gate_node['inputs'] == [], f"Gate '{gate_id}' should not have inputs."
            if gate_node['gate_func'] == 'in_port':
                assert gate_id in self.__in_ports, f"Input port '{gate_id}' is not in the input ports list."
            if gate_node['gate_func'] == 'out_port':
                assert gate_node['outputs'] == [], f"Output port '{gate_id}' should not have outputs."
                assert gate_id in self.__out_ports, f"Output port '{gate_id}' is not in the output ports list."
        # Check if wire_fanins and wire_fanouts are in sync
        if self.debug_level >= 2:
            print("INFO: Wire connection sanity check...")
        wire_fanins = {}
        wire_fanouts = {}
        for from_gate_id, to_gate_id, edge_data in self.graph.edges(data=True):
            wire_name = edge_data.get('wire_name', None)
            if wire_name is None:
                if edge_data.get('wire_label', None) not in ['dep-reuse', 'dep-copy']:
                    raise ValueError(f"Edge without wire_name or wire_label found between {from_gate_id} and {to_gate_id}.")
                continue
            wire_fanins.setdefault(wire_name, set()).add(from_gate_id)
            wire_fanouts.setdefault(wire_name, set()).add(to_gate_id)
        for wire_name in set(wire_fanins.keys()).union(wire_fanouts.keys()):
            fanins = wire_fanins.get(wire_name, set())
            fanouts = wire_fanouts.get(wire_name, set())
            assert len(fanins) == 1, f"Wire '{wire_name}' has multiple fanins: {fanins}. Expected a single fanin."
            assert len(fanouts) > 0, f"Wire '{wire_name}' has no fanouts: {fanouts}. Expected at least one fanout."
        # Check if gate inputs and outputs are in sync
        if self.debug_level >= 2:
            print("INFO: Gate input/output sanity check...")
        for gate_id in self.graph.nodes:
            gate_node = self.graph.nodes[gate_id]
            input_wires = gate_node['inputs']
            output_wires = gate_node['outputs']
            for input_wire in input_wires:
                if gate_id not in wire_fanouts[input_wire]:
                    raise ValueError(f"Gate '{gate_id}' not found in fanouts of input wire '{input_wire}'.")
            for output_wire in output_wires:
                if gate_id not in wire_fanins[output_wire]:
                    raise ValueError(f"Gate '{gate_id}' not found in fanins of output wire '{output_wire}'.")
            if gate_node['gate_func'] == 'in_port':
                assert len(input_wires) == 0, f"Input port '{gate_id}' should not have any input wires."
                assert len(output_wires) == 1, f"Input port '{gate_id}' should have exactly one output wire."
                assert output_wires[0] == gate_id, f"Output wire '{output_wires[0]}' of input port '{gate_id}' should match the gate ID."
            if gate_node['gate_func'] == 'out_port':
                assert len(output_wires) == 0, f"Output port '{gate_id}' should not have any output wires."
                assert len(input_wires) == 1, f"Output port '{gate_id}' should have exactly one input wire."
                assert input_wires[0] == gate_id, f"Input wire '{input_wires[0]}' of output port '{gate_id}' should match the gate ID."

    @staticmethod
    def save_dag_as_json(dag, file_path):
        """ Save the DAG as a JSON file """
        # Export graph with embedded attributes
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
            label = edge_data.get('wire_name', None)
            if label is None:
                label = edge_data.get('wire_label', 'unknown')
            network.add_edge(u, v, label=label)

        network.show_buttons(filter_=['physics'])
        # Save to html file instead of popup with show()
        network.save_graph(output_file)
        print(f"Interactive graph saved to: {output_file}")
