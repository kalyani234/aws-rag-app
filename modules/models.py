from langchain_aws import ChatBedrockConverse
from .config import bedrock_client

def create_llama3_model(max_tokens=1024, temperature=0.5):
    """
    Creates and returns a configured Llama 3 Bedrock model.
    :param max_tokens: Controls how long the model's answers can be.
    :param temperature: Controls creativity (0.0 = focused, 1.0 = creative).
    """
    return ChatBedrockConverse(
        client=bedrock_client,
        model="meta.llama3-8b-instruct-v1:0",
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=0.9
    )
