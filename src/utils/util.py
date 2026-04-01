#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: util.py
Description: Utility functions
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Date: 2024-09-27
"""

def getContent(file_name):
    try:
        with open(file_name, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "Error: File not found."
    except Exception as e:
        return f"Error: get_content: {e}"

def getFileLines(file_name):
    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()
        return [line.strip() for line in lines]
    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")
        return []
    except Exception as e:
        print(f"Error: get_file_lines: {e}")
        return []

def writeToFile(file_name, content):
    try:
        with open(file_name, 'w') as file:
            file.write(content)
        print(f"Info: Content successfully written to {file_name}")
    except Exception as e:
        print(f"Error: write_to_file: {e}")

def concatenateListElements(lst):
    return ', '.join(map(str, lst))

def natural_sort_key(s):
    """Sort key that treats embedded numbers numerically.
    e.g. A_2_ < A_10_, temp3 < temp12.
    """
    import re
    return [int(part) if part.isdigit() else part
            for part in re.split(r'(\d+)', s)]

def natural_sorted(lst):
    """Sort a list of strings with natural numeric ordering."""
    return sorted(lst, key=natural_sort_key)

