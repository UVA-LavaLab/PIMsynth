#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: dag_transformer_base.py
Description: Base class for DAG transformers.
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Date: 2025-05-08
"""

from blif_dag import DAG

class DagTransformer:
    """ Base class for DAG transformers """

    def apply(self, dag: DAG):
        """ Apply a transformation to the input DAG """
        raise NotImplementedError("Subclasses must implement the apply() method.")

