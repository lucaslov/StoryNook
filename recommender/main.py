import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Load the datasets
movies = pd.read_csv('movies.csv')
ratings = pd.read_csv('ratings.csv')
tags = pd.read_csv('tags.csv')

# Merge ratings and movies dataframes
data = pd.merge(ratings, movies, on='movieId')

# Map userId and movieId to a continuous range of indices
user_id_mapping = {id: i for i, id in enumerate(data['userId'].unique())}
movie_id_mapping = {id: i for i, id in enumerate(data['movieId'].unique())}
data['userId'] = data['userId'].map(user_id_mapping)
data['movieId'] = data['movieId'].map(movie_id_mapping)

num_users = len(user_id_mapping)
num_movies = len(movie_id_mapping)

# Extract and process movie genres
movies['genres'] = movies['genres'].str.split('|')
all_genres = set(genre for sublist in movies['genres'] for genre in sublist)
mlb = MultiLabelBinarizer()
genre_features = mlb.fit_transform(movies['genres'])

# Group tags by movieId and aggregate them into a single string, ensuring all tags are strings
tags['tag'] = tags['tag'].astype(str)
tags_grouped = tags.groupby('movieId')['tag'].apply(lambda x: ' '.join(x)).reset_index()

# Merge tags with movies
movies_with_tags = pd.merge(movies, tags_grouped, on='movieId', how='left')
movies_with_tags['tag'] = movies_with_tags['tag'].fillna('')

# Combine genres and tags into a single feature
movies_with_tags['features'] = movies_with_tags['genres'].apply(lambda x: ' '.join(x)) + ' ' + movies_with_tags['tag']

# Use TF-IDF to transform features into vectors
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies_with_tags['features'])

# Create a mapping from movieId to index for genre features
movie_index_mapping = {id: i for i, id in enumerate(movies_with_tags['movieId'])}

# Register the custom model class
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

# Instantiate the model
embedding_size = 50
model = RecommenderNet(num_users, num_movies, embedding_size)
model.compile(loss=tf.keras.losses.BinaryCrossentropy(), optimizer=tf.keras.optimizers.legacy.Adam(learning_rate=0.001))

# Prepare training data
user_ids = data['userId'].values
movie_ids = data['movieId'].values
ratings = data['rating'].apply(lambda x: 1 if x >= 4 else 0).values

# Use TensorFlow's tf.data API to load and preprocess data in parallel
dataset = tf.data.Dataset.from_tensor_slices((np.vstack((user_ids, movie_ids)).T, ratings))
dataset = dataset.shuffle(buffer_size=1024).batch(64).prefetch(tf.data.experimental.AUTOTUNE)

# Train the model on the entire dataset
history = model.fit(
    dataset,
    epochs=10,
    verbose=1
)

# Save the model to a file using the new .keras format
model.save('recommender_model.keras')

# Load the model
loaded_model = tf.keras.models.load_model('recommender_model.keras')

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
    predictions = loaded_model.predict(user_input)
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

user_ratings = {
    1: 10,
    260: 9,
    296: 9,
    220: 1
}

recommended_movies = recommend_movies(user_ratings)
print("Recommended Movies:", recommended_movies)