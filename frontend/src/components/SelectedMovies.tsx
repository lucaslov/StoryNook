import { Box, Typography, Card, CardContent, CardMedia, IconButton, Button, Rating } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import StarIcon from '@mui/icons-material/Star';
import { useState } from 'react';
import { LibraryMovie } from '../interfaces/LibraryMovie';

interface SelectedMoviesProps {
    selectedMovies: LibraryMovie[];
    removeMovie: (id: number) => void;
    updateMovieRating: (id: number, rating: number) => void;
    triggerRecommendations: () => void;
    clearSelectedMovies: () => void;
}

const SelectedMovies = ({ selectedMovies, removeMovie, updateMovieRating, triggerRecommendations, clearSelectedMovies }: SelectedMoviesProps) => {
    const [hover, setHover] = useState<{ [key: number]: number }>({});

    const labels: { [index: string]: string } = {
        0.5: 'Useless',
        1: 'Useless+',
        1.5: 'Poor',
        2: 'Poor+',
        2.5: 'Ok',
        3: 'Ok+',
        3.5: 'Good',
        4: 'Good+',
        4.5: 'Excellent',
        5: 'Excellent+',
    };

    function getLabelText(value: number) {
        return `${value} Star${value !== 1 ? 's' : ''}, ${labels[value]}`;
    }

    return (
        <Box sx={{
            width: '30vw',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            borderLeft: '1px solid #e0e0e0',
            height: '100vh',
            position: 'sticky',
            top: 0,
            overflowY: 'auto'
        }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', padding: 2 }}>
                <Typography variant="h6">Selected Movies</Typography>
                <Box>
                    <Button color='secondary' variant="contained" onClick={clearSelectedMovies} sx={{ marginRight: 1 }}>Clear</Button>
                    <Button variant="contained" onClick={triggerRecommendations}>Recommend</Button>
                </Box>
            </Box>
            {selectedMovies.map((movie: LibraryMovie, index: number) => (
                <Card key={index} sx={{
                    width: '90%',
                    display: 'flex',
                    flexDirection: 'column',
                    marginBottom: 2,
                    minHeight: 80,
                    overflow: 'hidden',
                    position: 'relative',
                    padding: 1
                }}>
                    <IconButton
                        sx={{
                            position: 'absolute',
                            top: 0,
                            right: 0,
                            color: 'red',
                            zIndex: 1
                        }}
                        onClick={() => removeMovie(movie.id)}
                    >
                        <CloseIcon />
                    </IconButton>
                    <Box sx={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }}>
                        <CardMedia
                            component="img"
                            sx={{
                                width: '8vh',
                                height: '8vh',
                                objectFit: 'cover',
                                marginRight: '8px'
                            }}
                            image={movie.posterPath}
                            alt={movie.title}
                        />
                        <CardContent sx={{
                            flex: '1',
                            display: 'flex',
                            flexDirection: 'column',
                            justifyContent: 'center',
                            padding: '8px'
                        }}>
                            <Typography variant="subtitle1" noWrap sx={{ fontSize: '1.1rem' }}>
                                {movie.title}
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                                <Rating
                                    name={`hover-feedback-${movie.id}`}
                                    value={movie.rating}
                                    precision={0.5}
                                    getLabelText={getLabelText}
                                    onChange={(_, newValue) => {
                                        updateMovieRating(movie.id, newValue ?? 0);
                                    }}
                                    onChangeActive={(_, newHover) => {
                                        setHover((prevHover) => ({ ...prevHover, [movie.id]: newHover }));
                                    }}
                                    emptyIcon={<StarIcon style={{ opacity: 0.55 }} fontSize="inherit" />}
                                />
                                <Box sx={{ ml: 2 }}>{labels[hover[movie.id] !== undefined ? hover[movie.id] : movie.rating]}</Box>
                            </Box>
                        </CardContent>
                    </Box>
                </Card>
            ))}
        </Box>
    );
};

export default SelectedMovies;