from typing import Union
from fastapi import APIRouter, HTTPException
from fastapi_pagination import Page, paginate
from models import RecommendationRequest, MovieModel
from database import movies, movie_to_tmdb_map, model, tfidf_matrix, movie_index_mapping, movies_with_tags, movie_id_mapping
from utils import get_poster_path
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

router = APIRouter()

@router.get("/movies/{movie_id}", response_model=MovieModel, summary="Get a movie by its ID", description="Fetch a single movie by its ID and return its details including the poster path.")
def get_movie(movie_id: str):
    # Fetch a single movie by ID or raise a 404 if not found
    movie = next((movie for movie in movies if movie.id == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    movie.posterPath = get_poster_path(movie_id, movie_to_tmdb_map)
    return movie

@router.get('/movies', response_model=Page[MovieModel], summary="Get all movies", description="Fetch all movies or search for a movie by its title.")
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

@router.post("/recommend", summary="Get movie recommendations", description="Get movie recommendations based on user ratings using a combination of collaborative and content-based filtering.")
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
                "posterPath": get_poster_path(str(movie_id), movie_to_tmdb_map)
            })
    
    return {"recommended_movies": recommended_movies}
