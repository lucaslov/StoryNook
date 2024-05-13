from typing import Union
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi_pagination import Page, add_pagination, paginate
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import tensorflow_datasets as tfds
import json
import sys
import uvicorn
app = FastAPI()

model = tf.keras.models.load_model('my_movielens_model')
movie_id_vocabulary = tf.keras.layers.StringLookup()
with open('movie_vocabulary.txt', 'r', encoding='utf-8') as f:
    vocab = [line.strip() for line in f]
movie_id_vocabulary.set_vocabulary(vocab)

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MovieModel(BaseModel):
    id: str = Field(alias='movie_id')
    title: str = Field(alias='movie_title')
    posterPath: str = Field(default="https://example.com/default_poster.jpg")

# Load the movie data from the JSON file
with open('movies.json', 'r', encoding='utf-8') as f:
    movies_data = json.load(f)
    
movies = [MovieModel(**movie) for movie in movies_data]

@app.get("/movies/{movie_id}")
def get_movie(movie_id: str):
    movie = next((movie for movie in movies if movie.id == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.get('/movies')  
def get_movies(q: Union[str, None] = None) -> Page[MovieModel]:
    if q:
        return paginate(list((movie for movie in movies if q.lower() in movie.title.lower())))
    return paginate(movies)

def recommend_movies(input_movie_ids):
    input_movie_ids_tensor = movie_id_vocabulary(tf.constant(input_movie_ids, dtype=tf.string))
    input_movie_embeddings = model.movie_embed(input_movie_ids_tensor)
    
    mean_embedding = tf.reduce_mean(input_movie_embeddings, axis=0, keepdims=True)
    all_movie_embeddings = model.movie_embed(tf.range(start=0, limit=movie_id_vocabulary.vocabulary_size(), dtype=tf.int32))

    similarity = tf.keras.losses.cosine_similarity(mean_embedding, all_movie_embeddings)
    top_indices = tf.argsort(similarity, direction='DESCENDING')[:10]

    vocab = movie_id_vocabulary.get_vocabulary()
    top_movie_ids = tf.gather(vocab, top_indices)
    return [mid.decode('utf-8') for mid in top_movie_ids.numpy()]

@app.get("/recommend")
async def get_recommendations(movie_ids: str):
    # Convert the comma-separated string of movie IDs to a list
    movie_ids_list = movie_ids.split(',')
    recommendations = recommend_movies(movie_ids_list)
    return {"recommended_movie_ids": recommendations}

add_pagination(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)