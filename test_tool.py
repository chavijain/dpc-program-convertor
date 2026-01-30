#!/usr/bin/env python3
"""
DPC Testing Tool

A comprehensive testing tool for DPC program converter.
Provides test discovery, execution, and reporting capabilities.
"""

import sys
import os
import time
import traceback
from typing import List, Callable, Dict, Any, Tuple


class TestResult:
    """Stores the result of a test execution."""
    
    def __init__(self, test_name: str, passed: bool, error: str = None, duration: float = 0):
        self.test_name = test_name
        self.passed = passed
        self.error = error
        self.duration = duration


class TestRunner:
    """Main test runner for DPC converter tests."""
    
    def __init__(self):
        self.tests: List[Tuple[str, Callable]] = []
        self.results: List[TestResult] = []
        self.verbose = False
    
    def add_test(self, name: str, test_func: Callable):
        """Register a test function."""
        self.tests.append((name, test_func))
    
    def run_test(self, name: str, test_func: Callable) -> TestResult:
        """Run a single test and capture the result."""
        if self.verbose:
            print(f"  Running: {name}...", end=" ")
        
        start_time = time.time()
        try:
            test_func()
            duration = time.time() - start_time
            result = TestResult(name, True, duration=duration)
            if self.verbose:
                print(f"✓ PASSED ({duration:.3f}s)")
            return result
        except AssertionError as e:
            duration = time.time() - start_time
            error_msg = str(e) if str(e) else "Assertion failed"
            result = TestResult(name, False, error_msg, duration)
            if self.verbose:
                print(f"✗ FAILED ({duration:.3f}s)")
                print(f"    Error: {error_msg}")
            return result
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"{type(e).__name__}: {str(e)}"
            result = TestResult(name, False, error_msg, duration)
            if self.verbose:
                print(f"✗ ERROR ({duration:.3f}s)")
                print(f"    {error_msg}")
                if self.verbose:
                    traceback.print_exc()
            return result
    
    def run_all(self, verbose: bool = False) -> bool:
        """
        Run all registered tests.
        
        Args:
            verbose: Print detailed test execution information
            
        Returns:
            True if all tests passed, False otherwise
        """
        self.verbose = verbose
        self.results = []
        
        if not self.tests:
            print("No tests found!")
            return False
        
        print(f"\nRunning {len(self.tests)} tests...\n")
        
        for name, test_func in self.tests:
            result = self.run_test(name, test_func)
            self.results.append(result)
        
        return self.print_summary()
    
    def print_summary(self) -> bool:
        """Print test results summary."""
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        total_duration = sum(r.duration for r in self.results)
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests: {len(self.results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Duration: {total_duration:.3f}s")
        print("=" * 60)
        
        if failed > 0:
            print("\nFailed tests:")
            for result in self.results:
                if not result.passed:
                    print(f"  ✗ {result.test_name}")
                    print(f"    {result.error}")
        
        all_passed = failed == 0
        if all_passed:
            print("\n✓ All tests passed!")
        else:
            print(f"\n✗ {failed} test(s) failed")
        
        print()
        return all_passed


def assert_equal(actual, expected, message=None):
    """Assert that two values are equal."""
    if actual != expected:
        msg = message or f"Expected {expected}, but got {actual}"
        raise AssertionError(msg)


def assert_true(condition, message=None):
    """Assert that a condition is true."""
    if not condition:
        msg = message or "Condition is not true"
        raise AssertionError(msg)


def assert_false(condition, message=None):
    """Assert that a condition is false."""
    if condition:
        msg = message or "Condition is not false"
        raise AssertionError(msg)


def assert_raises(exception_class, callable_func, *args, **kwargs):
    """Assert that calling a function raises a specific exception."""
    try:
        callable_func(*args, **kwargs)
        raise AssertionError(f"Expected {exception_class.__name__} to be raised")
    except exception_class:
        pass  # Expected exception was raised


def main():
    """Main entry point for the testing tool."""
    # Import the converter
    try:
        from dpc_converter import DPCConverter, default_converter
    except ImportError:
        print("Error: Could not import dpc_converter module")
        sys.exit(1)
    
    # Create test runner
    runner = TestRunner()
    
    # Register tests
    def test_converter_initialization():
        """Test that converter initializes correctly."""
        converter = DPCConverter()
        assert_true(isinstance(converter.conversion_rules, dict))
        assert_equal(len(converter.conversion_rules), 0)
    
    def test_add_conversion_rule():
        """Test adding a conversion rule."""
        converter = DPCConverter()
        
        def dummy_converter(x):
            return x.upper()
        
        converter.add_rule('a', 'b', dummy_converter)
        assert_equal(len(converter.conversion_rules), 1)
        assert_true(('a', 'b') in converter.conversion_rules)
    
    def test_convert_with_valid_rule():
        """Test conversion with a valid rule."""
        converter = DPCConverter()
        
        def double(x):
            return x * 2
        
        converter.add_rule('num', 'doubled', double)
        result = converter.convert(5, 'num', 'doubled')
        assert_equal(result, 10)
    
    def test_convert_without_rule():
        """Test that conversion without rule raises error."""
        converter = DPCConverter()
        
        def test_func():
            converter.convert("test", 'a', 'b')
        
        assert_raises(ValueError, test_func)
    
    def test_json_to_yaml_conversion():
        """Test JSON to YAML conversion."""
        import json
        
        data = {"name": "test", "value": 123}
        json_str = json.dumps(data)
        
        result = default_converter.convert(json_str, 'json', 'yaml')
        assert_true(isinstance(result, str))
        assert_true('name: test' in result)
        assert_true('value: 123' in result)
    
    def test_yaml_to_json_conversion():
        """Test YAML to JSON conversion."""
        import json
        
        yaml_str = "name: test\nvalue: 123\n"
        
        result = default_converter.convert(yaml_str, 'yaml', 'json')
        assert_true(isinstance(result, str))
        
        # Parse result to verify it's valid JSON
        parsed = json.loads(result)
        assert_equal(parsed['name'], 'test')
        assert_equal(parsed['value'], 123)
    
    def test_round_trip_conversion():
        """Test that converting JSON->YAML->JSON preserves data."""
        import json
        
        original_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        json_str = json.dumps(original_data)
        
        # Convert JSON to YAML
        yaml_result = default_converter.convert(json_str, 'json', 'yaml')
        
        # Convert back to JSON
        json_result = default_converter.convert(yaml_result, 'yaml', 'json')
        
        # Parse and compare
        final_data = json.loads(json_result)
        assert_equal(final_data, original_data)
    
    # Register all tests
    runner.add_test("Converter Initialization", test_converter_initialization)
    runner.add_test("Add Conversion Rule", test_add_conversion_rule)
    runner.add_test("Convert with Valid Rule", test_convert_with_valid_rule)
    runner.add_test("Convert without Rule (Error)", test_convert_without_rule)
    runner.add_test("JSON to YAML Conversion", test_json_to_yaml_conversion)
    runner.add_test("YAML to JSON Conversion", test_yaml_to_json_conversion)
    runner.add_test("Round-trip Conversion", test_round_trip_conversion)
    
    # Run tests with verbose output
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    success = runner.run_all(verbose=verbose)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
