#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: util.py
Description: Utility functions
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Date: 2024-09-27
"""

import json
from networkx.readwrite import json_graph
from pyvis.network import Network
import networkx as nx

def getContent(fileName):
    try:
        with open(fileName, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "Error: File not found."
    except Exception as e:
        return f"Error: {e}"

def getFileLines(fileName):
    try:
        with open(fileName, 'r') as file:
            lines = file.readlines()
        return [line.strip() for line in lines]
    except FileNotFoundError:
        print(f"Error: The file '{fileName}' was not found.")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def writeToFile(fileName, content):
    try:
        with open(fileName, 'w') as file:
            file.write(content)
        print(f"Info: Content successfully written to {fileName}")
    except Exception as e:
        print(f"Error: {e}")

def concatenateListElements(lst):
    return ', '.join(map(str, lst))

def saveGraphAsJson(graph, filePath):
    data = json_graph.node_link_data(graph)
    with open(filePath, "w") as f:
        json.dump(data, f, indent=2)

def loadGraphFromJson(filePath):
    with open(filePath) as f:
        data = json.load(f)
    return json_graph.node_link_graph(data, edges="links")


def drawInteractiveCircuit(graph, outputFile="circuit.html"):
    net = Network(height='800px', width='100%', directed=True, notebook=False, filter_menu=True, cdn_resources='remote')

    # Add nodes with formatted labels
    for node, data in graph.nodes(data=True):
        gateType = data.get('type', 'unknown')
        outputs = ', '.join(data.get('outputs', []))
        label = f"{gateType}\n{outputs}"
        net.add_node(node, label=label, shape="box", color="#AED6F1")

    # Add edges with optional signal label
    for u, v in graph.edges():
        fromSignals = set(graph.nodes[u].get('outputs', []))
        toSignals = set(graph.nodes[v].get('inputs', []))
        common = fromSignals & toSignals
        label = ', '.join(common) if common else ''
        net.add_edge(u, v, label=label)

    net.show_buttons(filter_=['physics'])  # Optional: let user tweak layout
    net.show(outputFile)
    print(f"Interactive graph saved to: {outputFile}")

