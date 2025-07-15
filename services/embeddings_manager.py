import chromadb
from openai import OpenAI
from config import OPENAI_KEY

client = OpenAI(api_key=OPENAI_KEY)

# Initialize ChromaDB Client
chorma_client = chromadb.PersistentClient(path="./data/embeddings_db")
collection = chorma_client.get_or_create_collection("alfred_memories")

def generate_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def store_memory_vector(memory_text, metadata=None):
    embedding = generate_embedding(memory_text)
    collection.add(
        embeddings=[embedding],
        documents=[memory_text],
        ids=[str(len(collection.get()["ids"]))],
        metadatas=[metadata or {}]
    )

    print(f"Stored Memory Vector: {memory_text}")

def search_memory(query, n_results=3):
    query_embedding = generate_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results