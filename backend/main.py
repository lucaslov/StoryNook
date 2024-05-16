from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
import uvicorn
from routes import router as api_router

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

# Include the API routes
app.include_router(api_router)

# Add pagination
add_pagination(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
