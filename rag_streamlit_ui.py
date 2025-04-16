# rag_streamlit_ui.py

import os
import streamlit as st
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import openai

# === LOAD CONFIG ===
load_dotenv()

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
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

# === FUNCTIONS ===
def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        engine=AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    )
    return response['data'][0]['embedding']

def search_similar_docs(question, k=3):
    embedding = get_embedding(question)
    results = search_client.search(
        search_text="",
        vectors=[{
            "value": embedding,
            "fields": "content_vector",
            "k": k
        }],
        top=k
    )
    return [doc["content"] for doc in results]

def ask_rag_question(question):
    context_docs = search_similar_docs(question)
    context = "\n---\n".join(context_docs)

    prompt = f"""
Tu es un assistant expert ISO 27001.
Réponds précisément à la question ci-dessous en te basant uniquement sur le contexte fourni.

Contexte :
{context}

Question :
{question}
"""

    response = openai.ChatCompletion.create(
        engine=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Tu es un assistant expert en cybersécurité et conformité ISO 27001."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response["choices"][0]["message"]["content"], context_docs

# === STREAMLIT UI ===
st.set_page_config(page_title="Chat ISO 27001", page_icon="🛡️")
st.title("🛡️ Assistant ISO 27001")
st.markdown("Pose une question sur la norme ISO 27001 (Annexe A)")

question = st.text_input("💬 Ta question :")

if question:
    with st.spinner("Recherche et génération de réponse..."):
        answer, context = ask_rag_question(question)
        st.subheader("🤖 Réponse")
        st.write(answer)

        with st.expander("📚 Contexte utilisé"):
            for i, chunk in enumerate(context):
                st.markdown(f"**Chunk {i+1}:**\n{chunk}")
