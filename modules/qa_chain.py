# modules/qa_chain.py
"""
Handles RAG + memory + AWS Docs web fallback.
If PGVector doesn't provide enough context, it searches AWS Docs via SerpAPI.
"""

from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.memory import ConversationSummaryMemory
from sqlalchemy import create_engine
from .prompts import rag_prompt
from .config import PG_CONNECTION_STRING
from .models import create_summary_model
from .web_search import search_aws_docs, fetch_page_content, summarize_with_groq

# ------------------------------
# 🧠 Persistent Memory (PostgreSQL)
# ------------------------------
engine = create_engine(PG_CONNECTION_STRING)

chat_history = SQLChatMessageHistory(
    table_name="chat_history",
    session_id="default_session",  # change this later for user sessions
    connection_string=PG_CONNECTION_STRING,
)

summary_llm = create_summary_model()

memory = ConversationSummaryMemory(
    llm=summary_llm,
    memory_key="chat_history",
    return_messages=True,
    output_key="answer",
    chat_memory=chat_history,
)

# ------------------------------
# 🔗 Conversational RAG + Web Search
# ------------------------------
def get_response_with_prompt(llm, vector_store, query):
    """
    Executes a RAG query with persistent memory and web fallback.
    1. Search PGVector (PDF knowledge base)
    2. If weak or missing, search AWS Docs (SerpAPI)
    """
    
    # Convert query to string first
    query_str = query if isinstance(query, str) else str(query)
    
    # Get current chat history
    loaded_memory = memory.load_memory_variables({})
    current_chat_history = loaded_memory.get("chat_history", [])

    # Create the QA chain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        ),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": rag_prompt},
        return_source_documents=True,
        verbose=True  # Add verbose for debugging
    )

    try:
        # ✅ FIXED: Use the correct input format
        result = qa_chain.invoke({"question": query_str})
        
        # Extract answer and sources
        if isinstance(result, dict):
            answer_text = result.get("answer", "").strip()
            source_docs = result.get("source_documents", [])
        else:
            answer_text = str(result).strip()
            source_docs = []

        unique_sources = {doc.metadata.get("source", "Unknown file") for doc in source_docs}

        # 🔍 Check if fallback is needed
        if should_trigger_fallback(answer_text):
            print("🔍 Triggering fallback: AWS Docs search...")
            return handle_web_fallback(llm, query_str, answer_text)

        # ✅ Default — return RAG result
        return {
            "answer": answer_text or "No response generated.",
            "sources": list(unique_sources) if unique_sources else [],
        }
        
    except Exception as e:
        print(f"Error in QA chain: {e}")
        # Fallback to direct LLM call
        return handle_web_fallback(llm, query_str, "Error in RAG system")

def should_trigger_fallback(answer_text):
    """Check if we should trigger web search fallback"""
    if not answer_text:
        return True
    answer_lower = answer_text.lower()
    return (
        "not related to aws" in answer_lower or
        "no response generated" in answer_lower or
        "i don't know" in answer_lower or
        "i cannot answer" in answer_lower or
        len(answer_text.split()) < 15
    )

def handle_web_fallback(llm, query_str, original_answer):
    """Handle web search fallback when RAG fails"""
    print("🔍 Searching AWS Docs for current information...")
    aws_links = search_aws_docs(query_str)
    
    if aws_links:
        print(f"📄 Found {len(aws_links)} relevant AWS documentation links")
        
        # Fetch and combine content from links
        combined_content = ""
        for url in aws_links[:3]:  # Limit to first 3 links to avoid too much content
            content = fetch_page_content(url)
            if content:
                combined_content += f"\n\nFrom {url}:\n{content}"
        
        if combined_content:
            # Summarize the combined content
            summarized_context = summarize_with_groq(combined_content)
            
            # Create a new prompt with the web context
            enhanced_prompt = f"""Based on the latest AWS documentation, answer the following question:

Question: {query_str}

Context from AWS Documentation:
{summarized_context}

Please provide a comprehensive answer based on the current AWS documentation:"""
            
            # Get answer using the enhanced context
            try:
                fallback_result = llm.invoke(enhanced_prompt)
                fallback_answer = getattr(fallback_result, "content", str(fallback_result))
                
                return {
                    "answer": f"Based on current AWS documentation:\n\n{fallback_answer.strip()}",
                    "sources": aws_links,
                    "note": "This information came from live AWS documentation search"
                }
            except Exception as e:
                print(f"Error in fallback LLM call: {e}")
    
    # If web search also fails, return the original answer with note
    return {
        "answer": f"{original_answer}\n\nNote: I also searched current AWS documentation but couldn't find specific information about 2025 features.",
        "sources": [],
        "note": "Limited information available"
    }