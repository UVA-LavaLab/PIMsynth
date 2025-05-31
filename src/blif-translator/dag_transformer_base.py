#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: dag_transformer_base.py
Description: Base class for DAG transformers.
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Date: 2025-05-08
"""

from blif_dag import Dag

class DagTransformer:
    def apply(self, dag: Dag) -> Dag:
        """Apply a transformation to the input DAG and return the modified DAG."""
        raise NotImplementedError("Subclasses must implement the apply() method.")

