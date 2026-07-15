# Poke-Teach ETL Pipeline
## Overview
Loading Pokémon data from PokeAPI using Pymongo and hosting on S3.

## Table of Contents
- [Pipeline Worflow](#pipeline-workflow)
- [Data Model](#data-model)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Technical Decisions](#technical-decisions)
- [Future Improvements](#future-improvements)
- [Team Members](#team-members)
- [License](#license)

---

## Pipeline Workflow
![pipeline workflow](./images/pipeline-workflow.png)

## Data Model
### Pokémon Collection

| Field | Type | Description | Reasoning |
|-------|------|-------------|-----------|
| `id` | Integer | Unique Pokémon ID | Primary key and API reference |
| `name` | String | Pokémon name | Primary search field |
| `types` | Array | Pokémon types (e.g., Fire, Water) | Type-based filtering and recommendations |
| `abilities` | Array | Abilities with name and effect | Searchable field for ability queries |
| `height` | Integer | Height in decimeters | Physical characteristic filter |
| `weight` | Integer | Weight in hectograms | Physical characteristic filter |
| `stats` | Object | Base stats (HP, Attack, Defense, etc.) | Battle calculations and comparisons |
| `moves` | Array | List of learnable move names | Relationship mapping to moves collection |
| `sprites` | Object | URLs to Pokémon images; kept only `front_default` | Visual reference for future UI |

---

### Moves Collection

| Field | Type | Description | Reasoning |
|-------|------|-------------|-----------|
| `id` | Integer | Unique move ID | Primary key and API reference |
| `name` | String | Move name | Primary search field |
| `type` | String | Move type (e.g., Fire, Water) | Type-matching recommendations |
| `power` | Integer | Base power (null for status moves) | Damage calculation and recommendations |
| `accuracy` | Integer | Accuracy percentage (null for always-hit) | Move reliability assessment |
| `pp` | Integer | Power points (usage limit) | Usage limitation for strategy |
| `priority` | Integer | Move priority (negative/positive) | Turn order determination |
| `damage_class` | String | "physical", "special", or "status" | Stat usage categorization |
| `target` | String | Target selection (e.g., "selected-pokemon") | Strategic considerations |
| `effect_entries` | Object | Short effect description in English | Semantic search descriptions |
| `meta` | Object | Additional metadata (ailment, category, etc.) | Advanced filtering options |
| `learned_by_pokemon` | Array | List of Pokémon that learn this move | Relationship mapping to Pokémon collection |

### Data Selection Rationale
We worked backwards from our desired semantic search and recommendation queries to determine which fields to keep:
- **Search requirements**: Need name, type, and effect descriptions for text matching
- **Recommendation requirements**: Need stats, type matchups, and move effectiveness for suggesting optimal Pokémon/Moves

## Setup Instructions

### Prerequisites
- Python 3.8+
- MongoDB (local or Atlas)
- AWS Account with S3 access
- pip (Python package manager)

### Python Libraries
See `requirements.txt`

Main libraries used:
- `pymongo`,`requests`, `boto3`  for ETL
- `sentence-transformers`, `scikit-learn`, `faiss`, `numpy` for Semantic Search

### Installation

1. Clone the repository
```bash
git clone [your-repo-url]
cd [repo-name]
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Start MongoDB (optional)
```bash
# Start MongoDB (if not already running)
mongod
```

### Downloading Sprites
The project includes a utility script to download all Pokémon `default_front` sprites for potential visual display.

Why we included this:
- The script dynamically gets the total number of Pokémon from the API, so it works with any current or future Pokémon count
- No MongoDB required - downloads directly from PokeAPI
- Saves images as {pokemon_id}.png for easy lookup

To run:
```bash
pip install requests  # If not already installed
python download_sprites.py
```

> This will create a sprites/ folder and download all available Pokémon sprites; it includes a small delay between requests to respect PokeAPI's rate limits.

## Usage

### ETL Pipeline
```bash
# Run the ETL pipeline
python main.py
```

Details of the pipeline:

```bash
# Extract data from Pokemon API into MongoDB
python import_poke_data.py

# Keep relevant fields from the Pokemon and Move collections
python drop_poke_data.py

# Filtering and reformatting to flatten the data 
python transform_poke_data.py

# Upload to S3
python upload_s3.py
```
![MongoDB API call?](/images/.png)

### Semantic Search

Instructions on how to use the transformed data to search:
- 
- 
- 

![MongoDB terminal output](/images/.png)


## Technical Decisions

### Why Pokémon API?
- Rich dataset with clear relationships
- Well-documented REST API
- No authentication required
- Large community of users

### Why These Collections?
- Pokémon and Moves provide natural relationship (Pokémon use Moves)
- Easy to demonstrate semantic search (e.g., "show me fire-type Pokémon with high speed")
- Can extend to include other collections if needed

### Data Transformation Approach
- Normalised nested objects from API into flat documents for MongoDB
- Used existing JSON structure to maintain relationships


## Future Improvements
- Add more Pokémon collections (Abilities, Items, etc.)
- Implement more sophisticated recommendation algorithms
- Add caching layer for API calls
- Create a web interface for search

## Team Members
- Jordan Marajh
- Sarah Hasan

## License
MIT License