# All Bedrock chat models live here
from langchain_aws import ChatBedrockConverse
from .config import bedrock_client

# Fast/cheap – good for chat & summarization
def create_llama3_model(max_tokens=1024, temperature=0.5):
    return ChatBedrockConverse(
        client=bedrock_client,
        model="meta.llama3-8b-instruct-v1:0",
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=0.9,
    )

# Deep/reasoning – Nova Pro via Inference Profile ARN
def create_nova_model(max_tokens=1024, temperature=0.5):
    return ChatBedrockConverse(
        client=bedrock_client,
        model="arn:aws:bedrock:us-east-1:359416636668:inference-profile/us.amazon.nova-pro-v1:0",
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=0.9,
    )

# Lightweight summarizer for memory – use Llama 3
def create_summary_model():
    return create_llama3_model(max_tokens=256, temperature=0.3)
