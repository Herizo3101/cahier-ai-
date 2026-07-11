def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Découpe un texte en morceaux de `chunk_size` mots, avec `overlap`
    mots de chevauchement entre deux morceaux consécutifs.
    """
    words = text.split()

    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))

        if end >= len(words):
            break
        start = end - overlap  # recule pour créer le chevauchement

    return chunks


def chunk_units(units: list[dict], chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """
    Prend la liste d'unités (pages/slides/blocs) et produit la liste
    finale de chunks prête pour l'embedding.
    """
    all_chunks = []

    for unit in units:
        pieces = chunk_text(unit["text"], chunk_size=chunk_size, overlap=overlap)

        for i, piece in enumerate(pieces):
            all_chunks.append({
                "filename": unit["filename"],
                "unit_type": unit["unit_type"],
                "unit_number": unit["unit_number"],
                "chunk_index": i,
                "text": piece,
            })

    return all_chunks