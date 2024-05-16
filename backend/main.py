from typing import Union, List, Dict
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi_pagination import Page, add_pagination, paginate
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
import uvicorn
import os
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import math
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@tf.keras.utils.register_keras_serializable()
class RecommenderNet(tf.keras.Model):
    def __init__(self, num_users, num_movies, embedding_size, **kwargs):
        super(RecommenderNet, self).__init__(**kwargs)
        self.user_embedding = tf.keras.layers.Embedding(
            num_users, embedding_size,
            embeddings_initializer='he_normal',
            embeddings_regularizer=tf.keras.regularizers.l2(1e-6)
        )
        self.movie_embedding = tf.keras.layers.Embedding(
            num_movies, embedding_size,
            embeddings_initializer='he_normal',
            embeddings_regularizer=tf.keras.regularizers.l2(1e-6)
        )
        self.user_bias = tf.keras.layers.Embedding(num_users, 1)
        self.movie_bias = tf.keras.layers.Embedding(num_movies, 1)

    def call(self, inputs):
        user_vector = self.user_embedding(inputs[:, 0])
        movie_vector = self.movie_embedding(inputs[:, 1])
        user_bias = self.user_bias(inputs[:, 0])
        movie_bias = self.movie_bias(inputs[:, 1])
        dot_user_movie = tf.tensordot(user_vector, movie_vector, 2)
        x = dot_user_movie + user_bias + movie_bias
        return tf.nn.sigmoid(x)
    
current_script_dir = os.path.dirname(os.path.abspath(__file__))

# Load the trained model
model = tf.keras.models.load_model(os.path.join(current_script_dir, '../recommender/recommender_model.keras'))

app = FastAPI(
    title="Movie Recommendation API",
    description="An API to recommend movies based on user ratings using collaborative and content-based filtering.",
    version="1.0.0"
)

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

class RecommendationRequest(BaseModel):
    movie_ratings: List[Dict[str, float]] = Field(
        default=[],
        description="List of movie IDs with corresponding user ratings."
    )

class MovieModel(BaseModel):
    id: str
    title: str
    posterPath: str

# Load movies to memory
movies = []
movies_df = pd.read_csv('data/ml-20m/movies.csv')
for _, row in movies_df.iterrows():
    movie_instance = MovieModel(id=str(row['movieId']), title=row['title'], posterPath="")
    movies.append(movie_instance)
ratings_df = pd.read_csv('data/ml-20m/ratings.csv')
tags_df = pd.read_csv('data/ml-20m/tags.csv')
links_df = pd.read_csv('data/ml-20m/links.csv')
movie_to_tmdb_map = {
    str(int(row['movieId'])): (str(int(row['tmdbId'])) if not (isinstance(row['tmdbId'], float) and math.isnan(row['tmdbId'])) else 'NaN')
    for _, row in links_df.iterrows()
}
# Merge ratings and movies dataframes
data = pd.merge(ratings_df, movies_df, on='movieId')

# Map userId and movieId to a continuous range of indices
user_id_mapping = {id: i for i, id in enumerate(data['userId'].unique())}
movie_id_mapping = {id: i for i, id in enumerate(data['movieId'].unique())}
data['userId'] = data['userId'].map(user_id_mapping)
data['movieId'] = data['movieId'].map(movie_id_mapping)

num_users = len(user_id_mapping)
num_movies = len(movie_id_mapping)

# Extract and process movie genres
movies_df['genres'] = movies_df['genres'].str.split('|')
all_genres = set(genre for sublist in movies_df['genres'] for genre in sublist)
mlb = MultiLabelBinarizer()
genre_features = mlb.fit_transform(movies_df['genres'])

# Group tags by movieId and aggregate them into a single string, ensuring all tags are strings
tags_df['tag'] = tags_df['tag'].astype(str)
tags_grouped = tags_df.groupby('movieId')['tag'].apply(lambda x: ' '.join(x)).reset_index()

# Merge tags with movies
movies_with_tags = pd.merge(movies_df, tags_grouped, on='movieId', how='left')
movies_with_tags['tag'] = movies_with_tags['tag'].fillna('')

# Combine genres and tags into a single feature
movies_with_tags['features'] = movies_with_tags['genres'].apply(lambda x: ' '.join(x)) + ' ' + movies_with_tags['tag']

# Use TF-IDF to transform features into vectors
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies_with_tags['features'])

