import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Typography from '@mui/material/Typography';
import { Box, CardActionArea, CardActions, Rating } from '@mui/material';
import { useState, useEffect } from 'react';
import StarIcon from '@mui/icons-material/Star';
import { checkEndpointStatus } from '../repositories/MoviesRepository';

const PLACEHOLDER_IMAGE = "https://via.placeholder.com/150?text=Poster+Not+Available";

const MovieTile = ({ imageSrc, title }: { imageSrc: string, title: string }) => {
    const [starsValue, setStarsValue] = useState(0);
    const [hover, setHover] = useState(-1);
    const [currentImageSrc, setCurrentImageSrc] = useState(imageSrc);

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

    useEffect(() => {
        checkEndpointStatus(imageSrc).then(isValid => {
            if (!isValid) {
                setCurrentImageSrc(PLACEHOLDER_IMAGE);
            }
        });
    }, [imageSrc]);

    return (
        <Card sx={{
            width: '15vw',
            height: '35vh',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            overflow: 'hidden',
        }}>
            <CardActionArea>
                <CardMedia
                    component="img"
                    height="200vh"
                    image={currentImageSrc}
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
            <CardActions>
                <Rating
                    name="hover-feedback"
                    value={starsValue}
                    precision={0.5}
                    getLabelText={getLabelText}
                    onChange={(_, newValue) => {
                        setStarsValue(newValue ?? 0);
                    }}
                    onChangeActive={(_, newHover) => {
                        setHover(newHover);
                    }}
                    emptyIcon={<StarIcon style={{ opacity: 0.55 }} fontSize="inherit" />}
                />
                {starsValue !== null && (
                    <Box sx={{ ml: 2 }}>{labels[hover !== -1 ? hover : starsValue]}</Box>
                )}
            </CardActions>
        </Card>
    );
}

export default MovieTile;
