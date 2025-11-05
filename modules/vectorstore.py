import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import PGVector
from .config import bedrock_embeddings, PG_CONNECTION_STRING

COLLECTION_NAME = "aws_docs"

def data_ingestion():
    if not os.path.exists("data") or not os.listdir("data"):
        raise ValueError("Please add PDF files to the `data/` folder.")
    loader = PyPDFDirectoryLoader("data")
    documents = loader.load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=300).split_documents(documents)
    return chunks

def create_vector_store(docs):
    PGVector.from_documents(
        documents=docs,
        embedding=bedrock_embeddings,
        collection_name=COLLECTION_NAME,
        connection_string=PG_CONNECTION_STRING,
    )

def load_vector_store():
    return PGVector(
        embedding_function=bedrock_embeddings,
        collection_name=COLLECTION_NAME,
        connection_string=PG_CONNECTION_STRING,
    )
