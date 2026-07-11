import sys
from ingestion import extract_document
from chunking import chunk_units

if len(sys.argv) < 2:
    print("Usage : python test_chunking.py chemin/vers/ton/fichier.pdf")
    sys.exit(1)

path = sys.argv[1]
units = extract_document(path)
chunks = chunk_units(units)

print(f"\n{'='*50}")
print(f"Unités extraites : {len(units)}")
print(f"Chunks produits  : {len(chunks)}")
print(f"{'='*50}\n")

for c in chunks[:5]:
    preview = c["text"][:100].replace("\n", " ")
    print(f"[{c['unit_type']} {c['unit_number']} · chunk {c['chunk_index']}] "
          f"({len(c['text'].split())} mots) {preview}...")