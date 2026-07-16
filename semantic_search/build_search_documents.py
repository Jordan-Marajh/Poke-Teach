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

def describe_stat(stat_name, value):

    if value >= 120:
        level = "very high"

    elif value >= 90:
        level = "high"

    elif value >= 60:
        level = "moderate"

    elif value >= 30:
        level = "low"

    else:
        level = "very low"

    return (
        f"{level} {stat_name} "
        f"with a value of {value}"
    )

def build_pokemon_tags(pokemon):

    stats = pokemon["stats"]

    hp = stats["hp"]
    attack = stats["attack"]
    defence = stats["defense"]
    special_attack = stats["special-attack"]
    special_defence = stats["special-defense"]
    speed = stats["speed"]

    tags = []

    # Speed descriptions.
    if speed >= 120:
        tags.extend([
            "extremely fast",
            "very high speed"
        ])

    elif speed >= 90:
        tags.extend([
            "fast",
            "high speed"
        ])

    elif speed <= 30:
        tags.extend([
            "extremely slow",
            "very low speed"
        ])

    elif speed < 60:
        tags.extend([
            "slow",
            "low speed"
        ])

    # Offensive descriptions.
    if attack >= 100:
        tags.extend([
            "strong physical attacker",
            "high physical attack"
        ])

    if special_attack >= 100:
        tags.extend([
            "strong special attacker",
            "high special attack"
        ])

    # Defensive descriptions.
    if defence >= 100:
        tags.extend([
            "physically defensive",
            "high physical defence"
        ])

    if special_defence >= 100:
        tags.extend([
            "specially defensive",
            "high special defence"
        ])

    if hp >= 100:
        tags.extend([
            "high health",
            "high HP"
        ])

    # General battle descriptions.
    if (
        hp >= 80
        and (
            defence >= 90
            or special_defence >= 90
        )
    ):
        tags.extend([
            "bulky",
            "durable"
        ])

    if (
        attack >= 100
        or special_attack >= 100
    ) and (
        defence < 60
        and special_defence < 60
    ):
        tags.extend([
            "powerful but fragile",
            "glass cannon"
        ])

    # Physical size descriptions.
    height = pokemon["height_m"]
    weight = pokemon["weight_kg"]

    if height <= 0.5:
        tags.append("small")

    elif height >= 2:
        tags.append("tall")

    if weight <= 10:
        tags.append("lightweight")

    elif weight >= 100:
        tags.append("heavy")

    return tags

def build_pokemon_search_text(pokemon):

    name = readable_name(
        pokemon["name"]
    ).title()

    pokemon_types = [
        readable_name(pokemon_type)
        for pokemon_type in pokemon["types"]
    ]

    regular_abilities = [
        readable_name(ability["name"])
        for ability in pokemon["abilities"]
        if not ability["is_hidden"]
    ]

    hidden_abilities = [
        readable_name(ability["name"])
        for ability in pokemon["abilities"]
        if ability["is_hidden"]
    ]

    all_abilities = (
        regular_abilities +
        hidden_abilities
    )

    stats = pokemon["stats"]

    tags = build_pokemon_tags(
        pokemon
    )

    search_parts = [
        f"{name}.",
        (
            f"{join_words(pokemon_types)} "
            f"type Pokémon."
        )
    ]

    if tags:
        search_parts.append(
            f"Battle and physical traits: "
            f"{', '.join(tags)}."
        )

    stat_descriptions = [
        describe_stat(
            "HP",
            stats["hp"]
        ),
        describe_stat(
            "physical attack",
            stats["attack"]
        ),
        describe_stat(
            "physical defence",
            stats["defense"]
        ),
        describe_stat(
            "special attack",
            stats["special-attack"]
        ),
        describe_stat(
            "special defence",
            stats["special-defense"]
        ),
        describe_stat(
            "speed",
            stats["speed"]
        )
    ]

    search_parts.append(
        "Stats: " +
        "; ".join(stat_descriptions) +
        "."
    )

    if all_abilities:
        search_parts.append(
            f"Abilities: "
            f"{join_words(all_abilities)}."
        )

    search_parts.append(
        f"Height {pokemon['height_m']} metres. "
        f"Weight {pokemon['weight_kg']} kilograms."
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
        f"{name}.",
        (
            f"{move_type} type "
            f"{damage_class} move."
        )
    ]

    power = move.get("power")

    if (
        damage_class == "status"
        or power is None
    ):
        search_parts.extend([
            "Non-damaging move.",
            "Status move."
        ])

    else:
        search_parts.append(
            f"Damaging move with "
            f"{power} power."
        )

        if power >= 120:
            search_parts.append(
                "Extremely powerful attack."
            )

        elif power >= 90:
            search_parts.append(
                "Powerful attack."
            )

        elif power < 50:
            search_parts.append(
                "Low-power attack."
            )

    accuracy = move.get("accuracy")

    if accuracy is None:
        search_parts.append(
            "No standard accuracy value."
        )

    else:
        search_parts.append(
            f"{accuracy} percent accuracy."
        )

    pp = move.get("pp")

    if pp is not None:
        search_parts.append(
            f"{pp} power points."
        )

    priority = move.get("priority", 0)

    if priority > 0:
        search_parts.append(
            "Increased-priority move."
        )

    elif priority < 0:
        search_parts.append(
            "Reduced-priority move."
        )

    target = move.get("target")

    if target:
        search_parts.append(
            f"Targets "
            f"{readable_name(target)}."
        )

    effect = move.get("effect")

    if effect:

        cleaned_effect = " ".join(
            effect.split()
        )

        effect_chance = move.get(
            "effect_chance"
        )

        if effect_chance is not None:
            cleaned_effect = (
                cleaned_effect.replace(
                    "$effect_chance",
                    str(effect_chance)
                )
            )

        search_parts.append(
            f"Effect: {cleaned_effect}"
        )

    move_meta = move.get("meta") or {}

    ailment = move_meta.get("ailment")

    if ailment and ailment != "none":
        readable_ailment = readable_name(
            ailment
        )

        search_parts.extend([
            f"Can cause {readable_ailment}.",
            f"{readable_ailment} inflicting move."
        ])

    flinch_chance = move_meta.get(
        "flinch_chance"
    )

    if flinch_chance:
        search_parts.extend([
            "Can make the target flinch.",
            (
                f"{flinch_chance} percent "
                f"flinch chance."
            )
        ])

    healing = move_meta.get("healing")

    if healing and healing > 0:
        search_parts.extend([
            "Healing move.",
            "Restores the user's health.",
            (
                f"Restores {healing} percent "
                f"of maximum health."
            )
        ])

    drain = move_meta.get("drain")

    if drain and drain > 0:
        search_parts.extend([
            "Health-draining move.",
            "Restores health from damage dealt."
        ])

    elif drain and drain < 0:
        search_parts.extend([
            "Recoil move.",
            "Damages the user through recoil."
        ])

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
        search_parts.extend([
            "Multi-hit move.",
            (
                f"Hits between "
                f"{minimum_hits} and "
                f"{maximum_hits} times."
            )
        ])

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