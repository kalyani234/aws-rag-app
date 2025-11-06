"""
Hybrid RAG + SerpAPI + GROQ fallback.
Uses PGVector (PDFs) first, then live AWS Docs if context is weak.
"""

import os, requests
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.memory import ConversationSummaryMemory
from sqlalchemy import create_engine
from modules.prompts import rag_prompt
from modules.config import PG_CONNECTION_STRING
from modules.models import create_llama3_model
from modules.web_search import search_aws_docs, fetch_page_content, summarize_with_groq

# ------------------------------
# 🧠 Persistent Memory
# ------------------------------
engine = create_engine(PG_CONNECTION_STRING)
chat_history = SQLChatMessageHistory(
    table_name="chat_history",
    session_id="default_session",
    connection_string=PG_CONNECTION_STRING,
)
summary_llm = create_llama3_model(max_tokens=256, temperature=0.3)
memory = ConversationSummaryMemory(
    llm=summary_llm,
    memory_key="chat_history",
    return_messages=True,
    output_key="answer",
    chat_memory=chat_history,
)

# ------------------------------
# 🌐 Fallback trigger logic
# ------------------------------
def should_fallback(answer: str, query: str) -> bool:
    if not answer:
        return True
    text = answer.lower()
    # typical refusal phrases
    triggers = [
        "not related to aws",
        "not related to aws prescriptive guidance",
        "not related to the provided documents",
        "no response generated",
        "i don't know",
        "cannot answer",
        "no relevant information",
    ]
    # new/future topics trigger automatically
    future = ["2025", "preview", "latest", "new", "release", "announcement"]
    if any(f in query.lower() for f in future):
        print("🧠 Future/preview keyword detected — forcing SerpAPI fallback.")
        return True
    return any(t in text for t in triggers) or len(text.split()) < 40


# ------------------------------
# 🔗 Hybrid pipeline
# ------------------------------
def get_response_with_prompt(llm, vector_store, query):
    query_str = query if isinstance(query, str) else str(query)

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3},
        ),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": rag_prompt},
        return_source_documents=True,
    )

    try:
        result = qa_chain.invoke({"question": query_str})
        answer = result.get("answer", "").strip()
        srcs = {d.metadata.get("source", "Unknown") for d in result.get("source_documents", [])}
    except Exception as e:
        print(f"❌ RAG chain error: {e}")
        answer, srcs = "", set()

    # ---------------- Fallback ----------------
    if should_fallback(answer, query_str):
        print("🌐 Falling back to SerpAPI + GROQ ...")
        links = search_aws_docs(query_str)
        if links:
            text = ""
            for u in links[:3]:
                text += fetch_page_content(u)
            summary = summarize_with_groq(text) if text else ""
            if summary:
                enhanced = f"""Based on latest AWS docs:
{summary}

Question: {query_str}
Provide code snippets (Python/boto3/SQL/CLI) and AWS best practices."""
                try:
                    resp = llm.invoke(enhanced)
                    new_ans = getattr(resp, "content", str(resp))
                    return {"answer": new_ans.strip(), "sources": links}
                except Exception as e:
                    print(f"⚠️ Fallback LLM error: {e}")
                    return {"answer": summary[:2000], "sources": links}
        return {
            "answer": answer + "\n\n(No live AWS info found.)",
            "sources": list(srcs),
        }

    print("📚 Using local PDF embeddings.")
    return {"answer": answer, "sources": list(srcs)}
