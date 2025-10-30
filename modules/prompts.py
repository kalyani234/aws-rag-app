from langchain_core.prompts import PromptTemplate

rag_prompt = PromptTemplate(
    template="""
Human: You are an expert AWS cloud engineer and technical instructor. 
Use the following context to answer the question in a structured and complete way.

Your response must:
- Begin with a brief overview.
- Then list the detailed technical steps or architecture.
- End with key considerations or best practices.
- Stay complete but concise (within the model’s max token limit).
- Do not fabricate any information outside the provided context.

<context>
{context}
</context>

Question: {question}

Assistant (respond completely and clearly within the token limit):
""",
    input_variables=["context", "question"]
)
