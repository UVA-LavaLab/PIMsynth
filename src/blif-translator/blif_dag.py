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


class GateNode:
    """ Represents a logic gate in the DAG """

    def __init__(self, gate_id, gate_func, inputs, outputs):
        """ Initialize GateNode """
        self.gate_id = gate_id
        self.gate_func = gate_func
        self.inputs = inputs
        self.outputs = outputs
        self.has_deps = False  # for scheduling

    def __repr__(self):
        """ String representation of GateNode """
        return f"{self.gate_func:<10} | outputs: {str(self.outputs):<30} | inputs: {str(self.inputs)}"


class Dag:
    """ Directed Acyclic Graph (DAG) representation of a circuit """

    def __init__(self):
        """ Initialize the DAG """
        self.graph = nx.DiGraph()
        self.module_name = ''
        self.gate_info = {}
        self.wire_to_gate_id = {}
        # Access internal properties through methods
        self.__in_ports = []
        self.__out_ports = []
        self.__in_ports_set = set()
        self.__out_ports_set = set()

    def add_gate(self, gate: GateNode):
        """ Add a gate to the DAG """
        gate_id = gate.gate_id
        self.graph.add_node(gate_id)
        self.gate_info[gate_id] = gate

        # Add edges
        for input_wire in gate.inputs:
            if input_wire not in self.wire_to_gate_id:
                if not self.is_in_port(input_wire):
                    raise ValueError(f"Input wire '{input_wire}' not found in wire_to_gate_id mapping.")
                else:
                    continue
            fanin_gate_id = self.wire_to_gate_id[input_wire]
            self.graph.add_edge(fanin_gate_id, gate_id)

        for output_wire in gate.outputs:
            if output_wire in self.wire_to_gate_id:
                raise ValueError(f"Output wire '{output_wire}' already exists in wire_to_gate_id mapping.")
            self.wire_to_gate_id[output_wire] = gate_id

    def __repr__(self):
        """ String representation of the DAG """
        repr_str = ""
        for gate in self.get_gate_list():
            repr_str += gate.__repr__() + "\n"
        return repr_str

    def set_in_ports(self, in_ports):
        """ Set the input ports of the DAG """
        self.__in_ports = in_ports
        self.__in_ports_set = set(in_ports)

    def get_in_ports(self):
        """ Get the input ports of the DAG """
        return self.__in_ports

    def is_in_port(self, wire):
        """ Check if a wire is an input port """
        return wire in self.__in_ports_set

    def set_out_ports(self, out_ports):
        """ Set the output ports of the DAG """
        self.__out_ports = out_ports
        self.__out_ports_set = set(out_ports)

    def get_out_ports(self):
        """ Get the output ports of the DAG """
        return self.__out_ports

    def is_out_port(self, wire):
        """ Check if a wire is an output port """
        return wire in self.__out_ports_set

    def get_gate_list(self):
        """ Get a list of all gates in topological order """
        return [self.gate_info[gate_id] for gate_id in nx.topological_sort(self.graph)]

    def get_wire_list(self):
        """ Get a list of all wires """
        wire_list = []
        gate_list = self.get_gate_list()
        for gate in gate_list:
            wire = gate.outputs[0]
            if not self.is_out_port(wire):
                wire_list.append(wire)
        return wire_list


def save_dag_as_json(dag, file_path):
    """ Save the DAG as a JSON file """
    # Embed gate_info into node attributes
    for gate_id, gate in dag.gate_info.items():
        dag.graph.nodes[gate_id]["gate_func"] = gate.gate_func
        dag.graph.nodes[gate_id]["inputs"] = gate.inputs
        dag.graph.nodes[gate_id]["outputs"] = gate.outputs

    # Export graph with embedded attributes
    data = json_graph.node_link_data(dag.graph, edges="links")

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def load_dag_from_json(file_path):
    """ Load a DAG from a JSON file """
    with open(file_path) as f:
        data = json.load(f)

    dag = Dag()
    dag.graph = json_graph.node_link_graph(data, edges="links")

    # Rebuild gate_info and wire_to_gate_id
    for gate_id, attrs in dag.graph.nodes(data=True):
        gate = GateNode(
            gate_id=gate_id,
            gate_func=attrs.get("gate_func", "unknown"),
            inputs=attrs.get("inputs", []),
            outputs=attrs.get("outputs", [])
        )
        dag.gate_info[gate_id] = gate
        for output in gate.outputs:
            dag.wire_to_gate_id[output] = gate_id

    return dag

def draw_interactive_circuit(dag, output_file="circuit.html"):
    """ Draw an interactive circuit using PyVis """
    network = Network(height='800px', width='100%', directed=True, notebook=False, filter_menu=True, cdn_resources='remote')

    for gate_id, data in dag.graph.nodes(data=True):
        gate_func = data.get('gate_func', 'unknown')
        outputs = ', '.join(data.get('outputs', []))
        label = f"{gate_func}\n{outputs}"
        network.add_node(gate_id, label=label, shape="box", color="#AED6F1")

    for u, v, edge_data in dag.graph.edges(data=True):
        label = edge_data.get('label')
        if label is None:
            from_wires = set(dag.graph.nodes[u].get('outputs', []))
            to_wires = set(dag.graph.nodes[v].get('inputs', []))
            common = from_wires & to_wires
            label = ', '.join(common) if common else ''
        network.add_edge(u, v, label=label)

    network.show_buttons(filter_=['physics'])
    network.show(output_file)
    print(f"Interactive graph saved to: {output_file}")
