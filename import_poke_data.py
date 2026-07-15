import requests
from pymongo import MongoClient
from pymongo.errors import PyMongoError

POKE_API_URL = "https://pokeapi.co/api/v2" # URL for online API

def get_data(group):

    # Download all pokemon documents from PokeAPI as a JSON file. 

    response = requests.get(
        f"{POKE_API_URL}/{group}",
        params={"limit": 25},
        timeout=60
    )
    response.raise_for_status()

    return response.json()["results"]

def replace_urls(collection):

    # Replace URLs with Pokemon information

    entries = collection.find(
        {"url": {'$exists': True}},
        {"url": 1}
    )

    for entry in entries:
        response = requests.get(entry["url"], timeout=60)
        response.raise_for_status()

        details = response.json()

        collection.replace_one(
            {"_id": entry["_id"]},
            details
        )

## Main loop for task using the above functions.

def import_data():
    client = MongoClient("mongodb://localhost:27017/") # IP and Port for MongoDB to use

    database = client["pokemon"]
    pokemon_collection = database["pokemon"]
    move_collection = database["move"]

    # Clear existing documents before importing fresh data. Moving this caused problems!!
    pokemon_collection.delete_many({})
    move_collection.delete_many({})
    
    ######################### Pokemon

    print("Downloading Pokémon list...")
    pokemon_data = get_data("pokemon")

    pokemon_result = pokemon_collection.insert_many(pokemon_data)

    print(f"Inserted {len(pokemon_result.inserted_ids)} Pokémon documents.")

    print("Replacing Pokémon URLs with detailed data...")
    replace_urls(pokemon_collection)

    print(
        "Pokémon documents currently in MongoDB:",
        pokemon_collection.count_documents({})
    )

    ######################### Moves

    print("Downloading move list...")
    moves_data = get_data("move")

    move_result = move_collection.insert_many(moves_data)

    print(f"Inserted {len(move_result.inserted_ids)} move documents.")

    print("Replacing Move URLs with detailed data...")
    replace_urls(move_collection)

    print(
        "Move documents currently in MongoDB:",
        move_collection.count_documents({})
    )

    #########################

    client.close()