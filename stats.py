import pandas as pd
import matplotlib.pyplot as plt
import os

current_script_dir = os.path.dirname(os.path.abspath(__file__))

ratings = pd.read_csv(current_script_dir + '/data/ml-20m/ratings.csv')
movies = pd.read_csv(current_script_dir + '/data/ml-20m/movies.csv')

# Total number of users
num_users = ratings['userId'].nunique()

# Total number of movies
num_movies = ratings['movieId'].nunique()

# Total number of ratings
total_ratings = len(ratings)

print(f"Total number of users: {num_users}")
print(f"Total number of movies: {num_movies}")
print(f"Total number of ratings: {total_ratings}")

# Splitting the 'genres' column where '|' is found and then stacking them into a single column
unique_genres = movies['genres'].str.split('|').explode().unique()

# Counting the unique genres
num_unique_genres = len(unique_genres)

print("Unique Genres:", unique_genres)
print("Number of Unique Genres:", num_unique_genres)

# Histogram of all ratings
ratings['rating'].hist(bins=10, edgecolor='black')
plt.title('Distribution of Ratings')
plt.xlabel('Rating')
plt.ylabel('Frequency')
plt.show()

# Splitting the 'genres' column where '|' is found and exploding it
movies['genres'] = movies['genres'].str.split('|')
movies_exploded = movies.explode('genres')

# Counting occurrences of each genre
genre_counts = movies_exploded['genres'].value_counts()

# Plotting genres distribution
genre_counts.plot(kind='bar', color='skyblue')
plt.title('Movie Counts by Genre')
plt.xlabel('Genre')
plt.ylabel('Number of Movies')
plt.xticks(rotation=45, ha="right")  # Improve label readability
plt.tight_layout()  # Adjust layout to make room for label rotation
plt.show()