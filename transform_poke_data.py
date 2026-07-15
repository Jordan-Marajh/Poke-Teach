from pymongo import MongoClient

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

        "stats": [
            {entry["stat"]["name"]: entry["base_stat"]}
            for entry in collection["stats"]
        ],

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
        "weight_m": collection["weight"] / 10,

        "sprite_url": collection["sprites"]["front_default"]
    }
    
# Specify the exact attributes that we wish each Move to keep
def transform_move(collection):
    
    move_meta = collection.get("meta")

    # Specify the meta group if not empty, otherwise produce None
    if move_meta is not None:
        transformed_meta = {}

        for key, value in move_meta.items():
            if key in ["ailment", "category"]:
                transformed_meta[key] = value["name"]
            else:
                transformed_meta[key] = value
    else:
        trasnsformed_meta = None

# Function to transform the data
def transform_data():
    pass