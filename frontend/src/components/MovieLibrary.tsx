import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import MovieTile from './MovieTile';
import { Pagination, TextField } from '@mui/material';
import React, { useEffect, useState } from 'react';
import axios, { AxiosResponse } from 'axios';

interface GetMoviesResponse {
    items: LibraryMovie[],
    page: number,
    pages: number,
    size: number,
    total: number
}

interface LibraryMovie {
    id: number;
    title: string;
    posterPath: string;
}

  async function fetchMovies(): Promise<GetMoviesResponse> {
    const response: AxiosResponse = await axios.get('http://localhost:8000/movies');
    const responseData: GetMoviesResponse = response.data;
    return responseData;
  }

const MovieLibrary = () => {
    useEffect(() => {
        fetchMovies().then((data) => setMovies(data));
    }, []);

    const [movies, setMovies] = useState<GetMoviesResponse>();
    const [page, setPage] = useState(1);
    const handleChange = (event: any, value: React.SetStateAction<number>) => {
        setPage(value);
    };

    return (
        <>
            <Box sx={{ flexGrow: 1, marginTop: 3 }} display="flex"  alignItems="center" minHeight="100vh" flexDirection={'column'}>
                <TextField sx={{ mb: 3 }} id="outlined-basic" label="Movie Search" variant="outlined" />
                <Grid container spacing={2} justifyContent={"center"}>
                    {
                        movies 
                        ?
                        movies.items.map(movie => {
                            return (
                                <Grid item>
                                    <MovieTile imageSrc={'https://image.tmdb.org/t/p/w500' + movie.posterPath} title={movie.title} />
                                </Grid>
                            )
                        })
                        :
                        <h2>Wait for the movies to load...</h2>
                    }
                </Grid>
                <Pagination count={movies?.pages ?? 1} color="primary" showFirstButton showLastButton sx={{ my: 5 }} page={movies?.page ?? 1} onChange={handleChange} />
            </Box>

        </>
    )
}

export default MovieLibrary;