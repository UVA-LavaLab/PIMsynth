#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: dag_topo_sort.py
Description: Perform topological sort on the pre-scheduling IR to improve instruction scheduling performance.
Author: Deyaun Guo <guodeyuan@gmail.com>
"""

from collections import deque
import networkx as nx


def priority_khan_topo_sort(dag):
    """ Perform priority-aware topological sort based on Kahn's algorithm """
    in_ports = dag.get_in_ports()
    if dag.debug_level >= 2:
        print("DEBUG: Performing priority-aware topological sort based on Khan's algorithm.")
    orig_indeg = dict(dag.graph.in_degree(dag.graph))
    indeg = dict(dag.graph.in_degree(dag.graph))
    # Treat zero-degree and port-copy gates as sources
    def is_port_copy(gate_id):
        if dag.graph.nodes[gate_id]['gate_func'] in ['copy', 'copy_inout']:
            preds = list(dag.graph.predecessors(gate_id))
            if len(preds) == 1 and preds[0] in in_ports:
                return True
        return False
    is_source = {gate_id: indeg[gate_id] == 0 or is_port_copy(gate_id) for gate_id in dag.graph.nodes}
    ready_int = deque()
    ready_src = deque(in_ports)  # add in ports first
    ready_src += deque([gate_id for gate_id, degree in indeg.items() if degree == 0 and not gate_id in in_ports])
    order = []

    def can_unlock_successor(gate_id):
        return any(indeg[succ] == 1 for succ in dag.graph.successors(gate_id))
    def gate_score(gate_id):
        score = 0
        for succ in dag.graph.successors(gate_id):
            if indeg[succ] == 1:
                score += 1
                # Optimization: Prioritize in_ports that drive ready multi-output successors
                if orig_indeg[succ] > 1 and dag.is_in_port(gate_id):
                    score += orig_indeg[succ]
        return score
    def pick_most_critical(ready_list):
        return max(ready_list, key=gate_score)

    while ready_int or ready_src:
        if ready_int:
            # Prioritize INT1: non-copy gates
            crit_int1 = [gate_id for gate_id in ready_int if dag.graph.nodes[gate_id]['gate_func'] not in ['copy', 'copy_inout']]
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
            crit_src1 = [gate_id for gate_id in ready_src if (gate_id in in_ports or is_port_copy(gate_id)) and can_unlock_successor(gate_id)]
            if crit_src1:
                gate_id = pick_most_critical(crit_src1)
            else:
                # Prioritize SRC2: Source gates on critical paths
                crit_src2 = [gate_id for gate_id in ready_src if is_source[gate_id] and can_unlock_successor(gate_id)]
                if crit_src2:
                    gate_id = pick_most_critical(crit_src2)
                else:
                    # Prioritize SRC3: Rest in ports or port-copy gates
                    crit_src3 = [gate_id for gate_id in ready_src if gate_id in in_ports or is_port_copy(gate_id)]
                    if crit_src3:
                        gate_id = pick_most_critical(crit_src3)
                    else:
                        # Prioritize SRC4: Rest source gates
                        gate_id = ready_src[0]
            ready_src.remove(gate_id)
        order.append(gate_id)
        for succ in dag.graph.successors(gate_id):
            indeg[succ] -= 1
            if indeg[succ] == 0:
                if is_source[succ]:
                    ready_src.append(succ)
                else:
                    ready_int.append(succ)
    if len(order) != len(dag.graph):
        dag.raise_exception("Topological sort failed: not all nodes were processed.")
    return order


