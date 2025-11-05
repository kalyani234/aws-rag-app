import os
from dotenv import load_dotenv
import boto3
from langchain_aws import BedrockEmbeddings

load_dotenv()

PG_CONNECTION_STRING = os.getenv("PG_CONNECTION_STRING")  # required
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Bedrock runtime client
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# Embeddings (Titan v2)
bedrock_embeddings = BedrockEmbeddings(
    client=bedrock_client,
    model_id="amazon.titan-embed-text-v2:0",
)
