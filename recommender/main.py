import tensorflow as tf
import tensorflow_datasets as tfds
import numpy as np

# Load datasets.
ratings = tfds.load('movielens/100k-ratings', split="train")
movies = tfds.load('movielens/100k-movies', split="train")

movie_names = {}
for movie in tfds.as_numpy(movies):
    movie_id = movie['movie_id'].decode('utf-8')
    movie_title = movie['movie_title'].decode('utf-8')
    movie_names[movie_id] = movie_title

# Processing movies data to create a vocabulary of movie IDs.
movies = movies.map(lambda x: x["movie_id"])
movie_id_vocabulary = tf.keras.layers.StringLookup()
movie_id_vocabulary.adapt(movies.batch(1000))

# Define model that uses movie embeddings with user embeddings.
class MovieLensRankingModel(tf.keras.Model):
    def __init__(self, movie_vocab_size):
        super().__init__()
        self.movie_embed = tf.keras.layers.Embedding(movie_vocab_size, 128, embeddings_regularizer='l2')
        self.dense_layers = tf.keras.Sequential([
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(128, activation='relu'),
        ])

    def call(self, features: tf.Tensor) -> tf.Tensor:
        movie_embeddings = self.movie_embed(features)
        return self.dense_layers(movie_embeddings)

# Initialize and compile the model.
model = MovieLensRankingModel(movie_id_vocabulary.vocabulary_size())
model.compile(optimizer=tf.keras.optimizers.Adam(0.001), loss='mean_squared_error')

# Prepare dataset for training with negative sampling.
def prepare_dataset():
    movie_ids = ratings.map(lambda x: movie_id_vocabulary(x["movie_id"]))
    user_ratings = ratings.map(lambda x: x["user_rating"])
    dataset = tf.data.Dataset.zip((movie_ids, user_ratings))
    dataset = dataset.shuffle(10000).batch(32).cache().prefetch(tf.data.AUTOTUNE)
    return dataset

# Train the model with historical data.
ds_train = prepare_dataset()
model.fit(ds_train, epochs=20)

# Recommendation function using cosine similarity.
def recommend_movies(user_ratings):
    user_movie_ids = [mr[0] for mr in user_ratings]
    user_movie_ids_tensor = movie_id_vocabulary(tf.constant(user_movie_ids, dtype=tf.string))
    user_movie_embeddings = model(user_movie_ids_tensor)

    mean_embedding = tf.reduce_mean(user_movie_embeddings, axis=0, keepdims=True)
    all_movie_embeddings = model(tf.range(start=0, limit=movie_id_vocabulary.vocabulary_size(), dtype=tf.int32))

    similarity = tf.keras.losses.cosine_similarity(mean_embedding, all_movie_embeddings)
    top_indices = tf.argsort(similarity, direction='DESCENDING')[:10]

    # Convert indices to movie IDs
    vocab = movie_id_vocabulary.get_vocabulary()
    top_movie_ids = tf.gather(vocab, top_indices)
    return [mid.decode('utf-8') for mid in top_movie_ids.numpy()]

# Example input: list of (movie_id, rating)
sample_ratings = [("82", 5.0)]

# Get recommendations based on provided ratings.
recommended_movie_ids = recommend_movies(sample_ratings)
print("Recommended Movie IDs:", recommended_movie_ids)

# Function to get movie names from movie IDs.
def get_movie_names(movie_ids):
    return [movie_names[mid] for mid in movie_ids]

# Display the names of the chosen movies.
chosen_movie_ids = [r[0] for r in sample_ratings]
chosen_movie_names = get_movie_names(chosen_movie_ids)
print("Chosen Movie Names:", chosen_movie_names)

# Display the names of the recommended movies.
recommended_movie_names = get_movie_names(recommended_movie_ids)
print("Recommended Movie Names:", recommended_movie_names)
