import { Box, Typography, Card, CardContent, CardMedia, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { ExtendedMovie } from '../interfaces/ExtendedMovie';

interface RecommendationsPopupProps {
  recommendations: ExtendedMovie[];
  closePopup: () => void;
}

const RecommendationsPopup = ({ recommendations, closePopup }: RecommendationsPopupProps) => {
  return (
    <Box sx={{
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1300
    }}>
      <IconButton
        sx={{
          position: 'absolute',
          top: 8,
          right: 8,
          color: 'white',
          zIndex: 1
        }}
        onClick={closePopup}
      >
        <CloseIcon />
      </IconButton>
      <Box sx={{
        width: '80%',
        height: '80%',
        backgroundColor: 'white',
        overflowY: 'auto',
        padding: 2,
        borderRadius: 2
      }}>
        <Typography variant="h5" sx={{ textAlign: 'center', marginBottom: 2 }}>Recommended Movies</Typography>
        {recommendations.map((movie: ExtendedMovie, index: number) => (
          <Card key={index} sx={{
            display: 'flex',
            flexDirection: 'row',
            marginBottom: 2,
            height: '8vh',
            minHeight: 80,
            overflow: 'hidden'
          }}>
            <CardMedia
              component="img"
              sx={{
                width: '8vh',
                height: '8vh',
                objectFit: 'cover'
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
    </Box>
  );
};

export default RecommendationsPopup;