# 🧠 AWS RAG Assistant – LangChain + Bedrock + Streamlit
Intelligent Retrieval-Augmented Generation system specifically designed for AWS documentation, guidelines, and best practices.
Key features include:

* Document Processing: Supports multiple file formats, chunking, and embedding generation.
* Vector Database: Uses PGVector for efficient similarity searches on embeddings.
* RAG Pipeline: Combines retrieval and generation for context-aware responses.
* User Interface: Streamlit app for easy interaction, including file uploads and real-time querying.
* Scalability: Built on AWS services for cloud-native deployment.
This project demonstrates best practices in integrating AWS AI/ML services with open-source tools for production-ready RAG systems.
---

## ⚙️ 1. Environment Setup
To get started, set up a isolated Python environment using Conda to avoid conflicts with system packages. This ensures reproducibility and ease of management.

* Create a Conda Environment
This command creates a new Conda environment named 'venv' with Python 3.10, which is compatible with all dependencies in this project.
```conda create -p venv python==3.10 -y
conda activate ./venv
```
**Install Dependencies**

Install all required Python packages listed in requirements.txt, which includes libraries like langchain, langchain-aws, streamlit, psycopg2, and others for embeddings, database connections, and app functionality.
``` install -r requirements.txt ```

* (Optional) Install Watchdog for Faster Streamlit Reloads
Watchdog enables hot-reloading in Streamlit during development, automatically refreshing the app when code changes are detected.
```pip install watchdog```
---

## 🔑 2. Environment Variables

Environment variables are used to securely store sensitive information like AWS credentials and database connection details. Create a .env file in the project root directory (ensure it's added to .gitignore to prevent accidental commits).
Populate it with the following:

```AWS_ACCESS_KEY_ID=your_aws_access_key  # Your AWS IAM access key with Bedrock permissions
AWS_SECRET_ACCESS_KEY=your_aws_secret_key  # Corresponding secret key
AWS_DEFAULT_REGION=your_aws_region  # e.g., us-east-1; region where Bedrock is available

# PostgreSQL connection
PG_CONNECTION_STRING=postgresql+psycopg2://postgres:pwd@localhost:5432/docs_db
```
* Tip: For the database, use Amazon RDS PostgreSQL instance with the PGVector extension installed. To enable PGVector, connect to your database and run CREATE EXTENSION vector;. Ensure your IAM user has necessary permissions for Bedrock (e.g., bedrock:InvokeModel).
---

## 📦 3. Project Structure
The project is organized for modularity, separating concerns like configuration, embeddings, LLM integration, and the RAG chain. Here's the directory layout:

```aws-rag-app/
│
├── app.py                 # Main Streamlit application entry point; handles UI and user interactions
├── requirements.txt       # List of Python dependencies for pip installation
├── .env                   # Environment variables file (git-ignored for security)
├── modules/               # Core logic modules
│   ├── config.py          # Loads environment variables and sets up AWS/DB configurations
│   ├── embeddings.py      # Generates embeddings using AWS Bedrock's Titan model
│   ├── llm_model.py       # Initializes and invokes the Llama 3 model via Bedrock
│   ├── vectorstore.py     # Configures PGVector vector store, handles indexing and retrieval
│   └── rag_chain.py       # Builds the RAG pipeline, integrating retrieval and generation
├── data/                  # Directory for storing uploaded documents or processed files
└── build_index.py         # Standalone script to batch-index documents and store embeddings in the vector database
```
---

## 🚀 4. Run the Application

Once the environment is set up, launch the Streamlit app to interact with the RAG system.
Start Streamlit App
This command runs the app in development mode. Streamlit will automatically open a browser window or provide a local URL.
```streamlit run app.py```

Access the app at:
```http://localhost:8501```

In the interface -
  * Upload documents to the data/ folder.
  * Run indexing via build_index.py or integrated UI buttons.
  * Query the system for responses.
  
---

## 🧩 5. Notes

* LangChain-AWS Integration: Directly interfaces with Bedrock for Titan embeddings and Llama 3 inference, ensuring low-latency and secure model access.
* PGVector Usage: Enables efficient vector similarity searches (e.g., cosine similarity) for retrieving top-k relevant chunks.
* RAG Chain Details: The pipeline fetches contexts, formats prompts, and generates responses, customizable via rag_chain.py.
* Performance Tips: For large documents, adjust chunk sizes in embeddings.py. Monitor AWS quotas for Bedrock invocations.
* Security Best Practices: Use IAM roles instead of access keys in production; enable SSL for RDS connections.
* Rebuild Index: Run python build_index.py to re-process and index documents in data/.
* Test Database Connection: In Python, use psycopg2.connect() with env vars to verify connectivity.
* Update Dependencies: If adding new packages, update requirements.txt with pip freeze > requirements.txt.


6. Ethics & Fair Use
This project was developed with respect for ethical AI use and fair data access principles.

✅ Public Data Only — The assistant interacts exclusively with public AWS documentation (https://docs.aws.amazon.com/). It does not access or process any private, confidential, or user-specific data.

✅ Legitimate APIs — Integrations such as Amazon Bedrock, SerpAPI, and Groq are used in full compliance with their respective terms of service and rate limits.