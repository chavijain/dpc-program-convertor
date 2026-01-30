# DPC Program Converter

A flexible tool for converting programs between different formats.

## Features

- Extensible conversion framework
- Built-in support for JSON ↔ YAML conversion
- Easy to add custom conversion rules
- Comprehensive testing tool

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Using the Converter

```python
from dpc_converter import DPCConverter, default_converter

# Use the default converter with built-in rules
json_data = '{"name": "example", "value": 42}'
yaml_output = default_converter.convert(json_data, 'json', 'yaml')
print(yaml_output)

# Create a custom converter with your own rules
converter = DPCConverter()

def my_conversion(program):
    # Your conversion logic here
    return program.upper()

converter.add_rule('lowercase', 'uppercase', my_conversion)
result = converter.convert('hello', 'lowercase', 'uppercase')
```

### Running Tests

The testing tool provides a comprehensive test suite for the converter:

```bash
# Run all tests
python test_tool.py

# Run tests with verbose output
python test_tool.py --verbose
```

The testing tool includes:
- Unit tests for core converter functionality
- Integration tests for format conversions
- Assertion utilities for custom tests
- Detailed test reporting

## Testing Tool Features

The `test_tool.py` provides:

- **Test Runner**: Automatically discovers and runs tests
- **Assertion Utilities**: `assert_equal`, `assert_true`, `assert_false`, `assert_raises`
- **Test Results**: Detailed pass/fail reporting with timing
- **Verbose Mode**: Optional detailed output for debugging

## Adding Custom Tests

You can extend the testing tool with your own tests:

```python
from test_tool import TestRunner, assert_equal

runner = TestRunner()

def my_custom_test():
    result = some_function()
    assert_equal(result, expected_value)

runner.add_test("My Custom Test", my_custom_test)
runner.run_all(verbose=True)
```

## Project Structure

```
dpc-program-convertor/
├── README.md           # This file
├── dpc_converter.py    # Main converter module
├── test_tool.py        # Testing tool
└── requirements.txt    # Python dependencies
```

## License

MIT
