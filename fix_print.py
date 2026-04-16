import re, sys

with open('generate_pdfs.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    ('print(f"DONE: Dissertation PDF saved: {output_path}")', 'print("DONE: Dissertation PDF saved: " + output_path)'),
    ('print(f"\nALL DONE: All PDFs generated successfully!")', 'print("\\nAll PDFs generated successfully!")'),
    ('print(f"   Tool Doc:    {output_dir}/ACDRIP_Plus_Tool_Documentation.pdf")', 'print("   Tool Doc: " + output_dir + "/ACDRIP_Plus_Tool_Documentation.pdf")'),
    ('print(f"   Dissertation: {output_dir}/ACDRIP_Plus_Dissertation_80pages.pdf")', 'print("   Dissertation: " + output_dir + "/ACDRIP_Plus_Dissertation_80pages.pdf")'),
]
for old, new in replacements:
    content = content.replace(old, new)

with open('generate_pdfs.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed all emoji in print statements')
