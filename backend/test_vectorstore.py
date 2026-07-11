import sys
from ingestion import extract_document
from chunking import chunk_units
from vectorstore import index_chunks, search

if len(sys.argv) < 2:
    print("Usage : python test_vectorstore.py chemin/vers/ton/fichier.pdf")
    sys.exit(1)

path = sys.argv[1]

print("Extraction...")
units = extract_document(path)

print("Chunking...")
chunks = chunk_units(units)

print(f"Indexation de {len(chunks)} chunks (ça peut prendre quelques secondes)...")
n = index_chunks(chunks)
print(f"{n} chunks indexés dans ChromaDB.\n")

question = input("Pose une question sur ce document : ")
results = search(question, top_k=3)

print(f"\n--- Top {len(results)} résultats ---")
for r in results:
    preview = r["text"][:150].replace("\n", " ")
    print(f"\n[{r['filename']} · {r['unit_type']} {r['unit_number']}]")
    print(preview + "...")