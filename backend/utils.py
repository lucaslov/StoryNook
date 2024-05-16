import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

base_poster_url = "https://image.tmdb.org/t/p/original/"

def get_poster_path(movie_id, movie_to_tmdb_map):
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