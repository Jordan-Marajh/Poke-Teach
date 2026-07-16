# Create readable text documents for Pokémon and move semantic search.

import json
from pathlib import Path


# Find the project root folder.
PROJECT_FOLDER = Path(__file__).resolve().parent.parent

EXPORT_FOLDER = PROJECT_FOLDER / "exports"

SEARCH_DATA_FOLDER = (
    PROJECT_FOLDER /
    "semantic_search" /
    "data"
)

POKEMON_FILE = EXPORT_FOLDER / "pokemon.json"
MOVES_FILE = EXPORT_FOLDER / "moves.json"

POKEMON_SEARCH_FILE = (
    SEARCH_DATA_FOLDER /
    "pokemon_search_documents.json"
)

MOVE_SEARCH_FILE = (
    SEARCH_DATA_FOLDER /
    "move_search_documents.json"
)



def readable_name(name):
    # e.g. converts "special-attack" into "special attack"
    return (
        str(name)
        .replace("-", " ")
        .replace("_", " ")
        .replace("+", " and ")
    )


def join_words(words):
    # e.g. converts ["fire", "flying"] into "fire and flying"
    if not words:
        return "unknown"

    if len(words) == 1:
        return words[0]

    return ", ".join(words[:-1]) + f" and {words[-1]}"

def describe_stat(value):

    # Add descriptive words so that a query such as
    # "fast Pokémon" can match a numerical speed stat.

    if value >= 120:
        return "very high"

    if value >= 90:
        return "high"

    if value >= 60:
        return "moderate"

    if value >= 30:
        return "low"

    return "very low"

def build_pokemon_search_text(pokemon):

    name = readable_name(
        pokemon["name"]
    ).title()

    pokemon_types = [
        readable_name(pokemon_type)
        for pokemon_type in pokemon["types"]
    ]

    normal_abilities = [
        readable_name(ability["name"])
        for ability in pokemon["abilities"]
        if not ability["is_hidden"]
    ]

    hidden_abilities = [
        readable_name(ability["name"])
        for ability in pokemon["abilities"]
        if ability["is_hidden"]
    ]

    stats = pokemon["stats"]

    search_parts = [
        (
            f"{name} is a Pokémon with the types "
            f"{join_words(pokemon_types)}."
        ),
        (
            f"It is {pokemon['height_m']} metres tall "
            f"and weighs {pokemon['weight_kg']} kilograms."
        )
    ]

    if normal_abilities:

        if len(normal_abilities) == 1:
            search_parts.append(
                f"Its regular ability is "
                f"{normal_abilities[0]}."
            )

        else:
            search_parts.append(
                f"Its regular abilities are "
                f"{join_words(normal_abilities)}."
            )

    if hidden_abilities:

        if len(hidden_abilities) == 1:
            search_parts.append(
                f"Its hidden ability is "
                f"{hidden_abilities[0]}."
            )

        else:
            search_parts.append(
                f"Its hidden abilities are "
                f"{join_words(hidden_abilities)}."
            )

    stat_fields = [
        ("hp", "HP"),
        ("attack", "attack"),
        ("defense", "defence"),
        ("special-attack", "special attack"),
        ("special-defense", "special defence"),
        ("speed", "speed")
    ]

    for stat_key, stat_name in stat_fields:

        stat_value = stats[stat_key]

        search_parts.append(
            f"Its {stat_name} is "
            f"{describe_stat(stat_value)} "
            f"at {stat_value}."
        )

    return " ".join(search_parts)

