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
    if not import_data():
        print("\nPipeline stopped during data import.")
        return False
    print(f"------------------------\n")

    print("2. Dropping specified fields...\n")
    if not drop_data():
        print("\nPipeline stopped during field removal.")
        return False
    print(f"------------------------\n")

    print("3. Transforming MongoDB data...\n")
    if not transform_data():
        print("\nPipeline stopped during transformation.")
        return False
    print(f"------------------------\n")

    print("4. Downloading Pokémon sprites...\n")
    if not download_sprites():
        print("\nPipeline stopped during sprite download.")
        return False
    print(f"------------------------\n")

    print("5. Uploading JSON files and sprites to S3...\n")
    if not upload_to_s3():
        print("\nPipeline stopped during the S3 upload.")
        return False
    print(f"------------------------\n")

    print("Pokémon ETL pipeline completed successfully.")
    return True

if __name__ == "__main__":
    main()