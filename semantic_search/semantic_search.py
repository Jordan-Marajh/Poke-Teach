"""
Semantic search for Pokémon and moves.

FAISS ranks records by meaning. Optional user-entered filters
handle exact requirements such as type, stats and damage class.
"""

import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


ROOT = Path(__file__).resolve().parent.parent
EXPORTS = ROOT / "exports"
DATA = ROOT / "semantic_search" / "data"

MODEL_NAME = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"

FILES = {
    "pokemon_data": EXPORTS / "pokemon.json",
    "move_data": EXPORTS / "moves.json",
    "pokemon_docs": DATA / "pokemon_search_documents.json",
    "move_docs": DATA / "move_search_documents.json",
    "pokemon_index": DATA / "pokemon.index",
    "move_index": DATA / "move.index",
}

STAT_FIELDS = {
    "hp": "hp",
    "attack": "attack",
    "defence": "defense",
    "defense": "defense",
    "special attack": "special-attack",
    "special defence": "special-defense",
    "special defense": "special-defense",
    "speed": "speed",
    "height": "height_m",
    "weight": "weight_kg",
}


def load_json(path):
    """Load a JSON file."""

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def load_resources():
    """Load data, search documents and FAISS indexes."""

    resources = {
        "pokemon_docs":
            load_json(FILES["pokemon_docs"]),

        "move_docs":
            load_json(FILES["move_docs"]),

        "pokemon_data":
            load_json(FILES["pokemon_data"]),

        "move_data":
            load_json(FILES["move_data"]),

        "pokemon_index":
            faiss.read_index(
                str(FILES["pokemon_index"])
            ),

        "move_index":
            faiss.read_index(
                str(FILES["move_index"])
            ),
    }

    if (
        len(resources["pokemon_docs"])
        != resources["pokemon_index"].ntotal
    ):
        raise ValueError(
            "Pokémon documents and FAISS index "
            "do not match."
        )

    if (
        len(resources["move_docs"])
        != resources["move_index"].ntotal
    ):
        raise ValueError(
            "Move documents and FAISS index "
            "do not match."
        )

    resources["pokemon_lookup"] = {
        item["id"]: item
        for item in resources["pokemon_data"]
    }

    resources["move_lookup"] = {
        item["id"]: item
        for item in resources["move_data"]
    }

    return resources


def ask_number(prompt, integer=False):
    """Read an optional number from the user."""

    while True:
        value = input(prompt).strip()

        if not value:
            return None

        try:
            if integer:
                return int(value)

            return float(value)

        except ValueError:
            print(
                "Enter a valid number or "
                "press Enter to skip."
            )


