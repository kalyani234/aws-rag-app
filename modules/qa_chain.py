from langchain.chains import RetrievalQA
from .prompts import rag_prompt

def get_response_with_prompt(llm, vector_store, query):
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": rag_prompt}
    )
    result = qa_chain.invoke({"query": query})
    return result["result"]
