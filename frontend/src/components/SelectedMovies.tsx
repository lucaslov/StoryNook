import { Box, Typography, Card, CardContent, CardMedia, IconButton, Button } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { ExtendedMovie } from '../interfaces/ExtendedMovie';

interface SelectedMoviesProps {
    selectedMovies: ExtendedMovie[];
    removeMovie: (id: number) => void; // Make sure type is correct: number or string based on your ID type
    triggerRecommendations: () => void;
    clearSelectedMovies: () => void; // Function to clear all selected movies
}

const SelectedMovies = ({ selectedMovies, removeMovie, triggerRecommendations, clearSelectedMovies }: SelectedMoviesProps) => {
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
            {selectedMovies.map((movie: ExtendedMovie, index: number) => (
                <Card key={index} sx={{
                    width: '90%',
                    display: 'flex',
                    flexDirection: 'row',
                    marginBottom: 2,
                    height: '8vh',
                    minHeight: 80,
                    overflow: 'hidden',
                    position: 'relative'
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
                    <CardMedia
                        component="img"
                        sx={{
                            width: '8vh',
                            height: '8vh',
                            objectFit: 'cover',
                            marginRight: '8px'
                        }}
                        image={movie.currentImageSrc}
                        alt={movie.title}
                    />
                    <CardContent sx={{
                        flex: '1',
                        display: 'flex',
                        alignItems: 'flex-start',
                        padding: '8px'
                    }}>
                        <Typography variant="subtitle1" noWrap sx={{ fontSize: '1.1rem' }}>
                            {movie.title}
                        </Typography>
                    </CardContent>
                </Card>
            ))}
        </Box>
    );
};

export default SelectedMovies;
