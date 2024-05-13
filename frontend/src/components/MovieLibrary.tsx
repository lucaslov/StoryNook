import React, { useEffect, useState } from 'react';
import { Box, Grid, Button, Pagination, TextField } from '@mui/material';
import MovieTile from './MovieTile';
import { GetMoviesResponse } from '../interfaces/GetMoviesResponse';
import { LibraryMovie } from '../interfaces/LibraryMovie';
import { checkEndpointStatus, fetchMovies } from '../repositories/MoviesRepository';
import SelectedMovies from './SelectedMovies';
import RecommendationsPopup from './RecommendationsPopup';
import { ExtendedMovie } from '../interfaces/ExtendedMovie';

const DEFAULT_ITEM_LEN = 24;
const PLACEHOLDER_IMAGE = "https://via.placeholder.com/150?text=Poster+Not+Available";

const MovieLibrary = () => {
    const [movies, setMovies] = useState<GetMoviesResponse>();
    const [moviesToShow, setMoviesToShow] = useState<LibraryMovie[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [searchValue, setSearchValue] = useState("");
    const [numberOfPages, setNumberOfPages] = useState(1);
    const [selectedMovies, setSelectedMovies] = useState<ExtendedMovie[]>([]);
    const [showRecommendationsPopup, setShowRecommendationsPopup] = useState(false);
    const [recommendations, setRecommendations] = useState<ExtendedMovie[]>([]);

    useEffect(() => {
        fetchMovies(searchValue, DEFAULT_ITEM_LEN, currentPage).then((data) => {
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
    }, [currentPage]);

    const handlePageChange = (_event: any, value: React.SetStateAction<number>) => {
        setCurrentPage(value);
    };

    const handleMovieSearch = (_event: React.MouseEvent<HTMLButtonElement, MouseEvent>): void => {
        fetchMovies(searchValue).then((data) => {
            setMoviesToShow(data.items);
            setNumberOfPages(data.pages);
        });
    };

    const handleClear = (_event: React.MouseEvent<HTMLButtonElement, MouseEvent>): void => {
        setSearchValue("");
        setMoviesToShow(movies?.items || []);
        if (movies) {
            setNumberOfPages(movies.pages);
        }
    };

    const handleSearchValueChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
        setSearchValue(event.target.value);
        if (!event.target.value && movies) {
            setMoviesToShow(movies.items);
            setNumberOfPages(movies.pages);
        }
    };

    const addMovieToSelected = async (movie: LibraryMovie) => {
        if (!selectedMovies.find(m => m.id === movie.id)) {
            const isValid = await checkEndpointStatus(movie.posterPath);
            const extendedMovie: ExtendedMovie = {
                ...movie,
                currentImageSrc: isValid ? movie.posterPath : PLACEHOLDER_IMAGE
            };
            setSelectedMovies([...selectedMovies, extendedMovie]);
        }
    };

    const removeMovie = (id: Number) => {
        setSelectedMovies(selectedMovies.filter(movie => movie.id !== id));
    };


    const triggerRecommendations = async () => {
        const movieIds = selectedMovies.map(movie => movie.id);
        const requestBody = JSON.stringify({ movie_ids: movieIds });

        try {
            const response = await fetch('http://localhost:8000/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: requestBody
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Failed to fetch recommendations:', response.status, errorText);
                return;
            }

            const data = await response.json();
            if (!data.recommended_movie_ids) {
                console.error('Unexpected response format:', data);
                return;
            }

            // Assuming you have a way to map movie IDs to movie details
            // For the example below, we simulate this mapping
            const fetchedRecommendations = data.recommended_movie_ids.map((id: Number) => {
                // Simulate fetching movie details; replace with actual fetch if necessary
                const movie = moviesToShow.find(m => m.id === id);
                return movie ? {
                    ...movie,
                    currentImageSrc: movie.posterPath || PLACEHOLDER_IMAGE  // Ensure fallback to placeholder
                } : {
                    id,
                    title: `Movie ${id}`,
                    currentImageSrc: PLACEHOLDER_IMAGE
                };
            });

            setRecommendations(fetchedRecommendations);
            setShowRecommendationsPopup(true);
        } catch (error) {
            console.error('Error fetching recommendations:', error);
        }
    };


    const closeRecommendationsPopup = () => {
        setShowRecommendationsPopup(false);
    };

    const clearSelectedMovies = () => {
        setSelectedMovies([]); // Clear the array of selected movies
    };

    return (
        <>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 3, marginTop: 3 }}>
                <TextField
                    value={searchValue}
                    onChange={handleSearchValueChange}
                    sx={{ width: '40%', marginRight: 1 }}
                    id="outlined-basic"
                    label="Movie Search"
                    variant="outlined"
                />
                <Button onClick={handleClear} variant="contained" sx={{ height: '56px' }} color='secondary'>Clear</Button>
                <Button onClick={handleMovieSearch} variant="contained" sx={{ height: '56px', marginLeft: 1 }}>Search</Button>
            </Box>
            <Box sx={{ display: 'flex', flexDirection: 'row', width: '100%' }}>
                <Box sx={{ width: '70vw', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <Grid container spacing={2} justifyContent={"center"}>
                        {moviesToShow.length !== 0 ?
                            moviesToShow.map((movie: LibraryMovie) => (  // Explicit type here to satisfy TypeScript
                                <Grid item key={movie.id} onClick={() => addMovieToSelected(movie)}>
                                    <MovieTile imageSrc={movie.posterPath} title={movie.title} key={movie.id} />
                                </Grid>
                            )) :
                            <h2>{searchValue ? "No movies satisfy your query. Clear your search or adjust the query." : "Wait for the movies to load..."}</h2>
                        }
                    </Grid>
                    <Pagination count={numberOfPages} color="primary" showFirstButton showLastButton sx={{ my: 5 }} page={currentPage} onChange={handlePageChange} />
                </Box>
                <SelectedMovies
                    selectedMovies={selectedMovies}
                    removeMovie={removeMovie}
                    triggerRecommendations={triggerRecommendations}
                    clearSelectedMovies={clearSelectedMovies}
                />
            </Box>
            {showRecommendationsPopup && <RecommendationsPopup recommendations={recommendations} closePopup={closeRecommendationsPopup} />}
        </>
    );
};

export default MovieLibrary;
