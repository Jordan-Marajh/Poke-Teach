# import from specific libraries
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Select model for creating embeddings from text strings
model = SentenceTransformer("all-MiniLM-L6-v2")

# Hardcode strings by chopping into tokens - to be scaled up in the future 
# Can be done via json or txt file and loop through
sentences = [
    "Machine learning is powerful",
    "Artificial intelligence is growing rapidly",
    "Pizza tastes great"
]

# Generate embeddings
embeddings = model.encode(sentences)

# Print out data structure of embeddings
print(embeddings.shape)

# Calculate cosine similarity of embeddings
similarity = cosine_similarity(
    [embeddings[0]],
    embeddings
)
 
print(similarity)