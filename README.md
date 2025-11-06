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


## 🧱 Tech Stack

| Component | Technology | Description |
|------------|-------------|-------------|
| **Frontend UI** | 🖥️ **Streamlit** | Interactive chat interface for RAG queries, model selection, and result visualization. |
| **LLMs (Core Reasoning)** | 🤖 **Amazon Bedrock (Llama 3 & Nova Pro)** | Provides secure, managed access to state-of-the-art foundation models for reasoning and generation. |
| **Summarization LLM** | 🦙 **Llama 3 (lightweight)** | Used for conversation summarization inside `ConversationSummaryMemory` to persist context efficiently. |
| **Embeddings Model** | 🧩 **Amazon Titan Embeddings v2** | Converts AWS document text into numerical vectors for semantic similarity search. |
| **Vector Store** | 🗄️ **PGVector (PostgreSQL extension)** | Stores document embeddings and supports fast similarity queries. |
| **Database** | 🧠 **PostgreSQL** | Persists vector data (`langchain_pg_embedding`) and conversation memory (`chat_history`). |
| **Memory System** | 💬 **LangChain ConversationSummaryMemory** | Manages long-term chat context summaries using a summarization LLM. |
| **Retrieval Framework** | 🔗 **LangChain (ConversationalRetrievalChain)** | Orchestrates RAG flow between embeddings, LLMs, and user queries. |
| **Web Search (Fallback)** | 🌐 **SerpAPI** | Performs real-time Google searches restricted to `docs.aws.amazon.com` for live AWS documentation. |
| **Web Summarization** | ⚡ **Groq API** | Summarizes live AWS documentation pages returned by SerpAPI before passing them to the LLM. |
| **Containerization** | 🐳 **Docker & Docker Compose** | Runs Streamlit app and PGVector database in isolated, reproducible environments. |
| **Infrastructure & Deployment** | ☁️ **AWS Bedrock SDK + boto3** | Connects securely to Bedrock models using AWS credentials. |
| **Document Processing** | 📄 **LangChain PDF Loader + Text Splitters** | Loads and chunks AWS Prescriptive Guidance PDFs before embedding. |
| **Language Runtime** | 🐍 **Python 3.10** | Core language environment for all modules and LangChain integrations. |

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
AWS Architecture	What are the key components of an AWS data lake?
DevOps	How does AWS CodePipeline integrate with ECS deployments?
Event-driven	How does AWS Glue work with EventBridge in a data lake?
Web fallback	What new features were added to Amazon Bedrock in 2025?




📜 License — MIT
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
