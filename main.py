# orchestrateur_rag.py

import os
import uuid
from pathlib import Path
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.storage.blob import BlobServiceClient
import openai
from typing import List
import fitz  # PyMuPDF for PDF extraction

# === CONFIGURATION ===
load_dotenv()

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")
AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
AZURE_STORAGE_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

# === SETUP CLIENTS ===
openai.api_type = "azure"
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = "2023-05-15"

search_client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    index_name=AZURE_SEARCH_INDEX,
    credential=AzureKeyCredential(AZURE_SEARCH_API_KEY)
)

blob_service_client = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
    credential=AZURE_STORAGE_ACCOUNT_KEY
)

# === UTILS ===
def split_text(text: str, max_tokens: int = 500) -> List[str]:
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    for para in paragraphs:
        if len((current + para).split()) < max_tokens:
            current += para + "\n"
        else:
            chunks.append(current.strip())
            current = para + "\n"
    if current:
        chunks.append(current.strip())
    return chunks

def get_embedding(text: str):
    if not text.strip():
        print("⚠️ Chunk vide, embedding ignoré.")
        return []
    response = openai.Embedding.create(
        input=text,
        engine=AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    )
    return response['data'][0]['embedding']

# === MAIN INDEXING FUNCTION ===
def index_documents():
    print("📥 Téléchargement depuis Azure Blob...")
    container = blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER)
    blobs = container.list_blobs()

    for blob in blobs:
        print(f"🔍 Lecture de {blob.name}")
        blob_client = container.get_blob_client(blob)
        extension = blob.name.split(".")[-1].lower()

        # Lecture du contenu
        if extension == "pdf":
            pdf_bytes = blob_client.download_blob().readall()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
        elif extension == "txt":
            text = blob_client.download_blob().readall().decode("utf-8")
        else:
            print(f"⚠️ Format non supporté : {blob.name}")
            continue

        chunks = split_text(text)
        print(f"✂️  {len(chunks)} chunks générés")

        documents = []
        for i, chunk in enumerate(chunks):
            print(f"➡ Embedding chunk :\n{chunk[:100]}...\n")
            embedding = get_embedding(chunk)
            doc = {
                "chunk_id": str(uuid.uuid4()),
                "content": chunk,
                "content_vector": embedding
            }
            documents.append(doc)

        print(f"📤 Envoi de {len(documents)} documents dans Azure Search...")
        result = search_client.upload_documents(documents)
        print(f"✅ Résultat : {result[0].status_code if result else 'OK'}")

if __name__ == "__main__":
    index_documents()