def source_insertion_topo_sort(dag):
    """ Perform topological sort then insert sources right before first use """
    in_ports = dag.get_in_ports()
    if dag.debug_level >= 2:
        print("DEBUG: Performing topological sort with source insertion.")
    indeg = dict(dag.graph.in_degree(dag.graph))
    # Treat zero-degree non-in-port and port-copy gates as sources
    def is_port_copy(gate_id):
        if dag.graph.nodes[gate_id]['gate_func'] in ['copy', 'copy_inout']:
            preds = list(dag.graph.predecessors(gate_id))
            if len(preds) == 1 and preds[0] in in_ports:
                return True
        return False
    is_source = {gate_id: (indeg[gate_id] == 0 and not dag.is_in_port(gate_id)) or is_port_copy(gate_id) for gate_id in dag.graph.nodes}
    # Create original topological order
    order = list(nx.topological_sort(dag.graph))
    # Split into sources and internal gates
    src_gate_buffer = set()
    for gate_id in order:
        if is_source[gate_id]:
            src_gate_buffer.add(gate_id)
    new_order = []
    for gate_id in order:
        if not is_source[gate_id]:
            preds = list(dag.graph.predecessors(gate_id))
            for pred in preds:
                if pred in src_gate_buffer:
                    new_order.append(pred)
                    src_gate_buffer.remove(pred)
            new_order.append(gate_id)
        else:
            pass
    if src_gate_buffer:
        dag.raise_exception(f"Source insertion failed: remaining sources {src_gate_buffer} not inserted.")
    return new_order


def alsp_topo_sort(dag):
    """ Perform topological sort using ALSP algorithm """
    if dag.debug_level >= 2:
        print("DEBUG: Performing topological sort with ALAP scheduling.")
    # Compute duration
    dur = {}
    for v in dag.graph.nodes:
        dur[v] = 1
    # Compute ASAP
    asap = {}
    for v in nx.topological_sort(dag.graph):
        preds = list(dag.graph.predecessors(v))
        asap[v] = 0 if not preds else max(asap[p] + 1 for p in preds)
    # Compute ALAP
    t_max = max(asap.values())
    alap = {}
    for v in reversed(list(nx.topological_sort(dag.graph))):
        succs = list(dag.graph.successors(v))
        alap[v] = t_max if not succs else min(alap[s] - 1 for s in succs)
    # Compute slack
    slack = {n: alap[n] - asap[n] for n in dag.graph.nodes}
    # Compute ALAP order
    alap_order = sorted(alap, key=lambda n: (alap[n], slack[n]))
    if dag.debug_level >= 3:
        print("DEBUG: ASAP, ALAP, Slack")
        for v in alap_order:
            print(f"    ASAP={asap[v]}, ALAP={alap[v]}, Slack={slack[v]}, Dur={dur[v]} : Gate {dag.get_gate_info_str(v)}")
    return alap_order


def register_pressure_topo_sort(dag):
    """ Topological sort based on register pressure """
    if dag.debug_level >= 2:
        print("DEBUG: Performing topological sort with register pressure aware list scheduling.")
    # Compute duration
    dur = {}
    for v in dag.graph.nodes:
        dur[v] = 1
    # Compute ASAP
    asap = {}
    for v in nx.topological_sort(dag.graph):
        preds = list(dag.graph.predecessors(v))
        asap[v] = 0 if not preds else max(asap[p] + dur[v] for p in preds)
    # Compute ALAP
    t_max = max(asap.values())
    alap = {}
    for v in reversed(list(nx.topological_sort(dag.graph))):
        succs = list(dag.graph.successors(v))
        alap[v] = t_max if not succs else min(alap[s] - dur[v] for s in succs)
    # Compute slack
    slack = {n: alap[n] - asap[n] for n in dag.graph.nodes}
    # Run register pressure aware list scheduling
    indeg = dict(dag.graph.in_degree(dag.graph))
    ready = deque([gate_id for gate_id in dag.graph.nodes if indeg[gate_id] == 0])
    scheduled, live, order = set(), set(), []
    t = 0
    while ready:
        def cost(n):
            #if dag.graph.nodes[n]['gate_func'] in ['in_port']:
            #    return (-10000, -10000)  # schedule in_port first
            urgency = alap[n] - t
            urgency = 0
            delta = 1
            delta -= sum(1 for p in dag.graph.predecessors(n) if p in live)
            return (delta, urgency)
        best = min(ready, key=cost)
        ready.remove(best)
        order.append(best)
        scheduled.add(best)
        for p in dag.graph.predecessors(best):
            live.discard(p)
        live.add(best)
        for succ in dag.graph.successors(best):
            if all(pred in scheduled for pred in dag.graph.predecessors(succ)):
                ready.append(succ)
        t += dur[best]
    if dag.debug_level >= 3:
        print("DEBUG: New order")
        for i, v in enumerate(order):
            print(f"    ASAP={asap[v]}, ALAP={alap[v]}, Slack={slack[v]}, Dur={dur[v]} : Gate {dag.get_gate_info_str(v)}")
    return order


