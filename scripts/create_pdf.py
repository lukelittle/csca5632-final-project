#!/usr/bin/env python3

import os
import glob
import nbformat
from nbconvert import PDFExporter
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
            # Ensure all code cells have outputs property
            for cell in nb.cells:
                if cell.cell_type == 'code' and 'outputs' not in cell:
                    cell['outputs'] = []
            if merged is None:
                merged = nb
            else:
                # Add a markdown cell with the notebook name
                header_cell = nbformat.v4.new_markdown_cell(source=f"\n\n# {os.path.basename(fname)}\n")
                merged.cells.append(header_cell)
                # Append cells from the current notebook
                merged.cells.extend(nb.cells)
    return merged

def convert_to_pdf(notebook):
    """Convert notebook to PDF."""
    # Configure the PDF exporter
    c = Config()
    c.PDFExporter.exclude_input_prompt = True
    c.PDFExporter.exclude_output_prompt = True
    
    # Create PDF exporter
    pdf_exporter = PDFExporter(config=c)
    
    # Convert to PDF
    pdf_data, _ = pdf_exporter.from_notebook_node(notebook)
    return pdf_data

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
    
    # Convert to PDF
    print("Converting to PDF...")
    pdf_data = convert_to_pdf(merged_notebook)
    
    # Save PDF
    output_file = 'nba_pattern_analysis.pdf'
    print(f"Saving {output_file}...")
    with open(output_file, 'wb') as f:
        f.write(pdf_data)
    
    print("Done! PDF has been created.")

if __name__ == '__main__':
    main()
