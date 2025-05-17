#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: util.py
Description: Utility functions
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Date: 2024-09-27
"""

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

