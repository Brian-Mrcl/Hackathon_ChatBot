# ask_rag.py

import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import openai

# === CONFIGURATION ===
load_dotenv()

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

openai.api_type = "azure"
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = "2023-05-15"

search_client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    index_name=AZURE_SEARCH_INDEX,
    credential=AzureKeyCredential(AZURE_SEARCH_API_KEY)
)

# === Embedding de la question ===
def get_embedding(text: str):
    response = openai.Embedding.create(
        input=text,
        engine=AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    )
    return response['data'][0]['embedding']

# === Recherche dans Azure Search ===
def search_similar_docs(question: str, k=3):
    embedding = get_embedding(question)
    results = search_client.search(
        search_text="",  # rien, on passe que par les vecteurs
        vectors=[{
            "value": embedding,
            "fields": "content_vector",
            "k": k
        }],
        top=k
    )
    return [doc["content"] for doc in results]

# === Génération de réponse GPT ===
def ask_rag_question(question: str):
    print("🧠 Question :", question)
    context_docs = search_similar_docs(question)
    context = "\n---\n".join(context_docs)

    prompt = f"""
Tu es un expert en cybersécurité.
Réponds précisément à la question ci-dessous, uniquement à partir du contexte fourni.

Contexte :
{context}

Question :
{question}
"""

    response = openai.ChatCompletion.create(
        engine=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Tu es un assistant spécialisé en normes ISO 27001."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response["choices"][0]["message"]["content"]

# === TEST ===
if __name__ == "__main__":
    question = input("🧠 Pose ta question sur l'annexe A : ")
    answer = ask_rag_question(question)
    print("\n🤖 Réponse :\n", answer)
