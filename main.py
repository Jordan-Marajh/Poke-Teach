# Import dependencies from other files for readability

from etl.import_poke_data import import_data
from etl.drop_poke_data import drop_data
from etl.transform_poke_data import transform_data
from etl.download_sprites import download_sprites
from etl.upload_s3 import upload_to_s3

# Main call

def main():
    
    print("\nStarting Pokémon ETL pipeline...")
    print(f"------------------------\n")

    print("1. Extracting PokeAPI data and loading it into MongoDB...\n")
    import_data()
    print(f"------------------------\n")

    print("2. Dropping specified fields...\n")
    drop_data()
    print(f"------------------------\n")

    print("3. Transforming MongoDB data...\n")
    transform_data()
    print(f"------------------------\n")

    print("4. Downloading Pokémon sprites...\n")
    download_sprites()
    print(f"------------------------\n")

    print("5. Uploading JSON files and sprites to S3...\n")
    upload_to_s3()
    print(f"------------------------\n")

    print("Pokémon ETL pipeline completed successfully.")

if __name__ == "__main__":
    main()