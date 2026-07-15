from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "pokemon"

# Specifying which Pokemon fields to keep. Can be edited later.

POKEMON_FIELDS_TO_KEEP = {
    "_id",
    "id",
    "name",
    "abilities",
    "height",
    "weight",
    "moves",
    "sprites",
    "stats",
    "types"
}

# Specifying which Move fields to keep. Can be edited later.

MOVE_FIELDS_TO_KEEP = {
    "_id",
    "id",
    "name",
    "accuracy",
    "damage_class",
    "effect_entries",
    "learned_by_pokemon",
    "meta",
    "power",
    "pp",
    "priority",
    "target",
    "type"
}

# Function to remove unlisted fields in a collection from each document.

def remove_fields(collection, fields_to_keep):
    
    document = collection.find_one()

    # Simple error catch for empty collections.
    if document is None:
        print(f"No documents found in the '{collection.name}' collection.")

    existing_fields = set(document.keys())
    fields_to_drop = existing_fields - fields_to_keep

    # Simple error catch for no fields needing to be removed.
    if not fields_to_drop:
        print(
            f"No fields need to be removed from "
            f"the '{collection.name}' collection."
        )
        return
    
    # Record which fields to unset.
    unset_fields = {
        field: ""
        for field in fields_to_drop
    } # this syntax is a miracle of Python, otherwise it would look more complex.

    # Unset fields according to above list.
    result = collection.update_many(
        {},
        {
            "$unset": unset_fields
        }
    )

    print(f"\nCollection: {collection.name}")
    print(f"Fields removed: {sorted(fields_to_drop)}")
    print(f"Documents updated: {result.modified_count}")

def drop_data():
    client = MongoClient(MONGO_URI)

    try:
        database = client[DATABASE_NAME]

        pokemon_collection = database["pokemon"]
        move_collection = database["move"]

        print("Removing unwanted Pokémon fields...")

        remove_fields(
            pokemon_collection,
            POKEMON_FIELDS_TO_KEEP
        )

        print("\nRemoving unwanted move fields...")

        remove_fields(
            move_collection,
            MOVE_FIELDS_TO_KEEP
        )

        print("\nData removed successfully.")

    finally:
        client.close()

