import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Typography from '@mui/material/Typography';
import { Box, CardActionArea, CardActions, Rating } from '@mui/material';
import { useState, useEffect } from 'react';
import StarIcon from '@mui/icons-material/Star';
import axios from 'axios';

const MovieTile = ({ movieId, onClick }: { movieId: number, onClick: (rating: number) => void }) => {

    useEffect(() => {
        const fetchMovieData = async () => {
            try {
                const response = await axios.get(`http://0.0.0.0:8000/movies/${movieId}`);
                setTitle(response.data.title);
                setPosterPath(response.data.posterPath);
            } catch (error) {
                console.error("Failed to fetch movie data:", error);
            }
        };

        fetchMovieData();
    }, [movieId]);

    const [rating, setRating] = useState(0);
    const [hover, setHover] = useState(-1);
    const [title, setTitle] = useState('');
    const [posterPath, setPosterPath] = useState('');

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
        <Card sx={{
            width: '15vw',
            height: '35vh',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            overflow: 'hidden',
        }}>
            <CardActionArea onClick={() => onClick(10)}>
                <CardMedia
                    component="img"
                    height="200vh"
                    image={posterPath}
                />
                <CardContent>
                    <Typography gutterBottom variant="h5" component="div" sx={{
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                    }}>
                        {title}
                    </Typography>
                </CardContent>
            </CardActionArea>
            <CardActions sx={{ justifyContent: 'center', width: '100%' }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <Rating
                        name="hover-feedback"
                        value={rating}
                        precision={0.5}
                        getLabelText={getLabelText}
                        onChange={(_, newValue) => {
                            setRating(newValue ?? 0);
                            if (newValue) {
                                onClick(newValue)
                            }
                        }}
                        onChangeActive={(_, newHover) => {
                            setHover(newHover);
                        }}
                        emptyIcon={<StarIcon style={{ opacity: 0.55 }} fontSize="inherit" />}
                    />
                    <Box sx={{ mt: 1 }}>
                        {labels[hover !== -1 ? hover : rating]}
                    </Box>
                </Box>
            </CardActions>
        </Card>
    );
}

export default MovieTile;