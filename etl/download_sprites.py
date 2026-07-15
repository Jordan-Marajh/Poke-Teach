# Simple script to download all Pokémon default front sprites from PokeAPI
# Saves images as {pokemon_id}.png in the 'sprites' folder
# Dynamic script - automatically gets the total number of Pokémon

import json
from pathlib import Path

import requests

# Create sprites directory
PROJECT_FOLDER = Path(__file__).resolve().parent.parent
EXPORT_FOLDER = PROJECT_FOLDER / "exports"

POKEMON_FILE = EXPORT_FOLDER / "pokemon.json"
SPRITE_FOLDER = EXPORT_FOLDER / "sprites"

def clear_sprite_folder():

    # Create the sprites folder if it does not already exist.
    SPRITE_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    # Delete any old sprite files.
    for file_path in SPRITE_FOLDER.iterdir():
        if file_path.is_file():
            file_path.unlink()

def download_sprites():

    # Check that pokemon.json exists.
    if not POKEMON_FILE.is_file():
        print(f"File not found: {POKEMON_FILE}")
        return False

    # Read the transformed Pokémon data.
    try:
        with POKEMON_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:
            pokemon_data = json.load(file)

    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not read Pokémon data: {error}")
        return False

    # pokemon.json should contain a list of Pokémon.
    if not isinstance(pokemon_data, list):
        print("pokemon.json does not contain a list.")
        return False

    total_pokemon = len(pokemon_data)

    if total_pokemon == 0:
        print("No Pokémon were found in pokemon.json.")
        return False

    # Remove sprites left over from previous pipeline runs.
    clear_sprite_folder()

    print(f"\nStarting download of {total_pokemon} Pokémon sprites...")
    print(f"Saving to: {SPRITE_FOLDER.absolute()}")

    success_count = 0
    fail_count = 0

    for count, pokemon in enumerate(pokemon_data,start=1):
        pokemon_id = pokemon.get("id")
        pokemon_name = pokemon.get("name")
        sprite_url = pokemon.get("sprite_url")

        if pokemon_id is None or pokemon_name is None:
            print(f"\nInvalid Pokémon entry at position {count}.")
            fail_count += 1

        elif not sprite_url:
            print(f"\nNo sprite URL found for {pokemon_name}.")
            fail_count += 1

        else:
            try:
                response = requests.get(
                    sprite_url,
                    timeout=60
                )

                response.raise_for_status()

                file_path = (
                    SPRITE_FOLDER /
                    f"{pokemon_id}.png"
                )

                file_path.write_bytes(
                    response.content
                )

                success_count += 1

            except requests.exceptions.RequestException as error:
                print(
                    f"\nCould not download the sprite "
                    f"for {pokemon_name}: {error}"
                )

                fail_count += 1

            except OSError as error:
                print(
                    f"\nCould not save the sprite "
                    f"for {pokemon_name}: {error}"
                )

                fail_count += 1

        print(
            f"\rDownloading sprites: "
            f"{count}/{total_pokemon}",
            end=""
        )

    print()
    print("="*50)
    print("DOWNLOAD SUMMARY")
    print(f"Successfully downloaded: {success_count}")
    print(f"Failed or skipped: {fail_count}")
    print(f"Saved to: {SPRITE_FOLDER.absolute()}")

    return fail_count == 0

if __name__ == "__main__":
    download_sprites()