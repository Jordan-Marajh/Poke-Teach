# Import the correct libraries
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Provide dummy text data
documents = [
    "Machine learning uses data",
    "Python is a programming language",
    "Football is a popular sport",
    "The 2026 soccer world cup is on right now"
]

# Convert data into embeddings
embeddings = model.encode(documents)

# Create a FAISS Index
dimension = embeddings.shape[1]

index =  faiss.IndexFlatL2(dimension)

# Add embeddings into the index
index.add(np.array(embeddings))

# -----------------------------
# QUERY SECTION
# -----------------------------
 
user_query = input("Enter your query: ")
 
query = model.encode([user_query])
 
D, I = index.search(np.array(query), k=2)
 
for i in I[0]:
    print(documents[i])