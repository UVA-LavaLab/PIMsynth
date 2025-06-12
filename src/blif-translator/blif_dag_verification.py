#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: blif_dag_verification.py
Description: Verify the correctness of DAG transformation with simulated inputs
Author: Deyaun Guo <guodeyuan@gmail.com>
Date: 2025-06-12
"""

class DagVerifier:
    """ Base class for DAG verifiers """

    def __init__(self, dag, debug_level=0):
        self.dag = dag
        self.debug_level = debug_level
        self.test_inputs = self.generate_test_inputs()
        self.cached_outputs = []

    def verify(self, pim_mode='digital'):
        """ Verify the correctness of the DAG transformation """
        test_outputs = []
        for i, test_input in enumerate(self.test_inputs):
            test_output = self.simulate(test_input, pim_mode)
            test_outputs.append(test_output)
            if self.debug_level >= 1:
                print(f'DAG-Verification: Test {i} {pim_mode}, Outputs: {[int(o) for o in test_output]}, Inputs: {[int(i) for i in test_input]}')
        if not self.cached_outputs:
            self.cached_outputs = test_outputs
        else:
            for i, cached_output in enumerate(self.cached_outputs):
                if cached_output != test_outputs[i]:
                    raise ValueError(f'DAG-Verification failed')
        print(f'DAG-Verification: Passed')

    def generate_test_inputs(self):
        """ Generate test inputs for the DAG """
        in_ports = self.dag.get_in_ports()
        num_inputs = len(in_ports)
        if num_inputs == 0:
            return [[]]
        test_inputs = []
        # Test 1: All 0
        test_inputs.append([False] * num_inputs)
        # Test 2: All 1
        test_inputs.append([True] * num_inputs)
        # Test 3: Alternative 0/1
        test_inputs.append([i % 2 == 0 for i in range(num_inputs)])
        # Test 4: Alternative 1/0
        test_inputs.append([i % 2 == 1 for i in range(num_inputs)])
        return test_inputs

    def simulate(self, test_input, pim_mode):
        """ Simulate the DAG with given inputs and return outputs """
        if len(test_input) != len(self.dag.get_in_ports()):
            raise ValueError("Number of inputs does not match the number of input ports in the DAG.")
        symbol_table = {}
        for i, input_port in enumerate(self.dag.get_in_ports()):
            symbol_table[input_port] = test_input[i]
        for gate_id in self.dag.get_topo_sorted_gate_id_list():
            self.evaluate_gate(gate_id, symbol_table, pim_mode)
        outputs = []
        for output_port in self.dag.get_out_ports():
            if output_port not in symbol_table:
                raise ValueError(f"Output port '{output_port}' not found in symbol table.")
            outputs.append(symbol_table[output_port])
        return outputs

    def evaluate_gate(self, gate_id, symbol_table, pim_mode):
        """ Evaluate a gate based on its function and inputs """
        gate = self.dag.graph.nodes[gate_id]
        gate_func = gate['gate_func']

        # Get input variables
        input_wires = gate['inputs']
        input_inverted = [wire in gate['inverted'] for wire in input_wires]
        input_variables = [var.split(' seg')[0] for var in input_wires]
        input_values = []
        for input_var, inverted in zip(input_variables, input_inverted):
            if input_var not in symbol_table:
                raise ValueError(f"Variable '{input_var}' not found in symbol table.")
            value = symbol_table[input_var]
            if inverted:
                value = not value
            input_values.append(value)

        # Evalute the gate function
        if gate_func == "in_port":
            output_value = symbol_table[gate_id]
        elif gate_func == "out_port":
            output_value = input_values[0]
        elif gate_func == "copy":
            output_value = input_values[0]
        elif gate_func == "copy_inout":
            output_value = input_values[0]
        elif gate_func == "inv1":
            output_value = not input_values[0]
        elif gate_func == "and2":
            output_value = input_values[0] and input_values[1]
        elif gate_func == "nand2":
            output_value = not (input_values[0] and input_values[1])
        elif gate_func == "or2":
            output_value = input_values[0] or input_values[1]
        elif gate_func == "nor2":
            output_value = not (input_values[0] or input_values[1])
        elif gate_func == "xor2":
            output_value = input_values[0] != input_values[1]
        elif gate_func == "xnor2":
            output_value = input_values[0] == input_values[1]
        elif gate_func == "mux2":
            output_value = input_values[2] if input_values[0] else input_values[1]
        elif gate_func == "maj3":
            output_value = int(input_values[0]) + int(input_values[1]) + int(input_values[2]) >= 2
        elif gate_func == "zero":
            output_value = False
        elif gate_func == "one":
            output_value = True
        else:
            raise ValueError(f"Unsupported gate function: {gate_func}")

        # Update output variables
        output_wires = gate['outputs']
        output_variables = [var.split(' seg')[0] for var in output_wires]
        for output_var in output_variables:
            symbol_table[output_var] = output_value

        # Update input variables for analog PIM
        if pim_mode == 'analog':
            if gate_func in ['and2', 'or2', 'maj3']:
                for input_var, inverted in zip(input_variables, input_inverted):
                    value = output_value if not inverted else not output_value
                    symbol_table[input_var] = value

