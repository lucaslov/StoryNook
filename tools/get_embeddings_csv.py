import csv
import requests
import statistics
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# TMDB API details
api_key = os.getenv('TMDB_API_KEY')
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {api_key}"
}

current_script_dir = os.path.dirname(os.path.abspath(__file__))

base_path = current_script_dir.rsplit('/', 1)[0] + '/data/ml-20m/'
# File paths
movies_file = base_path + 'movies.csv'
ratings_file = base_path + 'ratings.csv'
tags_file = base_path + 'tags.csv'
links_file = base_path + 'links.csv'
output_csv = 'combined_for_embeddings.csv'
output_json = 'tmdb_responses.json'

# Read movies data
movies = {}
with open(movies_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        movie_id = int(row['movieId'])
        movies[movie_id] = {
            'title': row['title'],
            'genres': row['genres'],
            'median_rating': None,
            'tags': [],
            'description': None
        }

# Calculate median ratings
ratings = {}
with open(ratings_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        movie_id = int(row['movieId'])
        rating = float(row['rating'])
        if movie_id not in ratings:
            ratings[movie_id] = []
        ratings[movie_id].append(rating)

for movie_id, rating_list in ratings.items():
    median_rating = statistics.median(rating_list)
    if movie_id in movies:
        movies[movie_id]['median_rating'] = median_rating

# Aggregate tags
tags = {}
with open(tags_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        movie_id = int(row['movieId'])
        tag = row['tag']
        if movie_id not in tags:
            tags[movie_id] = []
        tags[movie_id].append(tag)

for movie_id, tag_list in tags.items():
    tags_str = '|'.join(tag_list)
    if movie_id in movies:
        movies[movie_id]['tags'] = tags_str

# Initialize CSV and JSON files
if not os.path.exists(output_csv):
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['movieId', 'title', 'genres', 'median_rating', 'tags', 'description'])

tmdb_responses = []
if os.path.exists(output_json):
    with open(output_json, 'r', encoding='utf-8') as f:
        tmdb_responses = json.load(f)

# Fetch descriptions from TMDB and write intermediate results
try:
    with open(links_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            movie_id = int(row['movieId'])
            tmdb_id = row['tmdbId']
            if movie_id in movies and movies[movie_id]['description'] is None:
                url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?language=en-US"
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    movies[movie_id]['description'] = data.get('overview', '')
                    tmdb_responses.append(data)
                    # Write to CSV
                    with open(output_csv, 'a', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile, delimiter=';')
                        writer.writerow([
                            movie_id,
                            movies[movie_id]['title'],
                            movies[movie_id]['genres'],
                            movies[movie_id]['median_rating'],
                            movies[movie_id]['tags'],
                            movies[movie_id]['description']
                        ])
                    # Write to JSON
                    with open(output_json, 'w', encoding='utf-8') as jsonfile:
                        json.dump(tmdb_responses, jsonfile, ensure_ascii=False, indent=4)
                else:
                    print(f"Failed to fetch data for TMDB ID: {tmdb_id}")
except Exception as e:
    print(f"An error occurred: {e}")
    print(f"Last processed movieId: {movie_id}")