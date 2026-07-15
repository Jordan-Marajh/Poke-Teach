# Simple script to download all Pokémon default front sprites from PokeAPI
# Saves images as {pokemon_id}.png in the 'sprites' folder
# Dynamic script - automatically gets the total number of Pokémon

import requests
import time
from pathlib import Path

# Create sprites directory
SPRITE_DIR = Path('sprites')
SPRITE_DIR.mkdir(exist_ok=True)

def get_total_pokemon_count():
   
# Get the total number of Pokémon from the PokeAPI
    response = requests.get("https://pokeapi.co/api/v2/pokemon", timeout=60)
    response.raise_for_status()
    data = response.json()
    total = data['count']
    print(f"Found {total} Pokémon in the API")
    return total

def download_all_pokemon_sprites():
    # Download sprites for all Pokémon from PokeAPI
    # Automatically determines the total number
    
    # Get the total count dynamically
    TOTAL_POKEMON = get_total_pokemon_count()
    
    print(f"Starting download of all {TOTAL_POKEMON} Pokémon sprites...")
    print(f"Saving to: {SPRITE_DIR.absolute()}")
    print("="*50)
    
    success_count = 0
    fail_count = 0
    
    for pokemon_id in range(1, TOTAL_POKEMON + 1):
        try:
            # Fetch Pokémon data from PokeAPI
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}", timeout=60)
            
            # If Pokémon doesn't exist, skip it
            if response.status_code == 404:
                print(f"Pokémon {pokemon_id} not found - skipping")
                fail_count += 1
                continue
            
            response.raise_for_status()
            data = response.json()
            
            # Get the default front sprite URL
            sprite_url = data['sprites']['front_default']
            
            # Some Pokémon might not have a sprite (rare, but possible)
            if not sprite_url:
                print(f"No sprite for {data['name']} (ID: {pokemon_id})")
                fail_count += 1
                continue
            
            # Download the sprite image
            img_response = requests.get(sprite_url, timeout=60)
            img_response.raise_for_status()
            
            # Save as {pokemon_id}.png
            file_path = SPRITE_DIR / f"{pokemon_id}.png"
            with open(file_path, 'wb') as f:
                f.write(img_response.content)
            
            success_count += 1
            print(f"Downloaded: {data['name']:15} (ID: {pokemon_id:4})")
            
            # Small delay to be respectful to the API
            time.sleep(0.2)
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading Pokémon {pokemon_id}: {e}")
            fail_count += 1
            continue
    
    # Print summary
    print("\n" + "="*50)
    print("DOWNLOAD SUMMARY")
    print("="*50)
    print(f"Successfully downloaded: {success_count} sprites")
    print(f"Failed/Skipped: {fail_count} sprites")
    print(f"Saved to: {SPRITE_DIR.absolute()}")
    
    # Count files in folder
    files = list(SPRITE_DIR.glob('*.png'))
    print(f"Total PNG files in folder: {len(files)}")

if __name__ == "__main__":
    download_all_pokemon_sprites()