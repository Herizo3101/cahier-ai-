import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError, ClientError

from vectorstore import search

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
GEN_MODEL = "gemini-2.5-flash-lite"

SYSTEM_PROMPT = """Tu es un assistant pédagogique qui aide un étudiant à réviser ses cours.

Règles :
- Réponds UNIQUEMENT à partir des extraits de cours fournis ci-dessous.
- Si les extraits ne contiennent pas la réponse, dis clairement que l'information
  n'est pas présente dans les cours importés, ne l'invente pas.
- Réponds en français, de façon claire et pédagogique, comme si tu expliquais
  à un camarade de classe.
- Reste concis mais complet."""


def build_prompt(question: str, chunks: list[dict]) -> str:
    """Construit le prompt augmenté avec le contexte récupéré."""
    context = "\n\n---\n\n".join(
        f"[Source : {c['filename']}, {c['unit_type']} {c['unit_number']}]\n{c['text']}"
        for c in chunks
    )

    return f"""{SYSTEM_PROMPT}

EXTRAITS DE COURS :
{context}

QUESTION DE L'ÉTUDIANT :
{question}

RÉPONSE :"""


def ask(question: str, top_k: int = 4) -> dict:
    """
    Point d'entrée principal : pose une question au RAG.
    Retourne {"answer": str, "sources": list[dict]}

    Si l'API Gemini est momentanément surchargée (erreur 503), on réessaie
    automatiquement jusqu'à 3 fois avec un délai croissant avant d'abandonner.
    """
    chunks = search(question, top_k=top_k)

    if not chunks:
        return {
            "answer": "Aucun cours n'a encore été importé, ou aucun passage pertinent n'a été trouvé.",
            "sources": [],
        }

    prompt = build_prompt(question, chunks)

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEN_MODEL,
                contents=prompt,
            )
            sources = [
                {
                    "filename": c["filename"],
                    "unit_type": c["unit_type"],
                    "unit_number": c["unit_number"],
                    "text": c["text"],
                }
                for c in chunks
            ]
            return {"answer": response.text, "sources": sources}

        except ClientError as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                return {
                    "answer": (
                        "Le quota gratuit de l'API Gemini est épuisé pour aujourd'hui "
                        "(20 requêtes/jour sur ce modèle). Réessaie demain, ou passe à "
                        "un modèle avec un quota plus élevé."
                    ),
                    "sources": [],
                }
            raise  # autre erreur client, on la laisse remonter

        except ServerError:
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
                continue

    # Après 3 tentatives échouées
    return {
        "answer": (
            "Le service Gemini est momentanément surchargé (erreur 503). "
            "Réessaie dans quelques instants — ce n'est pas un problème de ton côté."
        ),
        "sources": [],
    }