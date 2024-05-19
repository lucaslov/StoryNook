import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import AutoModel, pipeline, AutoModelForCausalLM, AutoTokenizer, GenerationConfig
import torch
import os
from fastapi.middleware.cors import CORSMiddleware
import torch
from langchain import HuggingFacePipeline
 
MODEL_NAME = "TheBloke/Llama-2-13b-Chat-GPTQ"
 
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
 
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME, torch_dtype=torch.float16, trust_remote_code=True, device_map="mps"
)
 
generation_config = GenerationConfig.from_pretrained(MODEL_NAME)
generation_config.max_new_tokens = 1024
generation_config.temperature = 0.0001
generation_config.top_p = 0.95
generation_config.do_sample = True
generation_config.repetition_penalty = 1.15
 
text_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    generation_config=generation_config,
)
 
llm = HuggingFacePipeline(pipeline=text_pipeline, model_kwargs={"temperature": 0})

result = llm(
    "Explain the difference between ChatGPT and open source LLMs in a couple of lines."
)
print(result)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to the specific frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load movie data
current_script_dir = os.path.dirname(os.path.abspath(__file__))
movie_data = pd.read_csv(os.path.join(current_script_dir, '../data/scrapped/combined_for_embeddings.csv'), sep=';')




# Initialize ChromaDB and load data
chroma_client = chromadb.Client(Settings(chroma_dir="path/to/chromadb", persist_directory="path/to/persist"))
collection = chroma_client.create_collection(name="movie_recommendations")

# Function to embed text using a local model
model_name = 'sentence-transformers/all-MiniLM-L6-v2'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def embed_text(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state[:, 0, :]
    return embeddings.numpy()[0]

# Add movie data to ChromaDB collection
for idx, row in movie_data.iterrows():
    embedding = embed_text(row['description'])
    collection.add(
        embeddings=[embedding],
        documents=[{
            'movieId': row['movieId'],
            'title': row['title'],
            'genres': row['genres'],
            'median_rating': row['median_rating'],
            'tags': row['tags'],
            'description': row['description']
        }],
        ids=[str(row['movieId'])]
    )

# Define request and response models
class UserInput(BaseModel):
    message: str
    conversation_id: str

class MovieRecommendation(BaseModel):
    movieId: int
    title: str
    genres: str
    median_rating: float
    description: str

# Load a local Llama model for generating responses
llama_model_name = "huggingface/llama"
llama_tokenizer = AutoTokenizer.from_pretrained(llama_model_name)
llama_model = AutoModel.from_pretrained(llama_model_name)
llama_pipeline = pipeline("text-generation", model=llama_model, tokenizer=llama_tokenizer)

# In-memory conversation storage
conversations = {}

# Define the API endpoints
@app.post("/recommend", response_model=list[MovieRecommendation])
async def recommend_movies(user_input: UserInput):
    user_message = user_input.message
    conversation_id = user_input.conversation_id

    # Retrieve or initialize conversation context
    if conversation_id not in conversations:
        conversations[conversation_id] = []

    # Step 4: Extract keywords
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform([user_message])
    keywords = vectorizer.get_feature_names_out()

    # Step 5: Search for matching movies in ChromaDB
    results = collection.query(query_texts=[user_message], n_results=20)

    if not results["documents"]:
        raise HTTPException(status_code=404, detail="No matching movies found")

    # Step 6: Filter and recommend movies using the local Llama model
    prompt = (
        "You are a movie recommendation assistant. Based on the following user input, "
        "provide a list of movies that match their preferences:\n\n"
        f"User Input: {user_message}\n\n"
        "Matching Movies:\n"
    )
    for movie in results["documents"]:
        prompt += (
            f"Title: {movie['title']}\n"
            f"Genres: {movie['genres']}\n"
            f"Median Rating: {movie['median_rating']}\n"
            f"Description: {movie['description']}\n\n"
        )
    prompt += (
        "Based on the above information, provide a curated list of movie recommendations that best match the user's preferences."
    )

    llama_response = llama_pipeline(prompt, max_length=300, num_return_sequences=1, temperature=0.7)
    recommendations_text = llama_response[0]['generated_text'].strip().split('\n\n')

    recommended_movies = []
    for rec in recommendations_text:
        lines = rec.split('\n')
        movie_info = {}
        for line in lines:
            if line.startswith("Title:"):
                movie_info['title'] = line.replace("Title: ", "").strip()
            elif line.startswith("Genres:"):
                movie_info['genres'] = line.replace("Genres: ", "").strip()
            elif line.startswith("Median Rating:"):
                movie_info['median_rating'] = float(line.replace("Median Rating: ", "").strip())
            elif line.startswith("Description:"):
                movie_info['description'] = line.replace("Description: ", "").strip()

        # Find the movie ID from the original data
        for idx, row in movie_data.iterrows():
            if row['title'] == movie_info.get('title'):
                movie_info['movieId'] = int(row['movieId'])
                break

        if movie_info:
            recommended_movies.append(MovieRecommendation(**movie_info))

    # Update conversation context
    conversations[conversation_id].append(user_message)

    return recommended_movies

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
