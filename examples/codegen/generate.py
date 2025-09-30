#!/usr/bin/env python3
"""
Code generator using Jinja2 templates

Usage: generate.py <language> <config_file> <template_file> <output_file>
"""

import sys
import yaml
import os
from datetime import datetime

# Simple template engine (replace with Jinja2 in real projects)


def simple_template_render(template_content, data):
    """Very basic template rendering - use Jinja2 for real projects"""
    result = template_content

    # Replace simple variables with filters
    import re

    # Handle variables with filters like {{ variable | filter }}
    pattern = r'\{\{\s*([^}]+?)\s*\|\s*(\w+)\s*\}\}'

    def replace_with_filter(match):
        var_path = match.group(1).strip()
        filter_name = match.group(2).strip()

        # Navigate through nested variables
        value = data
        for part in var_path.split('.'):
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return match.group(0)  # Return original if not found

        # Apply filter
        if filter_name == 'lower':
            if isinstance(value, bool):
                value = str(value).lower()
            else:
                value = str(value).lower()
        elif filter_name == 'upper':
            value = str(value).upper()

        return str(value)

    result = re.sub(pattern, replace_with_filter, result)

    # Replace simple variables without filters
    for key, value in data.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                # Only replace if not already handled by filter
                simple_pattern = f"{{{{ {key}.{subkey} }}}}"
                if simple_pattern in result:
                    result = result.replace(simple_pattern, str(subvalue))
        else:
            simple_pattern = f"{{{{ {key} }}}}"
            if simple_pattern in result:
                result = result.replace(simple_pattern, str(value))

    # Handle loops (very basic)
    if "{% for" in result:
        lines = result.split('\n')
        output_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if "{% for" in line and "in" in line:
                # Extract loop variable and collection
                for_part = line.strip().split()
                var_name = for_part[2]
                collection_name = for_part[4].rstrip(" %}")

                # Find end of loop
                loop_content = []
                i += 1
                while i < len(lines) and "{% endfor %}" not in lines[i]:
                    loop_content.append(lines[i])
                    i += 1

                # Render loop
                if collection_name in data:
                    for item in data[collection_name]:
                        for loop_line in loop_content:
                            rendered_line = loop_line
                            if isinstance(item, dict):
                                for key, value in item.items():
                                    rendered_line = rendered_line.replace(
                                        f"{{{{ {var_name}.{key} }}}}", str(value))
                            else:
                                rendered_line = rendered_line.replace(
                                    f"{{{{ {var_name} }}}}", str(item))
                            output_lines.append(rendered_line)
            else:
                output_lines.append(line)
            i += 1
        result = '\n'.join(output_lines)

    return result


def main():
    if len(sys.argv) != 5:
        print("Usage: generate.py <language> <config_file> <template_file> <output_file>")
        sys.exit(1)

    language = sys.argv[1]
    config_file = sys.argv[2]
    template_file = sys.argv[3]
    output_file = sys.argv[4]

    # Load configuration
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # Load template
    with open(template_file, 'r') as f:
        template = f.read()

    # Add generation metadata
    config['generation'] = {
        'timestamp': datetime.now().isoformat(),
        'language': language,
        'generator': 'Bazel Python Generator'
    }

    # Render template
    rendered = simple_template_render(template, config)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write output
    with open(output_file, 'w') as f:
        f.write(rendered)

    print(f"Generated {output_file} from {template_file}")


if __name__ == "__main__":
    main()