# Create a mapping from movieId to index for genre features
movie_index_mapping = {id: i for i, id in enumerate(movies_with_tags['movieId'])}

base_poster_url = "https://image.tmdb.org/t/p/original/"

def get_poster_path(movie_id):
    tmdb_id = movie_to_tmdb_map.get(movie_id)
    if tmdb_id == 'NaN' or tmdb_id is None:
        return ""
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/images"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv('TMDB_API_KEY')}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        posters = data.get('posters', [])
        if posters:
            return base_poster_url + posters[0]['file_path']
    return ""

@app.get("/movies/{movie_id}", response_model=MovieModel, summary="Get a movie by its ID", description="Fetch a single movie by its ID and return its details including the poster path.")
def get_movie(movie_id: str):
    # Fetch a single movie by ID or raise a 404 if not found
    movie = next((movie for movie in movies if movie.id == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    movie.posterPath = get_poster_path(movie_id)
    return movie

@app.get('/movies', response_model=Page[MovieModel], summary="Get all movies", description="Fetch all movies or search for a movie by its title.")
def get_movies(q: Union[str, None] = None) -> Page[MovieModel]:
    # Optionally filter movies by query string or return all
    if q:
        filtered_movies = [movie for movie in movies if q.lower() in movie.title.lower()]
        return paginate(filtered_movies)
    return paginate(movies)

# Content-Based Filtering using TF-IDF
def get_content_based_recommendations(user_ratings, num_recommendations=10):
    rated_movie_indices = [movie_index_mapping[movie_id] for movie_id in user_ratings]
    rated_movie_tfidf = tfidf_matrix[rated_movie_indices]
    user_profile = rated_movie_tfidf.mean(axis=0)
    user_profile_array = np.asarray(user_profile)
    cosine_similarities = cosine_similarity(user_profile_array, tfidf_matrix).flatten()
    similar_indices = cosine_similarities.argsort()[-num_recommendations:][::-1]
    similar_movie_ids = [movies_with_tags['movieId'].iloc[i] for i in similar_indices]
    return similar_movie_ids

# Combine Collaborative and Content-Based Filtering
def recommend_movies(user_ratings, num_recommendations=10):
    valid_user_ratings = {movie_id: rating for movie_id, rating in user_ratings.items() if movie_id in movie_id_mapping}
    
    if not valid_user_ratings:
        print("No valid movie IDs provided.")
        return []

    user_id = 0  # Dummy user ID since we are not using user ID in interaction
    user_input = np.array([[user_id, movie_id_mapping[movie_id]] for movie_id in valid_user_ratings])
    
    # Collaborative filtering predictions
    predictions = model.predict(user_input)
    predictions = np.squeeze(predictions)
    movie_ids = user_input[:, 1]
    movie_ratings = {movie_id: rating for movie_id, rating in zip(movie_ids, predictions)}
    top_collab_movie_ids = sorted(movie_ratings, key=movie_ratings.get, reverse=True)[:num_recommendations]
    
    # Content-based filtering recommendations
    top_content_movie_ids = get_content_based_recommendations(valid_user_ratings, num_recommendations)
    
    # Combine recommendations and remove overlap with input movies
    combined_recommendations = list(set(top_collab_movie_ids + top_content_movie_ids) - set(valid_user_ratings.keys()))
    combined_recommendations = combined_recommendations[:num_recommendations]
    
    return combined_recommendations

@app.post("/recommend", summary="Get movie recommendations", description="Get movie recommendations based on user ratings using a combination of collaborative and content-based filtering.")
async def get_recommendations(request: RecommendationRequest):
    # Use the parsed movie_ratings list from the request body
    movie_ratings_dict = {item['movie_id']: item['user_rating'] for item in request.movie_ratings}
    if not movie_ratings_dict:
        raise HTTPException(status_code=400, detail="No movie ratings provided for recommendations.")
    
    recommendations = recommend_movies(movie_ratings_dict)
    
    # Map ids to posterPath and title
    movie_map = {movie.id: movie for movie in movies}
    recommended_movies = []
    for movie_id in recommendations:
        movie = movie_map.get(str(movie_id))
        if movie:
            recommended_movies.append({
                "title": movie.title,
                "posterPath": get_poster_path(str(movie_id))
            })
    
    return {"recommended_movies": recommended_movies}

add_pagination(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)