def build_move_search_text(move):

    name = readable_name(
        move["name"]
    ).title()

    move_type = readable_name(
        move["type"]
    )

    damage_class = readable_name(
        move["damage_class"]
    )

    search_parts = [
        (
            f"{name} is a {move_type}-type "
            f"{damage_class} move."
        )
    ]

    if move["power"] is None:
        search_parts.append(
            "It has no standard power value."
        )

    else:
        search_parts.append(
            f"It has {move['power']} power."
        )

    if move["accuracy"] is not None:
        search_parts.append(
            f"It has {move['accuracy']} "
            f"percent accuracy."
        )

    if move["pp"] is not None:
        search_parts.append(
            f"It has {move['pp']} power points."
        )

    priority = move["priority"]

    if priority > 0:
        search_parts.append(
            f"It has increased priority "
            f"of {priority}."
        )

    elif priority < 0:
        search_parts.append(
            f"It has reduced priority "
            f"of {priority}."
        )

    else:
        search_parts.append(
            "It has standard priority."
        )

    search_parts.append(
        f"It targets "
        f"{readable_name(move['target'])}."
    )

    effect = move.get("effect")

    if effect:

        # Remove unnecessary line breaks and repeated spaces.
        cleaned_effect = " ".join(
            effect.split()
        )

        search_parts.append(
            f"Its effect is: {cleaned_effect}"
        )

    move_meta = move.get("meta")

    if move_meta:

        ailment = move_meta.get("ailment")

        if ailment and ailment != "none":
            search_parts.append(
                f"It can cause "
                f"{readable_name(ailment)}."
            )

        category = move_meta.get("category")

        if category:
            search_parts.append(
                f"Its effect category is "
                f"{readable_name(category)}."
            )

        flinch_chance = move_meta.get(
            "flinch_chance"
        )

        if flinch_chance:
            search_parts.append(
                f"It has a {flinch_chance} percent "
                f"chance to make the target flinch."
            )

        drain = move_meta.get("drain")

        if drain and drain > 0:
            search_parts.append(
                f"It restores health equal to "
                f"{drain} percent of the damage dealt."
            )

        elif drain and drain < 0:
            search_parts.append(
                f"It causes recoil equal to "
                f"{abs(drain)} percent of the damage dealt."
            )

        healing = move_meta.get("healing")

        if healing:
            search_parts.append(
                f"It restores {healing} percent "
                f"of the user's maximum health."
            )

        minimum_hits = move_meta.get(
            "min_hits"
        )

        maximum_hits = move_meta.get(
            "max_hits"
        )

        if (
            minimum_hits is not None
            and maximum_hits is not None
        ):
            search_parts.append(
                f"It can hit between "
                f"{minimum_hits} and "
                f"{maximum_hits} times."
            )

    return " ".join(search_parts)

def load_json(file_path):

    # Check that the input file exists.
    if not file_path.is_file():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    # Both export files should contain lists.
    if not isinstance(data, list):
        raise TypeError(
            f"{file_path.name} does not contain a list."
        )

    return data

def save_json(data, file_path):

    with file_path.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

def build_search_documents():

    try:
        print(
            "\nReading transformed Pokémon "
            "and move data..."
        )

        pokemon_data = load_json(
            POKEMON_FILE
        )

        move_data = load_json(
            MOVES_FILE
        )

        print(
            "Building Pokémon search documents..."
        )

        pokemon_search_documents = [
            {
                "id": pokemon["id"],
                "name": pokemon["name"],
                "search_text":
                    build_pokemon_search_text(
                        pokemon
                    )
            }
            for pokemon in pokemon_data
        ]

        print(
            "Building move search documents..."
        )

        move_search_documents = [
            {
                "id": move["id"],
                "name": move["name"],
                "search_text":
                    build_move_search_text(
                        move
                    )
            }
            for move in move_data
        ]

        SEARCH_DATA_FOLDER.mkdir(
            parents=True,
            exist_ok=True
        )

        save_json(
            pokemon_search_documents,
            POKEMON_SEARCH_FILE
        )

        save_json(
            move_search_documents,
            MOVE_SEARCH_FILE
        )

        print()
        print("=" * 50)
        print("SEARCH DOCUMENT SUMMARY")
        print(
            f"Pokémon documents created: "
            f"{len(pokemon_search_documents)}"
        )
        print(
            f"Move documents created: "
            f"{len(move_search_documents)}"
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
        OSError
    ) as error:
        print(
            f"Could not build search documents: "
            f"{error}"
        )

        return False


if __name__ == "__main__":
    build_search_documents()