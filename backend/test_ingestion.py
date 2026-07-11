"""
Test du module d'extraction avec un vrai fichier.
"""

import sys
from ingestion import extract_document

if len(sys.argv) < 2:
    print("Usage : python test_ingestion.py chemin/vers/ton/fichier.pdf")
    sys.exit(1)

path = sys.argv[1]
units = extract_document(path)

print(f"\n{'='*50}")
print(f"Fichier : {path}")
print(f"Nombre d'unités extraites : {len(units)}")
print(f"{'='*50}\n")

if not units:
    print("⚠️  Aucun texte extrait — le fichier est peut-être un PDF scanné (image) ou vide.")
else:
    # Affiche la première unité en entier
    print("--- Première unité ---")
    print(f"Type : {units[0]['unit_type']} | Numéro : {units[0]['unit_number']}")
    print(f"Texte ({len(units[0]['text'])} caractères) :\n")
    print(units[0]['text'][:500])
    print("...\n" if len(units[0]['text']) > 500 else "\n")

    # Affiche juste un aperçu des autres
    print("--- Aperçu des unités suivantes ---")
    for u in units[1:5]:
        preview = u['text'][:80].replace("\n", " ")
        print(f"[{u['unit_type']} {u['unit_number']}] {preview}...")