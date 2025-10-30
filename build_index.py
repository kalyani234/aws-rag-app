"""
build_index.py — Incremental, fault-tolerant vector index builder for large PDFs.
✅ Batch processing
✅ Automatic retry on timeout
✅ Live progress logging
✅ Safe writes to PostgreSQL (PGVector)
"""

import time
import math
from tqdm import tqdm
from langchain_community.vectorstores import PGVector
from modules.vectorstore import data_ingestion
from modules.config import bedrock_embeddings, PG_CONNECTION_STRING

# -----------------------------
# Settings
# -----------------------------
COLLECTION_NAME = "aws_docs"
BATCH_SIZE = 100        # ↓ Smaller = safer, avoids Titan timeouts (try 50–100)
MAX_RETRIES = 3         # Retry failed batches up to 3 times
RETRY_DELAY_BASE = 5    # Base seconds for exponential backoff between retries
SLEEP_BETWEEN_BATCHES = 1  # Wait between successful batches


# -----------------------------
# Batch Embed & Store Function
# -----------------------------
def create_vector_store_in_batches(docs):
    total_docs = len(docs)
    total_batches = math.ceil(total_docs / BATCH_SIZE)
    print(f"📄 Total Chunks: {total_docs}")
    print(f"🧩 Processing in {total_batches} batches of {BATCH_SIZE} each\n")

    for batch_idx in range(total_batches):
        start_idx = batch_idx * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, total_docs)
        batch_docs = docs[start_idx:end_idx]

        print(f"[Batch {batch_idx+1}/{total_batches}] Embedding {len(batch_docs)} chunks...")

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # Embed and store this batch
                PGVector.from_documents(
                    documents=batch_docs,
                    embedding=bedrock_embeddings,
                    collection_name=COLLECTION_NAME,
                    connection_string=PG_CONNECTION_STRING,
                )

                print(f"✅ Batch {batch_idx+1}/{total_batches} stored successfully.")
                break

            except Exception as e:
                print(f"⚠️ Attempt {attempt}/{MAX_RETRIES} failed for batch {batch_idx+1}: {e}")

                if "ModelTimeoutException" in str(e):
                    print("⏳ Bedrock model timed out — reducing batch size may help.")
                elif "ThrottlingException" in str(e):
                    print("⚠️ Hit AWS Bedrock rate limit — will retry automatically.")

                if attempt < MAX_RETRIES:
                    wait_time = RETRY_DELAY_BASE * attempt
                    print(f"🔁 Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Skipping batch {batch_idx+1} after {MAX_RETRIES} failures.")
                    break

        time.sleep(SLEEP_BETWEEN_BATCHES)


# -----------------------------
# Main Entry Point
# -----------------------------
if __name__ == "__main__":
    print("🚀 Starting index build...")
    start_time = time.time()

    try:
        # Load and chunk PDF data
        docs = data_ingestion()
        print(f"✅ Loaded {len(docs)} chunks.")

        # Progress bar for all batches
        with tqdm(total=len(docs), desc="🔢 Embedding progress", unit="chunks") as pbar:
            total_batches = math.ceil(len(docs) / BATCH_SIZE)
            for batch_idx in range(total_batches):
                start_idx = batch_idx * BATCH_SIZE
                end_idx = min(start_idx + BATCH_SIZE, len(docs))
                batch_docs = docs[start_idx:end_idx]

                success = False
                for attempt in range(1, MAX_RETRIES + 1):
                    try:
                        PGVector.from_documents(
                            documents=batch_docs,
                            embedding=bedrock_embeddings,
                            collection_name=COLLECTION_NAME,
                            connection_string=PG_CONNECTION_STRING,
                        )
                        success = True
                        break
                    except Exception as e:
                        print(f"⚠️ Batch {batch_idx+1}/{total_batches} attempt {attempt} failed: {e}")
                        wait_time = RETRY_DELAY_BASE * attempt
                        print(f"🔁 Retrying in {wait_time}s...")
                        time.sleep(wait_time)

                if success:
                    pbar.update(len(batch_docs))
                else:
                    print(f"❌ Skipped batch {batch_idx+1} after {MAX_RETRIES} retries.")

                time.sleep(SLEEP_BETWEEN_BATCHES)

        print("🎉 Vector store successfully saved to PostgreSQL!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        total_time = round(time.time() - start_time, 2)
        print(f"⏱️ Total time: {total_time} seconds")