def vector_search(
    model,
    query,
    documents,
    index,
    lookup,
    filter_function,
    top_k
):
    """
    Rank every record with FAISS, then keep the best records
    that satisfy the selected filters.
    """

    query_vector = model.encode_query(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    query_vector = np.ascontiguousarray(
        query_vector,
        dtype="float32"
    )

    # Search the full index because highly ranked records
    # may later be rejected by the exact filters.
    scores, indices = index.search(
        query_vector,
        index.ntotal
    )

    results = []

    for score, index_position in zip(
        scores[0],
        indices[0]
    ):
        if index_position == -1:
            continue

        document = documents[
            int(index_position)
        ]

        record = lookup.get(
            document["id"]
        )

        if (
            record
            and filter_function(record)
        ):
            results.append(
                (
                    record,
                    float(score)
                )
            )

        if len(results) == top_k:
            break

    return results


def pokemon_search(
    model,
    resources
):
    """Run a Pokémon search."""

    query = input(
        "\nDescribe the Pokémon: "
    ).strip() or "Pokémon"

    pokemon_type = input(
        "Type [blank for any]: "
    ).strip().lower()

    field = input(
        "Numeric filter "
        "[hp, attack, defence, special attack, "
        "special defence, speed, height, weight; "
        "blank for none]: "
    ).strip().lower()

    stat_key = (
        STAT_FIELDS.get(field)
        if field
        else None
    )

    if field and stat_key is None:
        print(
            "Unknown numeric field."
        )
        return

    minimum = (
        ask_number(
            "Minimum [blank for none]: "
        )
        if stat_key
        else None
    )

    maximum = (
        ask_number(
            "Maximum [blank for none]: "
        )
        if stat_key
        else None
    )

    top_k = (
        ask_number(
            "Results [5]: ",
            integer=True
        )
        or 5
    )

    def matches(pokemon):

        if (
            pokemon_type
            and pokemon_type
            not in pokemon.get(
                "types",
                []
            )
        ):
            return False

        if not stat_key:
            return True

        if stat_key in {
            "height_m",
            "weight_kg"
        }:
            value = pokemon.get(
                stat_key
            )

        else:
            value = (
                pokemon
                .get("stats", {})
                .get(stat_key)
            )

        if value is None:
            return False

        if (
            minimum is not None
            and value < minimum
        ):
            return False

        if (
            maximum is not None
            and value > maximum
        ):
            return False

        return True

    results = vector_search(
        model,
        query,
        resources["pokemon_docs"],
        resources["pokemon_index"],
        resources["pokemon_lookup"],
        matches,
        top_k
    )

    print("\nPOKÉMON RESULTS")

    for position, (
        pokemon,
        score
    ) in enumerate(
        results,
        start=1
    ):
        stats = pokemon.get(
            "stats",
            {}
        )

        name = (
            pokemon["name"]
            .replace("-", " ")
            .title()
        )

        print(
            f"\n{position}. {name}"
            f"\nTypes: "
            f"{', '.join(pokemon.get('types', []))}"
            f"\nHP: {stats.get('hp')} | "
            f"Attack: {stats.get('attack')} | "
            f"Defence: {stats.get('defense')} | "
            f"Speed: {stats.get('speed')}"
            f"\nSimilarity: {score:.4f}"
        )

    if not results:
        print(
            "No Pokémon matched those filters."
        )


def move_search(
    model,
    resources
):
    """Run a move search."""

    query = input(
        "\nDescribe the move: "
    ).strip() or "Pokémon move"

    move_type = input(
        "Type [blank for any]: "
    ).strip().lower()

    damage_class = input(
        "Damage class "
        "[physical, special, status; blank for any]: "
    ).strip().lower()

    ailment = input(
        "Ailment [blank for any]: "
    ).strip().lower()

    priority = input(
        "Priority "
        "[increased, standard, reduced; blank for any]: "
    ).strip().lower()

    top_k = (
        ask_number(
            "Results [5]: ",
            integer=True
        )
        or 5
    )

    def matches(move):

        if (
            move_type
            and move.get("type")
            != move_type
        ):
            return False

        if (
            damage_class
            and move.get("damage_class")
            != damage_class
        ):
            return False

        move_meta = (
            move.get("meta")
            or {}
        )

        if (
            ailment
            and move_meta.get("ailment")
            != ailment
        ):
            return False

        move_priority = (
            move.get("priority")
            or 0
        )

        if (
            priority == "increased"
            and move_priority <= 0
        ):
            return False

        if (
            priority == "standard"
            and move_priority != 0
        ):
            return False

        if (
            priority == "reduced"
            and move_priority >= 0
        ):
            return False

        return True

    results = vector_search(
        model,
        query,
        resources["move_docs"],
        resources["move_index"],
        resources["move_lookup"],
        matches,
        top_k
    )

    print("\nMOVE RESULTS")

    for position, (
        move,
        score
    ) in enumerate(
        results,
        start=1
    ):
        name = (
            move["name"]
            .replace("-", " ")
            .title()
        )

        print(
            f"\n{position}. {name}"
            f"\nType: {move.get('type')} | "
            f"Class: {move.get('damage_class')}"
            f"\nPower: {move.get('power')} | "
            f"Priority: {move.get('priority')}"
            f"\nSimilarity: {score:.4f}"
        )

    if not results:
        print(
            "No moves matched those filters."
        )


def semantic_search():
    """Load the resources and run the search menu."""

    try:
        resources = load_resources()

        model = SentenceTransformer(
            MODEL_NAME
        )

        while True:
            print(
                "\n1. Search Pokémon"
                "\n2. Search moves"
                "\n3. Exit"
            )

            choice = input(
                "Choose an option: "
            ).strip()

            if choice == "1":
                pokemon_search(
                    model,
                    resources
                )

            elif choice == "2":
                move_search(
                    model,
                    resources
                )

            elif choice == "3":
                break

            else:
                print(
                    "Choose 1, 2 or 3."
                )

        return True

    except Exception as error:
        print(
            f"Semantic search failed: "
            f"{error}"
        )
        return False


if __name__ == "__main__":
    semantic_search()