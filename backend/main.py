from typing import Union
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi_pagination import Page, add_pagination, paginate
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MovieModel(BaseModel):
    id: int = Field()
    title: str = Field()
    posterPath: str = Field()


movies = [
    MovieModel(id=1, title='Toy Story', posterPath='/7G9915LfUQ2lVfwMEEhDsn3kT4B.jpg'),
    MovieModel(id=2, title='Harry Potter', posterPath='/8Xmkc1HvCOpMlbFvVabrtr6HAsp.jpg'),
]

@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    movie = next((movie for movie in movies if movie.id == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.get('/movies')  
def get_movies(q: Union[str, None] = None) -> Page[MovieModel]:
    if q:
        return paginate(list((movie for movie in movies if q.lower() in movie.title.lower())))
    return paginate(movies)

add_pagination(app)