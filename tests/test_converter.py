import os
import pytest
from md2html.converter import MarkdownConverter
import shutil

@pytest.fixture
def temp_converter(tmp_path):
    """Fixture to create a converter instance with temporary directory"""
    def _create_converter(input_file):
        return MarkdownConverter(str(input_file), str(tmp_path))
    return _create_converter

def test_basic_conversion(temp_converter, tmp_path):
    """Test basic markdown to HTML conversion"""
    # Create a test markdown file
    md_content = "# Test Heading\nThis is a test."
    md_file = tmp_path / "test.md"
    md_file.write_text(md_content)
    
    # Convert the file
    converter = temp_converter(md_file)
    output_file = converter.process_markdown()
    
    # Check if output file exists
    assert os.path.exists(output_file)
    
    # Check if content was converted properly
    with open(output_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
        assert "<h1>Test Heading</h1>" in html_content
        assert "This is a test." in html_content

def test_mermaid_conversion(temp_converter, tmp_path):
    """Test Mermaid diagram conversion"""
    # Create a test markdown file with mermaid diagram
    md_content = """# Test Mermaid
```mermaid
graph TD
    A[Start] --> B[End]
```
"""
    md_file = tmp_path / "test_mermaid.md"
    md_file.write_text(md_content)
    
    # Convert the file
    converter = temp_converter(md_file)
    output_file = converter.process_markdown()
    
    # Check if output file exists and contains SVG
    with open(output_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
        assert "<svg" in html_content
        assert 'class="mermaid-diagram"' in html_content

def test_frontmatter_handling(temp_converter, tmp_path):
    """Test handling of frontmatter in markdown files"""
    md_content = """---
title: Test Document
author: Test Author
---
# Content
This is the content."""
    
    md_file = tmp_path / "frontmatter_test.md"
    md_file.write_text(md_content)
    
    converter = temp_converter(md_file)
    output_file = converter.process_markdown()
    
    with open(output_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
        assert "<h1>Content</h1>" in html_content
        assert "This is the content." in html_content
        # Frontmatter should be removed
        assert "title: Test Document" not in html_content

def test_custom_output_directory(tmp_path):
    """Test custom output directory creation and usage"""
    custom_output = tmp_path / "custom_output"
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test")
    
    converter = MarkdownConverter(str(md_file), str(custom_output))
    output_file = converter.process_markdown()
    
    assert os.path.exists(custom_output)
    assert os.path.exists(output_file)
    assert str(custom_output) in str(output_file)

def test_invalid_input_file(temp_converter, tmp_path):
    """Test handling of non-existent input file"""
    non_existent_file = tmp_path / "does_not_exist.md"
    
    converter = temp_converter(non_existent_file)
    with pytest.raises(FileNotFoundError):
        converter.process_markdown()

def test_mermaid_cli_check(temp_converter, tmp_path, monkeypatch):
    """Test mermaid-cli availability check"""
    def mock_which(cmd):
        return None if cmd in ['mmdc', 'npm'] else '/usr/bin/something'
    
    monkeypatch.setattr(shutil, 'which', mock_which)
    
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test")
    
    with pytest.raises(SystemExit):
        converter = temp_converter(md_file)

def test_table_conversion(temp_converter, tmp_path):
    """Test markdown table conversion"""
    md_content = """# Table Test
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
"""
    
    md_file = tmp_path / "table_test.md"
    md_file.write_text(md_content)
    
    converter = temp_converter(md_file)
    output_file = converter.process_markdown()
    
    with open(output_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
        assert "<table>" in html_content
        assert "<th>Header 1</th>" in html_content
        assert "<td>Cell 1</td>" in html_content

def test_multiple_mermaid_diagrams(temp_converter, tmp_path):
    """Test handling of multiple Mermaid diagrams in one file"""
    md_content = """# Multiple Diagrams
```mermaid
graph TD
    A --> B
```

Some text in between

```mermaid
graph TD
    C --> D
```
"""
    
    md_file = tmp_path / "multiple_mermaid.md"
    md_file.write_text(md_content)
    
    converter = temp_converter(md_file)
    output_file = converter.process_markdown()
    
    with open(output_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
        # Should find multiple SVG elements
        svg_count = html_content.count("<svg")
        assert svg_count == 2
