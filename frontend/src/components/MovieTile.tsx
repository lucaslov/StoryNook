import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Typography from '@mui/material/Typography';
import { Box, CardActionArea, CardActions, Rating } from '@mui/material';
import { useState } from 'react';
import StarIcon from '@mui/icons-material/Star';

const MovieTile = ({ imageSrc, title }: { imageSrc: string, title: string }) => {
    const [starsValue, setStarsValue] = useState(0);
    const [hover, setHover] = useState(-1);

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
        <Card sx={{ width: '23vw',
            display: 'flex',
            alignItems: 'center'}}>
            <CardActionArea>
                <CardMedia
                    component="img"
                    height="140"
                    image={imageSrc}
                />
                <CardContent>
                    <Typography gutterBottom variant="h5" component="div">
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
                    onChange={(event, newValue) => {
                        setStarsValue(newValue ?? 0);
                    }}
                    onChangeActive={(event, newHover) => {
                        setHover(newHover);
                    }}
                    emptyIcon={<StarIcon style={{ opacity: 0.55 }} fontSize="inherit" />}
                />
                {starsValue !== null && (
                    <Box sx={{ ml: 2 }}>{labels[hover !== -1 ? hover : starsValue]}</Box>
                )}
            </CardActions>
        </Card>
    )
}

export default MovieTile;