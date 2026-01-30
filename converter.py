"""
DPC Program Convertor - A versatile data format converter
Converts between JSON, CSV, XML, and YAML formats
"""

import json
import csv
import yaml
from lxml import etree
from io import StringIO
from typing import Any, Dict, List, Union


class DataConverter:
    """Main converter class for handling different data formats"""
    
    def __init__(self):
        self.supported_formats = ['json', 'csv', 'xml', 'yaml']
    
    def convert(self, input_data: str, input_format: str, output_format: str) -> str:
        """
        Convert data from one format to another
        
        Args:
            input_data: The input data as a string
            input_format: The format of the input data (json, csv, xml, yaml)
            output_format: The desired output format (json, csv, xml, yaml)
            
        Returns:
            Converted data as a string
        """
        input_format = input_format.lower()
        output_format = output_format.lower()
        
        if input_format not in self.supported_formats:
            raise ValueError(f"Unsupported input format: {input_format}")
        if output_format not in self.supported_formats:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        # Parse input data
        parsed_data = self._parse(input_data, input_format)
        
        # Convert to output format
        output_data = self._serialize(parsed_data, output_format)
        
        return output_data
    
    def _parse(self, data: str, format_type: str) -> Union[Dict, List]:
        """Parse data from a specific format"""
        if format_type == 'json':
            return json.loads(data)
        elif format_type == 'csv':
            return self._parse_csv(data)
        elif format_type == 'xml':
            return self._parse_xml(data)
        elif format_type == 'yaml':
            return yaml.safe_load(data)
        else:
            raise ValueError(f"Unknown format: {format_type}")
    
    def _serialize(self, data: Union[Dict, List], format_type: str) -> str:
        """Serialize data to a specific format"""
        if format_type == 'json':
            return json.dumps(data, indent=2)
        elif format_type == 'csv':
            return self._serialize_csv(data)
        elif format_type == 'xml':
            return self._serialize_xml(data)
        elif format_type == 'yaml':
            return yaml.dump(data, default_flow_style=False, sort_keys=False)
        else:
            raise ValueError(f"Unknown format: {format_type}")
    
    def _parse_csv(self, data: str) -> List[Dict]:
        """Parse CSV data into a list of dictionaries"""
        reader = csv.DictReader(StringIO(data))
        return list(reader)
    
    def _serialize_csv(self, data: Union[Dict, List]) -> str:
        """Serialize data to CSV format"""
        if isinstance(data, dict):
            data = [data]
        
        if not data:
            return ""
        
        output = StringIO()
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()
    
    def _parse_xml(self, data: str) -> Union[Dict, List]:
        """Parse XML data into a dictionary or list"""
        root = etree.fromstring(data.encode('utf-8'))
        return self._xml_to_dict(root)
    
    def _xml_to_dict(self, element: etree._Element) -> Dict:
        """Convert XML element to dictionary"""
        result = {}
        
        # Handle attributes
        if element.attrib:
            result['@attributes'] = dict(element.attrib)
        
        # Handle text content
        if element.text and element.text.strip():
            if len(element) == 0:  # No children
                return element.text.strip()
            result['#text'] = element.text.strip()
        
        # Handle child elements
        children = {}
        for child in element:
            child_data = self._xml_to_dict(child)
            
            if child.tag in children:
                if not isinstance(children[child.tag], list):
                    children[child.tag] = [children[child.tag]]
                children[child.tag].append(child_data)
            else:
                children[child.tag] = child_data
        
        if children:
            result.update(children)
        
        # If result only has one key and it's not special, return the value
        if len(result) == 1 and list(result.keys())[0] not in ['@attributes', '#text']:
            return result[list(result.keys())[0]]
        
        return result if result else element.text
    
    def _serialize_xml(self, data: Union[Dict, List], root_tag: str = 'root') -> str:
        """Serialize data to XML format"""
        root = etree.Element(root_tag)
        self._dict_to_xml(data, root)
        return etree.tostring(root, pretty_print=True, encoding='unicode')
    
    def _dict_to_xml(self, data: Union[Dict, List, str, int, float, bool], parent):
        """
        Convert dictionary to XML elements (recursive)
        
        Args:
            data: The data to convert (dict, list, or primitive type)
            parent: The parent XML element to populate
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if key == '@attributes':
                    parent.attrib.update(value)
                elif key == '#text':
                    parent.text = str(value)
                else:
                    if isinstance(value, list):
                        for item in value:
                            child = etree.SubElement(parent, key)
                            self._dict_to_xml(item, child)
                    else:
                        child = etree.SubElement(parent, key)
                        self._dict_to_xml(value, child)
        elif isinstance(data, list):
            for item in data:
                child = etree.SubElement(parent, 'item')
                self._dict_to_xml(item, child)
        else:
            parent.text = str(data)


def convert_file(input_file: str, output_file: str, input_format: str, output_format: str):
    """
    Convert a file from one format to another
    
    Args:
        input_file: Path to the input file
        output_file: Path to the output file
        input_format: Format of the input file
        output_format: Desired format for the output file
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        input_data = f.read()
    
    converter = DataConverter()
    output_data = converter.convert(input_data, input_format, output_format)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_data)


if __name__ == '__main__':
    # Example usage
    converter = DataConverter()
    
    # Example JSON to CSV conversion
    json_data = '{"name": "John", "age": 30, "city": "New York"}'
    csv_output = converter.convert(json_data, 'json', 'csv')
    print("JSON to CSV:")
    print(csv_output)
    
    # Example CSV to JSON conversion
    csv_data = "name,age,city\nJohn,30,New York\nJane,25,Boston"
    json_output = converter.convert(csv_data, 'csv', 'json')
    print("\nCSV to JSON:")
    print(json_output)
