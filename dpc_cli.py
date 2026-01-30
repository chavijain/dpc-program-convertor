#!/usr/bin/env python3
"""
DPC Program Convertor CLI
Command-line interface for the data format converter
"""

import argparse
import sys
from pathlib import Path
from converter import DataConverter, convert_file


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='DPC Program Convertor - Convert data between JSON, CSV, XML, and YAML formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert JSON file to CSV
  python dpc_cli.py input.json output.csv --from json --to csv
  
  # Convert CSV to YAML
  python dpc_cli.py data.csv data.yaml --from csv --to yaml
  
  # Convert XML to JSON
  python dpc_cli.py config.xml config.json --from xml --to json
        """
    )
    
    parser.add_argument(
        'input',
        help='Input file path'
    )
    
    parser.add_argument(
        'output',
        help='Output file path'
    )
    
    parser.add_argument(
        '--from', '-f',
        dest='input_format',
        required=True,
        choices=['json', 'csv', 'xml', 'yaml'],
        help='Input file format'
    )
    
    parser.add_argument(
        '--to', '-t',
        dest='output_format',
        required=True,
        choices=['json', 'csv', 'xml', 'yaml'],
        help='Output file format'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='DPC Program Convertor 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Perform conversion
        convert_file(
            args.input,
            args.output,
            args.input_format,
            args.output_format
        )
        print(f"Successfully converted {args.input} to {args.output}")
        print(f"Format: {args.input_format.upper()} → {args.output_format.upper()}")
    except Exception as e:
        print(f"Error during conversion: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