def register_pressure_topo_sort2(dag):
    """ Topological sort based on register pressure """
    if dag.debug_level >= 2:
        print("DEBUG: Performing topological sort with register pressure aware list scheduling.")
    # Compute duration
    dur = {}
    for v in dag.graph.nodes:
        dur[v] = 1
    # Compute ASAP
    asap = {}
    for v in nx.topological_sort(dag.graph):
        preds = list(dag.graph.predecessors(v))
        asap[v] = 0 if not preds else max(asap[p] + dur[v] for p in preds)
    # Compute ALAP
    t_max = max(asap.values())
    alap = {}
    for v in reversed(list(nx.topological_sort(dag.graph))):
        succs = list(dag.graph.successors(v))
        alap[v] = t_max if not succs else min(alap[s] - dur[v] for s in succs)
    # Compute slack
    slack = {n: alap[n] - asap[n] for n in dag.graph.nodes}
    # Run register pressure aware list scheduling
    indeg = dict(dag.graph.in_degree(dag.graph))
    ready = deque([gate_id for gate_id in dag.graph.nodes if indeg[gate_id] == 0])
    scheduled, live, order = set(), set(), []
    t = 0
    while ready:
        def cost(n):
            if dag.graph.nodes[n]['gate_func'] in ['in_port']:
                return (-10000, -10000)  # schedule in_port first
            urgency = alap[n] - t
            urgency = 0
            delta = 1
            delta -= sum(1 for p in dag.graph.predecessors(n) if p in live)
            return (delta, urgency)
        best = min(ready, key=cost)
        ready.remove(best)
        order.append(best)
        scheduled.add(best)
        for p in dag.graph.predecessors(best):
            live.discard(p)
        live.add(best)
        for succ in dag.graph.successors(best):
            if all(pred in scheduled for pred in dag.graph.predecessors(succ)):
                ready.append(succ)
        t += dur[best]
    # Postpone in-ports
    new_order = []
    added_in_ports = set()
    for gate_id in order:
        if dag.is_in_port(gate_id):
            continue
        else:
            for pred in dag.graph.predecessors(gate_id):
                if dag.is_in_port(pred) and pred not in added_in_ports:
                    new_order.append(pred)
                    added_in_ports.add(pred)
            new_order.append(gate_id)
    if dag.debug_level >= 3:
        print("DEBUG: New order")
        for i, v in enumerate(new_order):
            print(f"    ASAP={asap[v]}, ALAP={alap[v]}, Slack={slack[v]}, Dur={dur[v]} : Gate {dag.get_gate_info_str(v)}")
    return new_order


def get_topo_sorted_gate_id_list(dag):
    """ Get a list of all instructions (gates) in topological order """
    algorithm = dag.topo_sort_algorithm
    if algorithm == 1:
        return priority_khan_topo_sort(dag)
    elif algorithm == 2:
        return source_insertion_topo_sort(dag)
    elif algorithm == 3:
        return alsp_topo_sort(dag)
    elif algorithm == 4:
        return register_pressure_topo_sort(dag)
    elif algorithm == 5:
        return register_pressure_topo_sort2(dag)
    else:
        return list(nx.topological_sort(dag.graph))

