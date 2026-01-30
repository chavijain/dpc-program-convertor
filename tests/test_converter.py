"""
Unit tests for the DPC Program Convertor
"""

import unittest
import json
import yaml
from converter import DataConverter


class TestDataConverter(unittest.TestCase):
    """Test cases for DataConverter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.converter = DataConverter()
        
    def test_json_to_csv(self):
        """Test JSON to CSV conversion"""
        json_data = '[{"name": "John", "age": "30"}, {"name": "Jane", "age": "25"}]'
        result = self.converter.convert(json_data, 'json', 'csv')
        self.assertIn('name,age', result)
        self.assertIn('John,30', result)
        self.assertIn('Jane,25', result)
    
    def test_csv_to_json(self):
        """Test CSV to JSON conversion"""
        csv_data = "name,age\nJohn,30\nJane,25"
        result = self.converter.convert(csv_data, 'csv', 'json')
        data = json.loads(result)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'John')
        self.assertEqual(data[1]['name'], 'Jane')
    
    def test_json_to_yaml(self):
        """Test JSON to YAML conversion"""
        json_data = '{"name": "John", "age": 30, "skills": ["Python", "JavaScript"]}'
        result = self.converter.convert(json_data, 'json', 'yaml')
        data = yaml.safe_load(result)
        self.assertEqual(data['name'], 'John')
        self.assertEqual(data['age'], 30)
        self.assertEqual(len(data['skills']), 2)
    
    def test_yaml_to_json(self):
        """Test YAML to JSON conversion"""
        yaml_data = """
        name: John
        age: 30
        skills:
          - Python
          - JavaScript
        """
        result = self.converter.convert(yaml_data, 'yaml', 'json')
        data = json.loads(result)
        self.assertEqual(data['name'], 'John')
        self.assertEqual(data['age'], 30)
    
    def test_xml_to_json(self):
        """Test XML to JSON conversion"""
        xml_data = """
        <person>
            <name>John</name>
            <age>30</age>
        </person>
        """
        result = self.converter.convert(xml_data, 'xml', 'json')
        data = json.loads(result)
        self.assertIn('name', data)
        self.assertIn('age', data)
    
    def test_json_to_xml(self):
        """Test JSON to XML conversion"""
        json_data = '{"person": {"name": "John", "age": "30"}}'
        result = self.converter.convert(json_data, 'json', 'xml')
        self.assertIn('<root>', result)
        self.assertIn('<person>', result)
        self.assertIn('<name>John</name>', result)
        self.assertIn('<age>30</age>', result)
    
    def test_unsupported_input_format(self):
        """Test error handling for unsupported input format"""
        with self.assertRaises(ValueError):
            self.converter.convert('test', 'txt', 'json')
    
    def test_unsupported_output_format(self):
        """Test error handling for unsupported output format"""
        with self.assertRaises(ValueError):
            self.converter.convert('{"test": "data"}', 'json', 'pdf')
    
    def test_invalid_json(self):
        """Test error handling for invalid JSON"""
        with self.assertRaises(json.JSONDecodeError):
            self.converter.convert('invalid json', 'json', 'csv')
    
    def test_empty_csv(self):
        """Test CSV to JSON conversion with empty data"""
        csv_data = "name,age"
        result = self.converter.convert(csv_data, 'csv', 'json')
        data = json.loads(result)
        self.assertEqual(len(data), 0)
    
    def test_supported_formats(self):
        """Test that all expected formats are supported"""
        expected_formats = ['json', 'csv', 'xml', 'yaml']
        self.assertEqual(self.converter.supported_formats, expected_formats)


class TestConversions(unittest.TestCase):
    """Integration tests for various conversion scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.converter = DataConverter()
    
    def test_round_trip_json_yaml_json(self):
        """Test round-trip conversion: JSON -> YAML -> JSON"""
        original = '{"name": "Test", "value": 42}'
        yaml_result = self.converter.convert(original, 'json', 'yaml')
        final = self.converter.convert(yaml_result, 'yaml', 'json')
        
        original_data = json.loads(original)
        final_data = json.loads(final)
        self.assertEqual(original_data, final_data)
    
    def test_complex_nested_structure(self):
        """Test conversion of complex nested structures"""
        complex_json = '''
        {
            "company": {
                "name": "TechCorp",
                "departments": [
                    {"name": "Engineering", "count": 50},
                    {"name": "Sales", "count": 30}
                ]
            }
        }
        '''
        yaml_result = self.converter.convert(complex_json, 'json', 'yaml')
        json_result = self.converter.convert(yaml_result, 'yaml', 'json')
        
        original_data = json.loads(complex_json)
        final_data = json.loads(json_result)
        self.assertEqual(original_data['company']['name'], final_data['company']['name'])


if __name__ == '__main__':
    unittest.main()
