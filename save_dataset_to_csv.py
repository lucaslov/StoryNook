import tensorflow_datasets as tfds
import json

# Load the movies dataset
movies = tfds.load('movielens/100k-movies', split="train")

# Prepare a list to hold all movie data
movies_list = []

for movie in tfds.as_numpy(movies):
    movie_id = movie['movie_id'].decode('utf-8')
    movie_title = movie['movie_title'].decode('utf-8')
    genres = [str(g) for g in movie['movie_genres']]  # Convert genre IDs to strings

    # Create a dictionary for each movie
    movie_dict = {
        "movie_id": movie_id,
        "movie_title": movie_title,
        "genres": genres
    }
    movies_list.append(movie_dict)

# Save the movies data to a JSON file
with open('movies.json', 'w', encoding='utf-8') as f:
    json.dump(movies_list, f)
