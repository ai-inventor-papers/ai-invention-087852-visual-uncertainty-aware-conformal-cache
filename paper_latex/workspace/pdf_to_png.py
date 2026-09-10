#!/usr/bin/env python3
"""Convert PDF pages to PNG at 150 DPI for visual review."""
import fitz  # pymupdf
import os

pdf_path = "paper.pdf"
output_dir = "page_images"
os.makedirs(output_dir, exist_ok=True)

doc = fitz.open(pdf_path)
print(f"Total pages: {len(doc)}")

zoom = 150 / 72  # 150 DPI
mat = fitz.Matrix(zoom, zoom)

for i, page in enumerate(doc):
    pix = page.get_pixmap(matrix=mat)
    out_path = os.path.join(output_dir, f"page_{i+1:02d}.png")
    pix.save(out_path)
    print(f"Saved {out_path} ({pix.width}x{pix.height})")

doc.close()
print("Done.")
