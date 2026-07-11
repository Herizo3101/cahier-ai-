from vectorstore import get_collection

collection = get_collection()
data = collection.get()

filenames = set(m["filename"] for m in data["metadatas"])
print(f"Nombre total de chunks indexés : {len(data['ids'])}")
print(f"Fichiers présents dans la base : {filenames}")