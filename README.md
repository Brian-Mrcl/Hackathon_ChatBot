# 💼 Projet RAG - ISO 27001

Ce projet est un assistant intelligent qui répond à des questions sur l'annexe A de la norme ISO 27001 à l'aide de l'IA générative d'Azure OpenAI et d'Azure Cognitive Search.

---

## 🧠 Fonctionnalités
- Extraction du contenu de documents PDF (Annexe A)
- Découpage en chunks + génération d'embeddings via Azure OpenAI
- Indexation des chunks vectorisés dans Azure Cognitive Search
- Interface utilisateur via Streamlit pour poser des questions
- Réponses générées en fonction du contexte extrait

---

## ⚙️ Installation

### 1. Cloner le projet et créer l'environnement virtuel
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

> Si tu n’as pas de `requirements.txt`, installe manuellement :
```bash
pip install streamlit openai azure-search-documents python-dotenv azure-storage-blob pymupdf
```

---

## 🔐 Configuration `.env`
Crée un fichier `.env` à la racine du projet avec :
```env
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

AZURE_SEARCH_ENDPOINT=...
AZURE_SEARCH_API_KEY=...
AZURE_SEARCH_INDEX=index-iso27001

AZURE_STORAGE_ACCOUNT_NAME=...
AZURE_STORAGE_ACCOUNT_KEY=...
AZURE_STORAGE_CONTAINER=annexea
```

---

## 🚀 Lancer l’orchestrateur (indexation RAG)
```bash
python main.py
```
> Ce script va récupérer les fichiers depuis Azure Blob, générer les embeddings, et les envoyer dans Azure Search.

---

## 💬 Lancer l’interface de question (Streamlit)
```bash
streamlit run rag_streamlit_ui.py
```
> Une page va s’ouvrir dans ton navigateur pour poser des questions à l’assistant ISO 27001 🛡️

---

## 📁 Structure du projet
```
Hackathon_ChatBot/
├── .env
├── main.py                  # Indexation des documents
├── ask_rag.py               # Version terminal pour poser une question
├── rag_streamlit_ui.py      # Interface utilisateur Streamlit
├── venv/                    # Environnement virtuel
└── README.md
```

---

## 🧩 À venir / idées bonus
- Ajout de filtre par contrôle / catégorie
- Chat en continu (multi-turn)
- Support multi-documents (Annexe A, B, etc)

---

🎓 Projet réalisé dans le cadre du hackathon Microsoft / OpenCertif à l'EFREI Paris.

