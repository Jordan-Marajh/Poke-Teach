from pymongo import MongoClient
from pymongo.errors import PyMongoError

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "pokemon"

# This is the most tedious part. Here we specify which fields 
# require changes. This should be fixed once you have decided which
# key-value pairs should be dropped entirely and view the remaining
# documents in MongoDB Compass.

# Specify the exact attributes that we wish each Pokemon to keep
def transform_pokemon(collection):

    transformed_pokemon = {
        "_id": collection["_id"],
        "id": collection["id"],
        "name": collection["name"],

        "types": [
            entry["type"]["name"]
            for entry in collection["types"]
        ],

        "stats": {
            entry["stat"]["name"]: entry["base_stat"] 
            for entry in collection["stats"]
        },

        "abilities": [
            {
                "name": entry["ability"]["name"],
                "is_hidden": entry["is_hidden"]
            }
            for entry in collection["abilities"]
        ],

        # PokeAPI records height in decimetres.
        "height_m": collection["height"] / 10,

        "moves": [
            entry["move"]["name"]
            for entry in collection["moves"]
        ],

        # PokeAPI records weight in hectograms.
        "weight_kg": collection["weight"] / 10,

        "sprite_url": collection["sprites"]["front_default"]
    }

    return transformed_pokemon

# Find the English description of a move.
def get_english_effect(effect_entries):

    for entry in effect_entries:
        if entry["language"]["name"] == "en":
            return entry["effect"]

    return None

# Simplify the information stored inside a move's meta field.
def transform_meta(move_meta):

    if move_meta is None:
        return None

    transformed_meta = {}

    for key, value in move_meta.items():

        if key in ["ailment", "category"]:
            transformed_meta[key] = value["name"]

        else:
            transformed_meta[key] = value

    return transformed_meta
    
# Specify the exact attributes that we wish each Move to keep
def transform_move(collection):
    
    transformed_move = {}

    for key, value in collection.items():

        if key in ["damage_class", "target", "type"]:
            transformed_move[key] = value["name"]

        elif key == "effect_entries":
            transformed_move["effect"] = get_english_effect(value)

        elif key == "learned_by_pokemon":
            transformed_move[key] = [
                pokemon["name"]
                for pokemon in value
            ]

        elif key == "meta":
            transformed_move[key] = transform_meta(value)

        else:
            transformed_move[key] = value

    return transformed_move

# Function to transform the data
def transform_data():

    client = MongoClient(MONGO_URI)

    try:
        database = client[DATABASE_NAME]
        pokemon_collection = database["pokemon"]
        move_collection = database["move"]

        ######################### Pokémon

        print("\nTransforming Pokémon documents...")

        pokemon_documents = pokemon_collection.find({})

        pokemon_count = 0

        for pokemon in pokemon_documents:
            transformed_pokemon = transform_pokemon(pokemon)

            pokemon_collection.replace_one(
                {"_id": pokemon["_id"]},
                transformed_pokemon
            )

            pokemon_count += 1

        print(f"Transformed {pokemon_count} Pokémon documents.")

        ######################### Moves

        print("\nTransforming move documents...")

        move_documents = move_collection.find({})

        move_count = 0

        for move in move_documents:
            transformed_move = transform_move(move)

            move_collection.replace_one(
                {"_id": move["_id"]},
                transformed_move
            )

            move_count += 1

        print(f"Transformed {move_count} move documents.")

        #########################

    except PyMongoError as error:
        print(f"MongoDB error: {error}")

    except (KeyError, TypeError) as error:
        print(f"Error transforming data: {error}")

    finally:
        client.close()