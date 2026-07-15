# Import dependencies from other files for readability

from import_poke_data import import_data
from drop_poke_data import drop_data
from transform_poke_data import transform_data
from upload_s3 import upload_data

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

    print("2. Transforming MongoDB data...\n")
    transform_data()
    print(f"------------------------\n")

    print("3. Uploading JSON files and sprites to S3...\n")
    upload_data()
    print(f"------------------------\n")

    print("Pokémon ETL pipeline completed successfully.")

if __name__ == "__main__":
    main()