from typing import Union
from pydantic import BaseModel, Field
from fastapi import FastAPI
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

@app.get("/movies/{movieId}")
def get_movie(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get('/movies')  
async def get_movies() -> Page[MovieModel]:  # use Page[UserOut] as return type annotation
    return paginate(movies)  # use paginate function to paginate your data

add_pagination(app)