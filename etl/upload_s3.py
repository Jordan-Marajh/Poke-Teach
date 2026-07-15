# Upload transformed JSON files and Pokémon sprites to AWS S3.

from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Find the project root folder.
PROJECT_FOLDER = Path(__file__).resolve().parent.parent

EXPORT_FOLDER = PROJECT_FOLDER / "exports"
SPRITE_FOLDER = EXPORT_FOLDER / "sprites"

POKEMON_FILE = EXPORT_FOLDER / "pokemon.json"
MOVES_FILE = EXPORT_FOLDER / "moves.json"

BUCKET_NAME = "se-data-with-ai-etl-project"
AWS_REGION = "eu-central-1"

# Replace this with the folder assigned to your group in the shared bucket.
S3_PREFIX = "Poke-Teach"


def upload_file(s3_client, local_file, s3_key):

    # Check that the local file exists before attempting the upload.
    if not local_file.is_file():
        print(f"\nFile not found: {local_file}")
        return False

    try:
        s3_client.upload_file(
            str(local_file),
            BUCKET_NAME,
            s3_key
        )

        print(f"\nUploaded: {local_file.name}")
        print(f"S3 location: s3://{BUCKET_NAME}/{s3_key}")

        return True

    except (BotoCoreError, ClientError) as error:
        print(f"\nCould not upload {local_file.name}: {error}")
        return False


def upload_json_files(s3_client):

    print(f"\nUploading JSON files...")

    json_files = [
        POKEMON_FILE,
        MOVES_FILE
    ]

    success_count = 0
    fail_count = 0

    for file_path in json_files:
        s3_key = (
            f"{S3_PREFIX}/data/{file_path.name}"
        )

        if upload_file(
            s3_client,
            file_path,
            s3_key
        ):
            success_count += 1

        else:
            fail_count += 1

    return success_count, fail_count


def upload_sprites(s3_client):

    if not SPRITE_FOLDER.is_dir():
        print(f"\nSprite folder not found: {SPRITE_FOLDER}")
        return 0, 0

    sprite_files = sorted(
        SPRITE_FOLDER.glob("*.png")
    )

    total_sprites = len(sprite_files)

    if total_sprites == 0:
        print(f"\nNo sprite files were found.")
        return 0, 0

    print(f"\nUploading {total_sprites} sprites...")

    success_count = 0
    fail_count = 0

    for count, file_path in enumerate(
        sprite_files,
        start=1
    ):
        s3_key = (
            f"{S3_PREFIX}/sprites/{file_path.name}"
        )

        try:
            s3_client.upload_file(
                str(file_path),
                BUCKET_NAME,
                s3_key
            )

            success_count += 1

        except (BotoCoreError, ClientError) as error:
            print(
                f"\nCould not upload "
                f"{file_path.name}: {error}"
            )

            fail_count += 1

        print(
            f"\rUploading sprites: "
            f"{count}/{total_sprites}",
            end=""
        )

    print()

    return success_count, fail_count


def upload_to_s3():

    # Remove accidental slashes from the beginning or end.
    global S3_PREFIX
    S3_PREFIX = S3_PREFIX.strip("/")

    s3_client = boto3.client(
        "s3",
        region_name=AWS_REGION
    )

    print(f"Bucket: {BUCKET_NAME}")
    print(f"Group folder: {S3_PREFIX}")

    json_success, json_failed = upload_json_files(
        s3_client
    )

    sprite_success, sprite_failed = upload_sprites(
        s3_client
    )

    print()
    print("=" * 50)
    print("UPLOAD SUMMARY")
    print(f"JSON files uploaded: {json_success}")
    print(f"JSON files failed: {json_failed}")
    print(f"Sprites uploaded: {sprite_success}")
    print(f"Sprites failed: {sprite_failed}")