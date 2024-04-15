import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import MovieTile from './MovieTile';
import { Button, Pagination, TextField } from '@mui/material';
import React, { useEffect, useState } from 'react';
import { GetMoviesResponse } from '../interfaces/GetMoviesResponse';
import { LibraryMovie } from '../interfaces/LibraryMovie';
import { fetchMovies } from '../repositories/MoviesRepository';
const DEFAULT_ITEM_LEN = 1;

const MovieLibrary = () => {
    const [movies, setMovies] = useState<GetMoviesResponse>();
    const [moviesToShow, setMoviesToShow] = useState<LibraryMovie[]>();
    const [currentPage, setCurrentPage] = useState(1);
    const [searchValue, setSearchValue] = useState("");
    const [numberOfPages, setNumberOfPages] = useState(1);
    
    useEffect(() => {
        fetchMovies().then((data) => {
            setMovies(data);
            setMoviesToShow(data.items);
            setNumberOfPages(data.pages);
        });
    }, []);
    
    useEffect(() => {
        fetchMovies(searchValue, DEFAULT_ITEM_LEN, currentPage).then((data) => {
            setMovies(data);
            setMoviesToShow(data.items);
            setNumberOfPages(data.pages);
        });
    }, [currentPage])

    const handlePageChange = (_event: any, value: React.SetStateAction<number>) => {
        setCurrentPage(value);
    };

    function handleMovieSearch(_event: React.MouseEvent<HTMLButtonElement, MouseEvent>): void {
        fetchMovies(searchValue).then((data) => {
            setMoviesToShow(data.items)
            setNumberOfPages(data.pages);
        });
    }

    function handleClear(_event: React.MouseEvent<HTMLButtonElement, MouseEvent>): void {
        setSearchValue("");
        setMoviesToShow(movies?.items)
        if(movies) {
            setNumberOfPages(movies.pages)
        }
    }

    function handleSearchValueChange(event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void {
        setSearchValue(event.target.value);
        if (!event.target.value && movies) {
            setMoviesToShow(movies.items)
            setNumberOfPages(movies.pages)
        }
    }

    return (
        <>
            <Box sx={{ flexGrow: 1, marginTop: 3 }} display="flex" alignItems="center" minHeight="100vh" flexDirection={'column'}>
                <TextField value={searchValue} onChange={handleSearchValueChange} sx={{ mb: 3 }} id="outlined-basic" label="Movie Search" variant="outlined" />
                <Button onClick={handleMovieSearch} variant="contained">Search</Button>
                <Button onClick={handleClear} variant="contained">Clear</Button>
                <Grid container spacing={2} justifyContent={"center"}>
                    {
                        moviesToShow?.length != 0
                            ?
                            moviesToShow?.map(movie => {
                                return (
                                    <Grid item key={movie.id}>
                                        <MovieTile imageSrc={'https://image.tmdb.org/t/p/w500' + movie.posterPath} title={movie.title} key={movie.id} />
                                    </Grid>
                                )
                            })
                            :
                            <h2>{searchValue ? "No movies satisfy your query. Clear your search or adjust the query." : "Wait for the movies to load..."}</h2>
                    }
                </Grid>
                <Pagination count={numberOfPages} color="primary" showFirstButton showLastButton sx={{ my: 5 }} page={currentPage} onChange={handlePageChange} />
            </Box>

        </>
    )
}

export default MovieLibrary;