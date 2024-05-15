from typing import Union, List, Dict
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi_pagination import Page, add_pagination, paginate
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import json
import csv
import uvicorn

# Load the trained model
model = tf.keras.models.load_model('my_movielens_model')

# Initialize and load the movie vocabulary
movie_id_vocabulary = tf.keras.layers.StringLookup()
with open('movie_vocabulary.txt', 'r', encoding='utf-8') as f:
    vocab = [line.strip() for line in f]
movie_id_vocabulary.set_vocabulary(vocab)

# Load poster URL mappings from CSV
poster_url_map = {}
with open('posters.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        movie_id = row[0]  # Ensure this is a string to match your data and model
        poster_url = row[1]
        poster_url_map[movie_id] = poster_url

app = FastAPI()

# Define CORS origins for local development
origins = [
    "http://localhost",
    "http://localhost:5173",
]

# Apply CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the MovieModel using the actual data keys directly
class MovieModel(BaseModel):
    id: str  # Direct usage without alias
    title: str  # Direct usage without alias
    posterPath: str  # Will be set dynamically with the correct poster path

class RecommendationRequest(BaseModel):
    movie_ids: List[str] = Field(default=[], description="List of movie IDs for which to get recommendations.")

# Load the movie data and create MovieModel instances
movies = []
movie_map = {}
with open('movies.json', 'r', encoding='utf-8') as f:
    movies_data = json.load(f)
    for movie in movies_data:
        # Fetch the poster URL from the map or use a default if not found
        poster_path = poster_url_map.get(movie['movie_id'], "https://example.com/default_poster.jpg")
        # Create MovieModel instances
        movie_instance = MovieModel(id=movie['movie_id'], title=movie['movie_title'], posterPath=poster_path)
        movies.append(movie_instance)
        movie_map[movie['movie_id']] = {
            "title": movie['movie_title'],
            "posterPath": poster_path
        }

@app.get("/movies/{movie_id}")
def get_movie(movie_id: str):
    # Fetch a single movie by ID or raise a 404 if not found
    movie = next((movie for movie in movies if movie.id == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.get('/movies')
def get_movies(q: Union[str, None] = None) -> Page[MovieModel]:
    # Optionally filter movies by query string or return all
    if q:
        filtered_movies = [movie for movie in movies if q.lower() in movie.title.lower()]
        return paginate(filtered_movies)
    return paginate(movies)

def recommend_movies(input_movie_ids):
    # Convert movie IDs to tensor and compute embedding similarities
    input_movie_ids_tensor = movie_id_vocabulary(tf.constant(input_movie_ids, dtype=tf.string))
    input_movie_embeddings = model.movie_embed(input_movie_ids_tensor)
    
    mean_embedding = tf.reduce_mean(input_movie_embeddings, axis=0, keepdims=True)
    all_movie_embeddings = model.movie_embed(tf.range(start=0, limit=movie_id_vocabulary.vocabulary_size(), dtype=tf.int32))

    similarity = tf.keras.losses.cosine_similarity(mean_embedding, all_movie_embeddings)
    top_indices = tf.argsort(similarity, direction='DESCENDING')[:10]

    # Fetch and decode the top recommended movie IDs
    vocab = movie_id_vocabulary.get_vocabulary()
    top_movie_ids = tf.gather(vocab, top_indices)
    return [mid.decode('utf-8') for mid in top_movie_ids.numpy()]

@app.post("/recommend")
async def get_recommendations(request: RecommendationRequest):
    # Use the parsed movie_ids list from the request body
    movie_ids_list = request.movie_ids
    if not movie_ids_list:
        raise HTTPException(status_code=400, detail="No movie IDs provided for recommendations.")
    
    recommendations = recommend_movies(movie_ids_list)
    
    # Map ids to posterPath and title
    recommended_movies = [
        {
            "title": movie_map.get(movie_id, {}).get("title", "Unknown Title"),
            "posterPath": movie_map.get(movie_id, {}).get("posterPath")
        } 
        for movie_id in recommendations
    ]

    return {"recommended_movies": recommended_movies}

add_pagination(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)