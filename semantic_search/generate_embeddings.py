# Generate vector embeddings from the Pokémon and move search documents.

import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer



# Find the project root folder.
PROJECT_FOLDER = Path(__file__).resolve().parent.parent

SEARCH_DATA_FOLDER = (
    PROJECT_FOLDER /
    "semantic_search" /
    "data"
)

POKEMON_SEARCH_FILE = (
    SEARCH_DATA_FOLDER /
    "pokemon_search_documents.json"
)

MOVE_SEARCH_FILE = (
    SEARCH_DATA_FOLDER /
    "move_search_documents.json"
)

POKEMON_EMBEDDINGS_FILE = (
    SEARCH_DATA_FOLDER /
    "pokemon_embeddings.npy"
)

MOVE_EMBEDDINGS_FILE = (
    SEARCH_DATA_FOLDER /
    "move_embeddings.npy"
)

POKEMON_INDEX_FILE = (
    SEARCH_DATA_FOLDER /
    "pokemon.index"
)

MOVE_INDEX_FILE = (
    SEARCH_DATA_FOLDER /
    "move.index"
)

MODEL_NAME = (
    "sentence-transformers/"
    "multi-qa-MiniLM-L6-cos-v1"
)


def load_search_documents(file_path):

    # Check that the search-document file exists.
    if not file_path.is_file():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    # Read the JSON data.
    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:
        documents = json.load(file)

    # The file should contain a list of documents.
    if not isinstance(documents, list):
        raise TypeError(
            f"{file_path.name} does not contain a list."
        )

    if len(documents) == 0:
        raise ValueError(
            f"{file_path.name} contains no documents."
        )

    # Check that every document has usable search text.
    for position, document in enumerate(
        documents,
        start=1
    ):
        if not isinstance(document, dict):
            raise TypeError(
                f"Document {position} in "
                f"{file_path.name} is not an object."
            )

        search_text = document.get(
            "search_text"
        )

        if not isinstance(search_text, str):
            raise TypeError(
                f"Document {position} in "
                f"{file_path.name} does not have "
                f"valid search text."
            )

        if not search_text.strip():
            raise ValueError(
                f"Document {position} in "
                f"{file_path.name} has empty "
                f"search text."
            )

    return documents

def generate_document_embeddings(
    model,
    documents,
    output_file,
    document_type
):

    # Extract each search_text value into a list.
    search_texts = [
        document["search_text"]
        for document in documents
    ]

    print(
        f"\nGenerating embeddings for "
        f"{len(search_texts)} "
        f"{document_type} documents..."
    )

    # Generate one normalised embedding for
    # every search document.
    embeddings = model.encode_document(
        search_texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    # FAISS expects float32 vectors.
    embeddings = embeddings.astype(
        "float32"
    )

    # Save the raw embedding array.
    np.save(
        output_file,
        embeddings
    )

    print(
        f"{document_type.title()} embeddings "
        f"saved to: {output_file.absolute()}"
    )

    return embeddings
    
def create_faiss_index(
    embeddings,
    output_file,
    document_type
):

    # Each embedding row has this many dimensions.
    dimension = embeddings.shape[1]

    # The vectors are normalised, so inner-product
    # similarity is equivalent to cosine similarity.
    index = faiss.IndexFlatIP(
        dimension
    )

    # Add every embedding to the index.
    index.add(
        embeddings
    )

    # Save the completed index.
    faiss.write_index(
        index,
        str(output_file)
    )

    print(
        f"{document_type.title()} FAISS index "
        f"saved to: {output_file.absolute()}"
    )

    return index


def generate_embeddings():

    try:
        SEARCH_DATA_FOLDER.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            "\nReading Pokémon search documents..."
        )

        pokemon_documents = load_search_documents(
            POKEMON_SEARCH_FILE
        )

        print(
            "Reading move search documents..."
        )

        move_documents = load_search_documents(
            MOVE_SEARCH_FILE
        )

        print(
            f"\nLoading embedding model: "
            f"{MODEL_NAME}"
        )

        model = SentenceTransformer(
            MODEL_NAME
        )

        pokemon_embeddings = (
            generate_document_embeddings(
                model,
                pokemon_documents,
                POKEMON_EMBEDDINGS_FILE,
                "Pokémon"
            )
        )

        move_embeddings = (
            generate_document_embeddings(
                model,
                move_documents,
                MOVE_EMBEDDINGS_FILE,
                "move"
            )
        )

        pokemon_index = create_faiss_index(
            pokemon_embeddings,
            POKEMON_INDEX_FILE,
            "Pokémon"
        )

        move_index = create_faiss_index(
            move_embeddings,
            MOVE_INDEX_FILE,
            "move"
        )

        print()
        print("=" * 50)
        print("EMBEDDING AND INDEX SUMMARY")
        print(
            f"Pokémon embedding shape: "
            f"{pokemon_embeddings.shape}"
        )
        print(
            f"Move embedding shape: "
            f"{move_embeddings.shape}"
        )
        print(
            f"Embedding dimension: "
            f"{pokemon_embeddings.shape[1]}"
        )
        print(
            f"Pokémon vectors indexed: "
            f"{pokemon_index.ntotal}"
        )
        print(
            f"Move vectors indexed: "
            f"{move_index.ntotal}"
        )
        print(
            f"Saved to: "
            f"{SEARCH_DATA_FOLDER.absolute()}"
        )

        return True

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
        OSError
    ) as error:
        print(
            f"Could not generate embeddings "
            f"or indexes: {error}"
        )

        return False

    except Exception as error:
        print(
            f"Embedding or FAISS error: "
            f"{error}"
        )

        return False


if __name__ == "__main__":
    generate_embeddings()