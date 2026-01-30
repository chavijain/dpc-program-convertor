#!/usr/bin/env python3
"""
Example usage of the DPC Program Converter
"""

from dpc_converter import default_converter
import json

# Example 1: Convert JSON to YAML
print("Example 1: JSON to YAML conversion")
print("=" * 50)

json_data = {
    "application": "DPC Converter",
    "version": "1.0.0",
    "features": ["conversion", "testing", "extensibility"],
    "config": {
        "verbose": True,
        "timeout": 30
    }
}

json_string = json.dumps(json_data, indent=2)
print("Input (JSON):")
print(json_string)
print()

yaml_output = default_converter.convert(json_string, 'json', 'yaml')
print("Output (YAML):")
print(yaml_output)

# Example 2: Convert YAML to JSON
print("\nExample 2: YAML to JSON conversion")
print("=" * 50)

yaml_data = """
name: Sample Program
author: DPC Team
settings:
  debug: false
  port: 8080
"""

print("Input (YAML):")
print(yaml_data)

json_output = default_converter.convert(yaml_data, 'yaml', 'json')
print("Output (JSON):")
print(json_output)

# Example 3: Round-trip conversion
print("\nExample 3: Round-trip conversion (JSON -> YAML -> JSON)")
print("=" * 50)

original = {"test": "round-trip", "value": 123}
print(f"Original data: {original}")

# JSON to YAML
yaml_intermediate = default_converter.convert(json.dumps(original), 'json', 'yaml')
print(f"\nIntermediate (YAML):\n{yaml_intermediate}")

# YAML back to JSON
json_final = default_converter.convert(yaml_intermediate, 'yaml', 'json')
final_data = json.loads(json_final)
print(f"Final data: {final_data}")

if original == final_data:
    print("\n✓ Round-trip successful! Data preserved.")
else:
    print("\n✗ Round-trip failed! Data corrupted.")
