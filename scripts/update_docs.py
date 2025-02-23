#!/usr/bin/env python3

import os
import glob
import nbformat
from nbconvert import HTMLExporter
from traitlets.config import Config

def get_notebooks_in_order():
    """Get all notebooks sorted by their numeric prefix."""
    notebooks = glob.glob("notebooks/[0-9]*.ipynb")
    return sorted(notebooks)

def merge_notebooks(notebook_files):
    """Merge multiple notebooks into one."""
    merged = None
    for fname in notebook_files:
        with open(fname, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
            if merged is None:
                merged = nb
            else:
                # Append cells from the current notebook
                merged.cells.extend(nb.cells)
    return merged

def convert_to_html(notebook):
    """Convert notebook to HTML with a custom template."""
    # Configure the HTML exporter to embed images
    c = Config()
    c.HTMLExporter.embed_images = True
    
    # Configure the HTML template
    html_exporter = HTMLExporter(config=c)
    html_exporter.template_name = 'classic'
    
    # Convert to HTML
    body, _ = html_exporter.from_notebook_node(notebook)
    
    # Add custom styling
    with open('docs/styles.css', 'r', encoding='utf-8') as f:
        custom_css = f.read()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>NBA Pattern Analysis</title>
        <style>
            {custom_css}
        </style>
        <style>
            /* Additional styles for notebook outputs */
            .output_png img, .output_jpeg img {{
                max-width: 100%;
                height: auto;
            }}
            .cell {{
                margin: 20px 0;
                border: 1px solid #eee;
                padding: 10px;
                border-radius: 4px;
            }}
            .input, .output {{
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        {body}
    </body>
    </html>
    """
    return html

def main():
    # Get notebooks in order
    notebooks = get_notebooks_in_order()
    if not notebooks:
        print("No notebooks found!")
        return
    
    print(f"Found {len(notebooks)} notebooks to merge:")
    for nb in notebooks:
        print(f"  - {nb}")
    
    # Merge notebooks
    print("\nMerging notebooks...")
    merged_notebook = merge_notebooks(notebooks)
    
    # Convert to HTML
    print("Converting to HTML...")
    html_content = convert_to_html(merged_notebook)
    
    # Update docs/index.html
    print("Updating docs/index.html...")
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Done! Documentation has been updated.")

if __name__ == '__main__':
    main()
