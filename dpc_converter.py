"""
DPC Program Converter

A tool to convert programs between different formats.
"""


class DPCConverter:
    """Main converter class for DPC programs."""
    
    def __init__(self):
        self.conversion_rules = {}
    
    def add_rule(self, source_format, target_format, conversion_func):
        """Add a conversion rule from source to target format."""
        key = (source_format, target_format)
        self.conversion_rules[key] = conversion_func
    
    def convert(self, program, source_format, target_format):
        """
        Convert a program from source format to target format.
        
        Args:
            program: The program to convert (string or dict)
            source_format: The source format identifier
            target_format: The target format identifier
            
        Returns:
            The converted program
            
        Raises:
            ValueError: If no conversion rule exists
        """
        key = (source_format, target_format)
        if key not in self.conversion_rules:
            raise ValueError(
                f"No conversion rule found from {source_format} to {target_format}"
            )
        
        conversion_func = self.conversion_rules[key]
        return conversion_func(program)


# Example conversion functions
def json_to_yaml(program):
    """Convert JSON format to YAML format."""
    import json
    import yaml
    
    if isinstance(program, str):
        program = json.loads(program)
    
    return yaml.dump(program, default_flow_style=False)


def yaml_to_json(program):
    """Convert YAML format to JSON format."""
    import json
    import yaml
    
    if isinstance(program, str):
        program = yaml.safe_load(program)
    
    return json.dumps(program, indent=2)


# Create a default converter instance
default_converter = DPCConverter()
default_converter.add_rule('json', 'yaml', json_to_yaml)
default_converter.add_rule('yaml', 'json', yaml_to_json)
