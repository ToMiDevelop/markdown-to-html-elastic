import markdown
import frontmatter
import os
import subprocess
import tempfile
import re
from pathlib import Path
import shutil
import sys

class MarkdownConverter:
    def __init__(self, input_file, output_dir="output"):
        self.input_file = input_file
        self.output_dir = output_dir
        self.mermaid_counter = 0
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Check mermaid-cli without attempting installation
        if not shutil.which('mmdc'):
            print("mermaid-cli not found. Please install it using: npm install -g @mermaid-js/mermaid-cli")
            sys.exit(1)

    def convert_mermaid_to_svg(self, mermaid_code):
        """Convert Mermaid diagram code to SVG using mermaid-cli and return SVG content"""
        # Create a temporary file for the Mermaid code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as temp_file:
            temp_file.write(mermaid_code)
            temp_file_path = temp_file.name

        # Create a temporary file for the SVG output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as svg_temp_file:
            svg_temp_path = svg_temp_file.name

        try:
            # Run mmdc (mermaid-cli) to convert the diagram with increased timeout
            subprocess.run([
                'mmdc',
                '-i', temp_file_path,
                '-o', svg_temp_path,
                '-b', 'transparent'
            ], check=True, timeout=60)  # Increase to 60 seconds
            
            # Read the SVG content
            with open(svg_temp_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            return svg_content
        except subprocess.TimeoutExpired:
            print("Error: Mermaid diagram generation timed out")
            return f'<div class="error">Error generating diagram: timeout</div>'
        except subprocess.CalledProcessError as e:
            print(f"Error generating Mermaid diagram: {e}")
            return f'<div class="error">Error generating diagram: {e}</div>'
        finally:
            # Clean up temporary files
            os.unlink(temp_file_path)
            os.unlink(svg_temp_path)

    def process_markdown(self):
        # Read the markdown file
        with open(self.input_file, 'r', encoding='utf-8') as f:
            # Parse frontmatter if exists
            post = frontmatter.load(f)
            content = post.content

        # First pass: Extract and convert Mermaid diagrams
        mermaid_blocks = {}
        def replace_mermaid(match):
            mermaid_code = match.group(1)
            svg_content = self.convert_mermaid_to_svg(mermaid_code)
            placeholder = f"MERMAID_PLACEHOLDER_{len(mermaid_blocks)}"
            mermaid_blocks[placeholder] = svg_content
            return placeholder

        content = re.sub(
            r'```mermaid\n(.*?)\n```',
            replace_mermaid,
            content,
            flags=re.DOTALL
        )

        # Convert markdown to HTML
        html = markdown.markdown(
            content,
            extensions=[
                'fenced_code',
                'tables',
                'nl2br',
                'pymdownx.superfences',
                'pymdownx.highlight',
                'codehilite'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True,
                    'noclasses': False
                }
            }
        )

        # Replace Mermaid placeholders with SVG content
        for placeholder, svg_content in mermaid_blocks.items():
            html = html.replace(
                placeholder,
                f'<div class="mermaid-diagram">{svg_content}</div>'
            )

        # Add CSS styling
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .mermaid-diagram {{
            max-width: 100%;
            margin: 20px 0;
        }}
        .mermaid-diagram svg {{
            max-width: 100%;
            height: auto;
        }}
        pre {{
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 1em 0;
        }}
        code {{
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.9em;
        }}
        .language-python {{
            color: #333;
        }}
        .highlight {{
            background: #f8f8f8;
        }}
    </style>
</head>
<body>
    {html}
</body>
</html>
"""

        # Write the HTML file
        output_file = os.path.join(
            self.output_dir,
            os.path.splitext(os.path.basename(self.input_file))[0] + '.html'
        )
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        return output_file

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert Markdown to HTML with Mermaid support')
    parser.add_argument('input_file', help='Input markdown file')
    parser.add_argument('--output-dir', default='output', help='Output directory')
    
    args = parser.parse_args()
    
    try:
        converter = MarkdownConverter(args.input_file, args.output_dir)
        output_file = converter.process_markdown()
        print(f"Successfully converted file to: {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()