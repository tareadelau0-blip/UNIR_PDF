import os
from pypdf import PdfWriter

merger = PdfWriter()
# Busca todos los PDF excepto el resultado
files = sorted([f for f in os.listdir('.') if f.endswith('.pdf') and f != 'FINAL.pdf'])

for f in files:
    merger.append(f)

merger.write("FINAL.pdf")
merger.close()
