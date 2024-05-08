import tensorflow as tf
import tensorflow_datasets as tfds
import numpy as np

# Load datasets.
ratings = tfds.load('movielens/100k-ratings', split="train")
movies = tfds.load('movielens/100k-movies', split="train")

# Prepare movie and user name dictionaries
movie_names = {}
movie_genres = {}
for movie in tfds.as_numpy(movies):
    movie_id = movie['movie_id'].decode('utf-8')
    movie_title = movie['movie_title'].decode('utf-8')
    genres = movie['movie_genres']
    movie_names[movie_id] = movie_title
    movie_genres[movie_id] = genres

# Prepare vocabulary for movies and users
movies = movies.map(lambda x: x["movie_id"])
users = ratings.map(lambda x: x["user_id"])
movie_id_vocabulary = tf.keras.layers.StringLookup()
user_id_vocabulary = tf.keras.layers.StringLookup()
movie_id_vocabulary.adapt(movies.batch(1000))
user_id_vocabulary.adapt(users.batch(1000))

# Define a more complex model
class MovieLensHybridModel(tf.keras.Model):
    def __init__(self, movie_vocab_size, user_vocab_size, genre_vocab_size):
        super().__init__()
        self.movie_embed = tf.keras.layers.Embedding(movie_vocab_size, 128, embeddings_regularizer='l2')
        self.user_embed = tf.keras.layers.Embedding(user_vocab_size, 128, embeddings_regularizer='l2')
        self.genre_embed = tf.keras.layers.Embedding(genre_vocab_size, 32, embeddings_regularizer='l2', mask_zero=True)
        self.dense_layers = tf.keras.Sequential([
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(128, activation='relu'),
        ])

    def call(self, features: dict) -> tf.Tensor:
        movie_embeddings = self.movie_embed(features['movie_id'])
        user_embeddings = self.user_embed(features['user_id'])
        genre_mask = self.genre_embed.compute_mask(features['movie_genres'])
        genre_embeddings = self.genre_embed(features['movie_genres'])
        genre_embeddings = tf.reduce_sum(genre_embeddings, axis=1) / tf.reduce_sum(tf.cast(genre_mask, tf.float32), axis=1, keepdims=True)
        combined = tf.concat([movie_embeddings, user_embeddings, genre_embeddings], axis=1)
        return self.dense_layers(combined)

# Initialize and compile the model.
unique_genres = np.unique(np.concatenate([g for g in movie_genres.values() if g.size > 0]))
genre_vocab = tf.keras.layers.IntegerLookup()
genre_vocab.adapt(unique_genres)

model = MovieLensHybridModel(movie_id_vocabulary.vocabulary_size(), user_id_vocabulary.vocabulary_size(), genre_vocab.vocabulary_size())
model.compile(optimizer=tf.keras.optimizers.Adam(0.01), loss='mean_squared_error')

# Determine the maximum number of genres per movie for padding
max_genre_length = max(len(g) for g in movie_genres.values())

# Prepare the dataset for training with more features.
def prepare_dataset():
    def process_rating(x):
        movie_genres_padded = tf.pad(x['movie_genres'], [[0, max_genre_length - tf.shape(x['movie_genres'])[0]]])
        return {
            'movie_id': movie_id_vocabulary(x['movie_id']),
            'user_id': user_id_vocabulary(x['user_id']),
            'movie_genres': genre_vocab(movie_genres_padded)
        }, x['user_rating']
    
    dataset = ratings.map(process_rating)
    return dataset.shuffle(10000).batch(32).cache().prefetch(tf.data.AUTOTUNE)

# Train the model with the historical data.
ds_train = prepare_dataset()
model.fit(ds_train, epochs=20)

# Recommendation function using cosine similarity adjusted for the hybrid model.
def recommend_movies(user_id, user_ratings):
    user_movie_ids = [mr[0] for mr in user_ratings]
    user_movie_ids_tensor = movie_id_vocabulary(tf.constant(user_movie_ids, dtype=tf.string))
    user_embeddings = model.user_embed(user_id_vocabulary(tf.constant([user_id], dtype=tf.string)))
    user_movie_embeddings = model.movie_embed(user_movie_ids_tensor)

    mean_embedding = tf.reduce_mean(user_movie_embeddings, axis=0, keepdims=True) + user_embeddings
    all_movie_embeddings = model.movie_embed(tf.range(start=0, limit=movie_id_vocabulary.vocabulary_size(), dtype=tf.int32))

    similarity = tf.keras.losses.cosine_similarity(mean_embedding, all_movie_embeddings)
    top_indices = tf.argsort(similarity, direction='DESCENDING')[:10]

    vocab = movie_id_vocabulary.get_vocabulary()
    top_movie_ids = tf.gather(vocab, top_indices)
    return [mid.decode('utf-8') for mid in top_movie_ids.numpy()]

# Example input
sample_user_id = "196"  # An example user ID
sample_ratings = [("82", 5.0)]

# Get recommendations based on provided ratings.
recommended_movie_ids = recommend_movies(sample_user_id, sample_ratings)
print("Recommended Movie IDs:", recommended_movie_ids)

def get_movie_names(movie_ids):
    return [movie_names[mid] for mid in movie_ids if mid in movie_names]

# Display the names of the chosen movies.
chosen_movie_names = get_movie_names([r[0] for r in sample_ratings])
print("Chosen Movie Names:", chosen_movie_names)

# Display the names of the recommended movies.
recommended_movie_names = get_movie_names(recommended_movie_ids)
print("Recommended Movie Names:", recommended_movie_names)
