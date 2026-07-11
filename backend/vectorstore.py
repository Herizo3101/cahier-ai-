import ollama
import chromadb

CHROMA_PATH = "../data/chroma_db"
COLLECTION_NAME = "cours"
EMBED_MODEL = "nomic-embed-text"


def get_client():
    """Client ChromaDB avec stockage persistant sur disque."""
    return chromadb.PersistentClient(path=CHROMA_PATH)


def get_collection():
    """Récupère (ou crée) la collection unique où sont stockés tous les cours."""
    client = get_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)


def embed_text(text: str) -> list[float]:
    """Transforme un texte en vecteur via Ollama."""
    response = ollama.embed(model=EMBED_MODEL, input=text)
    return response["embeddings"][0]


def index_chunks(chunks: list[dict]):
    """
    Prend la liste de chunks (sortie de chunking.chunk_units) et les
    indexe dans ChromaDB : embedding + texte + métadonnées.
    """
    collection = get_collection()

    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for chunk in chunks:
        # ID unique et stable pour chaque chunk
        chunk_id = f"{chunk['filename']}_{chunk['unit_number']}_{chunk['chunk_index']}"

        ids.append(chunk_id)
        embeddings.append(embed_text(chunk["text"]))
        documents.append(chunk["text"])
        metadatas.append({
            "filename": chunk["filename"],
            "unit_type": chunk["unit_type"],
            "unit_number": chunk["unit_number"],
        })

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    return len(ids)


def search(question: str, top_k: int = 4) -> list[dict]:
    """
    Cherche les `top_k` chunks les plus proches sémantiquement de la question.
    Retourne une liste de dicts avec le texte et les métadonnées.
    """
    collection = get_collection()
    question_embedding = embed_text(question)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
    )

    hits = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        hits.append({
            "text": doc,
            "filename": meta["filename"],
            "unit_type": meta["unit_type"],
            "unit_number": meta["unit_number"],
        })

    return hits

def list_indexed_documents() -> list[dict]:
    """
    Retourne la liste des documents réellement présents dans ChromaDB,
    pour synchroniser l'affichage de la bibliothèque avec la réalité.
    """
    collection = get_collection()
    data = collection.get(include=["metadatas"])

    seen = {}
    for meta in data["metadatas"]:
        fname = meta["filename"]
        if fname not in seen:
            seen[fname] = {
                "name": fname,
                "ext": fname.split(".")[-1].lower(),
                "status": "ready",
            }
    return list(seen.values())

def delete_document(filename: str):
    """Supprime tous les chunks appartenant à un document précis."""
    collection = get_collection()
    collection.delete(where={"filename": filename})