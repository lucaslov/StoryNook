import os
import pandas as pd
import math
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from dotenv import load_dotenv
import tensorflow as tf
from models import MovieModel

# Load environment variables from .env file
load_dotenv()

current_script_dir = os.path.dirname(os.path.abspath(__file__))

# Load the trained model
model = tf.keras.models.load_model(os.path.join(current_script_dir, '../recommender/recommender_model.keras'))

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
