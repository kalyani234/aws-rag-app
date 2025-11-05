# modules/qa_chain.py
import os
import requests
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.memory import ConversationSummaryMemory
from sqlalchemy import create_engine
from modules.prompts import rag_prompt
from modules.config import PG_CONNECTION_STRING
from modules.models import create_llama3_model

# ------------------------------
# 🧠 Persistent Memory (PostgreSQL)
# ------------------------------

engine = create_engine(PG_CONNECTION_STRING)

chat_history = SQLChatMessageHistory(
    table_name="chat_history",
    session_id="default_session",
    connection_string=PG_CONNECTION_STRING
)

summary_llm = create_llama3_model(max_tokens=256, temperature=0.3)

memory = ConversationSummaryMemory(
    llm=summary_llm,
    memory_key="chat_history",
    return_messages=True,
    output_key="answer",
    chat_memory=chat_history
)

# ------------------------------
# 🌐 Web Augmentation (SerpAPI + GROQ)
# ------------------------------

SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def search_aws_docs(query: str):
    """Use SerpAPI to search AWS Docs for relevant content."""
    try:
        if not SERPAPI_KEY:
            return None

        params = {
            "engine": "google",
            "q": f"site:docs.aws.amazon.com {query}",
            "api_key": SERPAPI_KEY
        }
        resp = requests.get("https://serpapi.com/search", params=params, timeout=20)
        results = resp.json().get("organic_results", [])
        snippets = [r.get("snippet", "") for r in results[:3]]
        urls = [r.get("link", "") for r in results[:3]]

        web_context = "\n".join(snippets)
        web_sources = [u for u in urls if u]
        return web_context, web_sources
    except Exception as e:
        print(f"⚠️ SerpAPI error: {e}")
        return None, []

def summarize_with_groq(text: str):
    """Use GROQ to summarize or clean web results."""
    try:
        if not GROQ_API_KEY:
            return text
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mixtral-8x7b",
            "messages": [
                {"role": "system", "content": "Summarize AWS documentation concisely and factually."},
                {"role": "user", "content": text}
            ],
            "temperature": 0.3,
            "max_tokens": 512
        }
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=30)
        summary = resp.json()["choices"][0]["message"]["content"]
        return summary
    except Exception as e:
        print(f"⚠️ GROQ summarization error: {e}")
        return text

# ------------------------------
# 🔗 Hybrid RAG + Web + Memory
# ------------------------------

def get_response_with_prompt(llm, vector_store, query):
    """
    Executes a hybrid RAG query with persistent memory and live AWS Docs augmentation.
    """

    # 🔍 Step 1: Try vector DB (RAG)
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        ),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": rag_prompt},
        return_source_documents=True
    )

    query_str = query if isinstance(query, str) else str(query)
    result = qa_chain.invoke({"question": query_str})
    formatted_answer = result.get("answer", "").strip()

    # If the answer looks unrelated or empty → use web search fallback
    if (
        not formatted_answer
        or "This question is not related to AWS Prescriptive Guidance" in formatted_answer
        or len(formatted_answer.split()) < 15
    ):
        print("🌐 Falling back to SerpAPI + GROQ for live AWS Docs info...")
        web_context, web_sources = search_aws_docs(query_str)
        if web_context:
            summarized = summarize_with_groq(web_context)
            formatted_answer = summarized or "No live summary generated."
            return {
                "answer": formatted_answer.strip(),
                "sources": web_sources or ["https://docs.aws.amazon.com/"]
            }

    # Deduplicate sources from embeddings
    unique_sources = set()
    if "source_documents" in result:
        for doc in result["source_documents"]:
            file_name = doc.metadata.get("source", "Unknown file")
            unique_sources.add(file_name)

    source_text = " | ".join(sorted(unique_sources)) if unique_sources else "No source found."
    return {
        "answer": formatted_answer or "No response generated.",
        "sources": [source_text]
    }
