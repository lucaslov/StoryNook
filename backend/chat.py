from fastapi import HTTPException, APIRouter
import chromadb
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.llms.llama_cpp.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)
import re
from chromadb.utils import embedding_functions
import os
from langchain.document_loaders import CSVLoader
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma

llm_router = APIRouter()

# Load movie data
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# movie_data = pd.read_csv(os.path.join(current_script_dir, '../data/scrapped/combined_for_embeddings.csv'), sep=';')
file_path=os.path.join(current_script_dir, '../data/scrapped/combined_for_embeddings.csv')
loader = CSVLoader(file_path=file_path,
                   source_column="movieId",
                   csv_args={"delimiter": ";", "quotechar": '"',}
                   )
documents = loader.load()
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

db = Chroma.from_documents(documents, embedding_function)

# Initialize the LLM model
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
llm = LlamaCPP(
    model_path='/Users/lukasz/Desktop/StoryNook/data/llamaModels/smaller.gguf',
    temperature=0.1,
    max_new_tokens=256,
    context_window=3900,
    generate_kwargs={},
    model_kwargs={"n_gpu_layers": -1},
    messages_to_prompt=messages_to_prompt,
    completion_to_prompt=completion_to_prompt,
    verbose=True,
)

# Initialize ChromaDB client and collection
chroma_client = chromadb.PersistentClient(path="/Users/lukasz/Desktop/StoryNook/data/chroma")
collection = chroma_client.get_collection(name="movie_recommendations")
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

class LlmRecommendResponse:
  def __init__(self, llmResponse, context):
    self.llmResponse = llmResponse
    self.context = context

# Define the API endpoint
@llm_router.post("/llm-recommend")
async def recommend_movies(user_input: str):
    # Preliminary check: Is the user request about movies?
    domain_check_prompt = f"Is the following user input about movies? Answer yes or no. Input: {user_input}"
    domain_check_response = llm.complete(domain_check_prompt)
    is_movie_related = "yes" in domain_check_response.text.lower()

    if not is_movie_related:
        raise HTTPException(status_code=400, detail="This service is for movie recommendations only. Please provide a movie-related request.")

    # Generate a list of tags from the user input
    tags_prompt = f"Extract tags from the following user input for a movie recommendation. Return only the tags and nothing else, return them as comma separated values in a following format: ['tag', 'another tag']. Input: {user_input}"
    tags_response = llm.complete(tags_prompt).text

    tags_pattern = re.compile(r"\['(.*?)'\]")
    tags_match = tags_pattern.search(tags_response)

    if tags_match:
        tags = tags_match.group(0)
        search_query = " ".join(tags) + user_input
    else:
        search_query = user_input
    
    # Perform similarity search in ChromaDB
    docs = db.similarity_search(search_query)
    
    title_pattern = re.compile(r"title: (.+)")
    description_pattern = re.compile(r"description: (.+)")

    # List to hold the extracted objects
    extracted_movies = []

    for doc in docs:
        title_match = title_pattern.search(doc.page_content)
        description_match = description_pattern.search(doc.page_content)
        
        title = title_match.group(1) if title_match else None
        description = description_match.group(1) if description_match else None
        
        if title and description:
            extracted_movies.append({"title": title, "description": description})
        
    resp_prompt = f"Based on the provided context, evaluate and answer the user's query. Query: {user_input}. Context: {extracted_movies}"

    resp = llm.complete(resp_prompt).text

    return LlmRecommendResponse(llmResponse=resp, context=docs)