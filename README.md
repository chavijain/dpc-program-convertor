# DPC Program Convertor

A versatile data format converter that seamlessly converts between JSON, CSV, XML, and YAML formats.

## Features

- 🔄 Convert between multiple data formats:
  - JSON ↔ CSV
  - JSON ↔ XML
  - JSON ↔ YAML
  - CSV ↔ XML
  - CSV ↔ YAML
  - XML ↔ YAML
- 🚀 Simple command-line interface
- 🐍 Python library for programmatic use
- 📦 Handles complex nested structures
- ✅ Comprehensive error handling
- 🧪 Well-tested with unit tests

## Installation

1. Clone the repository:
```bash
git clone https://github.com/chavijain/dpc-program-convertor.git
cd dpc-program-convertor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Basic syntax:
```bash
python dpc_cli.py INPUT_FILE OUTPUT_FILE --from INPUT_FORMAT --to OUTPUT_FORMAT
```

#### Examples

Convert JSON to CSV:
```bash
python dpc_cli.py examples/sample.json output.csv --from json --to csv
```

Convert CSV to YAML:
```bash
python dpc_cli.py examples/sample.csv output.yaml --from csv --to yaml
```

Convert XML to JSON:
```bash
python dpc_cli.py examples/sample.xml output.json --from xml --to json
```

Convert YAML to XML:
```bash
python dpc_cli.py examples/sample.yaml output.xml --from yaml --to xml
```

### Python Library

You can also use the converter programmatically in your Python code:

```python
from converter import DataConverter

# Create a converter instance
converter = DataConverter()

# Convert JSON to CSV
json_data = '{"name": "John", "age": 30}'
csv_output = converter.convert(json_data, 'json', 'csv')
print(csv_output)

# Convert CSV to JSON
csv_data = "name,age\nJohn,30\nJane,25"
json_output = converter.convert(csv_data, 'csv', 'json')
print(json_output)

# Convert files
from converter import convert_file
convert_file('input.json', 'output.yaml', 'json', 'yaml')
```

## Supported Formats

| Format | Read | Write | Notes |
|--------|------|-------|-------|
| JSON   | ✅   | ✅    | Full support for nested structures |
| CSV    | ✅   | ✅    | Flat structures with headers |
| XML    | ✅   | ✅    | Full support with attributes |
| YAML   | ✅   | ✅    | Full support for nested structures |

## Examples

Example files are provided in the `examples/` directory:
- `sample.json` - JSON format example
- `sample.csv` - CSV format example
- `sample.xml` - XML format example
- `sample.yaml` - YAML format example

## Testing

Run the test suite:
```bash
python -m pytest tests/test_converter.py -v
```

Or using unittest:
```bash
python -m unittest tests/test_converter.py
```

## Project Structure

```
dpc-program-convertor/
├── converter.py          # Core converter module
├── dpc_cli.py           # Command-line interface
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── examples/           # Example data files
│   ├── sample.json
│   ├── sample.csv
│   ├── sample.xml
│   └── sample.yaml
└── tests/              # Unit tests
    └── test_converter.py
```

## Requirements

- Python 3.7 or higher
- PyYAML >= 6.0.0
- lxml >= 5.0.0

## Error Handling

The converter includes comprehensive error handling:
- Invalid file paths
- Unsupported formats
- Malformed data
- Empty files

All errors are reported with clear, actionable messages.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Author

Created by chavijain
