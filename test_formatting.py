#!/usr/bin/env python3
"""
Test file for formatting tools.
This file has intentionally poor formatting to test Black, isort, and flake8.
"""

import os
import sys
from pathlib import Path


def badly_formatted_function():
    x = 1 + 2 * 3
    y = {"a": 1, "b": 2}
    z = [1, 2, 3, 4, 5]
    return x, y, z


class BadlyFormattedClass:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def get_info(self):
        return f"Name: {self.name}, Age: {self.age}"


if __name__ == "__main__":
    obj = BadlyFormattedClass("Test", 25)
    result = badly_formatted_function()
    print(f"Result: {result}")
    print(f"Object: {obj.get_info()}")

# This line has bad formatting to test the auto-formatter
badly_formatted_line = 123 + 456 * 789
