import React, { useEffect, useState } from 'react';
import { Box, Grid, Button, Pagination, TextField } from '@mui/material';
import MovieTile from './MovieTile';
import { GetMoviesResponse } from '../interfaces/GetMoviesResponse';
import { LibraryMovie } from '../interfaces/LibraryMovie';
import { fetchMovies } from '../repositories/MoviesRepository';
import SelectedMovies from './SelectedMovies';
import RecommendationsPopup from './RecommendationsPopup';

const DEFAULT_ITEM_LEN = 24;

const MovieLibrary = () => {
    const [movies, setMovies] = useState<GetMoviesResponse>();
    const [moviesToShow, setMoviesToShow] = useState<LibraryMovie[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [searchValue, setSearchValue] = useState("");
    const [numberOfPages, setNumberOfPages] = useState(1);
    const [selectedMovies, setSelectedMovies] = useState<LibraryMovie[]>([]);
    const [showRecommendationsPopup, setShowRecommendationsPopup] = useState(false);
    const [recommendations, setRecommendations] = useState<LibraryMovie[]>([]);

    useEffect(() => {
        fetchMovies("", DEFAULT_ITEM_LEN, currentPage).then((data) => {
            setMovies(data);
            setMoviesToShow(data.items);
            setNumberOfPages(data.pages);
        });
    }, [currentPage]);

    useEffect(() => {
        const handler = setTimeout(() => {
            if (searchValue.length >= 3) {
                setCurrentPage(1);
                fetchMovies(searchValue, DEFAULT_ITEM_LEN, 1).then((data) => {
                    setMovies(data);
                    setMoviesToShow(data.items);
                    setNumberOfPages(data.pages);
                });
            }
        }, 500); // 500ms delay

        return () => {
            clearTimeout(handler);
        };
    }, [searchValue]);

    useEffect(() => {
        if (searchValue.length >= 3) {
            fetchMovies(searchValue, DEFAULT_ITEM_LEN, currentPage).then((data) => {
                setMovies(data);
                setMoviesToShow(data.items);
                setNumberOfPages(data.pages);
            });
        } else {
            fetchMovies("", DEFAULT_ITEM_LEN, currentPage).then((data) => {
                setMovies(data);
                setMoviesToShow(data.items);
                setNumberOfPages(data.pages);
            });
        }
    }, [currentPage, searchValue]);

    const handlePageChange = (_event: any, value: React.SetStateAction<number>) => {
        setCurrentPage(value);
    };

    const handleClear = (_event: React.MouseEvent<HTMLButtonElement, MouseEvent>): void => {
        setSearchValue("");
        setCurrentPage(1); // Reset to first page on clear
        fetchMovies("", DEFAULT_ITEM_LEN, 1).then((data) => {
            setMovies(data);
            setMoviesToShow(data.items);
            setNumberOfPages(data.pages);
        });
    };

    const handleSearchValueChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
        setSearchValue(event.target.value);
    };

    const addMovieToSelected = async (movie: LibraryMovie, rating: number) => {
        if (!selectedMovies.find(m => m.id === movie.id)) {
            movie.rating = rating;
            setSelectedMovies([...selectedMovies, movie]);
        }
    };

    const removeMovie = (id: number) => {
        setSelectedMovies(selectedMovies.filter(movie => movie.id !== id));
    };

    const updateMovieRating = (id: number, rating: number) => {
        setSelectedMovies(selectedMovies.map(movie => movie.id === id ? { ...movie, rating } : movie));
    };

    const triggerRecommendations = async () => {
        const moviesForRecommendation = selectedMovies.map(movie => { return { "movie_id": movie.id, "user_rating": movie.rating * 2 } });
        const requestBody = JSON.stringify({ "movie_ratings": moviesForRecommendation });
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
            if (!data.recommended_movies) {
                console.error('Unexpected response format:', data);
                return;
            }

            const fetchedRecommendations = await Promise.all(data.recommended_movies.map(async (mov: { title: string, posterPath: string }) => {
                return {
                    title: mov.title,
                    currentImageSrc: mov.posterPath,
                    rating: 0 // Initialize the rating for recommended movies
                };
            }));

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
        setSelectedMovies([]);
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
            </Box>
            <Box sx={{ display: 'flex', flexDirection: 'row', width: '100%' }}>
                <Box sx={{ width: '70vw', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <Grid container spacing={2} justifyContent={"center"}>
                        {moviesToShow.length !== 0 ?
                            moviesToShow.map((movie: LibraryMovie) => (
                                <Grid item key={movie.id}>
                                    <MovieTile movieId={movie.id} onClick={(rating: number) => addMovieToSelected(movie, rating)} />
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
                    updateMovieRating={updateMovieRating}
                    triggerRecommendations={triggerRecommendations}
                    clearSelectedMovies={clearSelectedMovies}
                />
            </Box>
            {showRecommendationsPopup && <RecommendationsPopup recommendations={recommendations} closePopup={closeRecommendationsPopup} />}
        </>
    );
};

export default MovieLibrary;