# ☁️ AWS RAG Assistant  
### 🦙 Amazon Bedrock · 🧠 PGVector · 🌐 SerpAPI + Groq Web Fallback  
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Cloud--UI-FF4B4B)
![LangChain](https://img.shields.io/badge/LangChain-RAG-brightgreen)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow)

---

## 🧩 Overview

**AWS RAG Assistant** is an intelligent Retrieval-Augmented Generation (RAG) chatbot that answers **AWS architecture, DevOps, and data engineering** questions.  
It combines **Amazon Bedrock (Llama 3 & Nova Pro)**, **PGVector/PostgreSQL embeddings**, and a **web fallback using SerpAPI + Groq** to fetch and summarize live AWS documentation.

If the local AWS PDF knowledge base doesn’t contain the answer, the assistant searches  
[`https://docs.aws.amazon.com`](https://docs.aws.amazon.com) in real time and includes citations.

---


## 🧱 Tech Stack## 🧱 Tech Stack

| Component | Technology | Description |
|------------|-------------|-------------|
| **Frontend** | Streamlit | Chat-based UI for user interaction and model selection. |
| **LLMs** | Amazon Bedrock (Llama 3, Nova Pro) | Core models for reasoning and AWS-related Q&A. |
| **Memory** | LangChain + PostgreSQL | Stores and summarizes past chats for context persistence. |
| **Embeddings** | Amazon Titan Embeddings v2 | Converts documents into vector form for semantic search. |
| **Vector Store** | PGVector | Stores and retrieves document embeddings efficiently. |
| **Database** | PostgreSQL | Backs vector data and chat history storage. |
| **Web Fallback** | SerpAPI + Groq | Fetches and summarizes live AWS Docs when PDFs lack context. |
| **Orchestration** | LangChain RAG | Connects retrieval, LLM, memory, and prompt logic. |
| **Containerization** | Docker + Compose | Runs app and database in isolated, reproducible environments. |

---
## 🗂️ Directory Structure

```
aws-rag-app/
├── app.py                    # Streamlit entry
├── build_index.py            # Chunk + embed AWS PDFs into PGVector
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
├── data/                     # Place your AWS PDFs here
└── modules/
    ├── config.py             # Bedrock client, embeddings, PG conn
    ├── models.py             # Bedrock model factory functions
    ├── prompts.py            # RAG prompt template
    ├── qa_chain.py           # RAG + memory + web fallback logic
    ├── vectorstore.py        # PGVector loader
    ├── web_search.py         # SerpAPI + Groq summarization
    ├── ui.py                 # Streamlit UI helpers
    ├── ui_markdown.py        # CSS + layout
    └── ui_texts.py           # Text constants
```

---

## ⚙️ Setup Instructions
1️⃣ Clone the repository
```
git clone https://github.com/<your-username>/aws-rag-assistant.git
cd aws-rag-assistant
```

## 2️⃣ Add environment variables

**Create a .env file in the project root:**
```
PG_CONNECTION_STRING=postgresql+psycopg2://postgres:pwd@db:5432/docs_db
AWS_REGION=us-east-1
SERPAPI_API_KEY=your_serpapi_key
GROQ_API_KEY=your_groq_key
```

💡 Your ~/.aws credentials are automatically mounted in the container for Bedrock access.

## 3️⃣ Add your AWS PDFs

**Place AWS Prescriptive Guidance or architecture PDFs in:**

```
data/
```

## 4️⃣ Build vector embeddings

```
docker compose up --build -d
docker exec -it aws-rag-assistant python build_index.py
```

**Check the database:**
```
docker exec -it pgvector-db psql -U postgres -d docs_db
\dt
SELECT COUNT(*) FROM langchain_pg_embedding;
```

## 5️⃣ Run the app
```
docker compose up
```

**App will be live at 👉 http://localhost:8501**

🧪 Example Prompts
Type	Example Question





## 📜 License — MIT
MIT License

Copyright (c) 2025 Navya Kalyani

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished
to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
