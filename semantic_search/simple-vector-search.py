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
    "Football is a popular sport"
]

# Convert data into embeddings
embeddings = model.encode(documents)

# Create a FAISS Index
dimension = embeddings.shape[1]

index =  faiss.IndexFlatL2(dimension)

# Add embeddings into the index
index.add(np.array(embeddings))

# Query section

# Convert query to an embedding
query = model.encode(["Artificial Intelligence"])

# Search for the top 2 similar vectors
# D for Distances and I for Indices
D, I = index.search(np.array(query), k=2)

# Print matching documents
print("Most similar documents:")

for i in I[0]:
    print(documents[i])