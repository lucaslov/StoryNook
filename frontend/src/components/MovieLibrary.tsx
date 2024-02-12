import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import MovieTile from './MovieTile';
const movies = [
    {
        imageSrc: "https://picsum.photos/200/301",
        title: "Film"
    },
    {
        imageSrc: "https://picsum.photos/200/302",
        title: "Film2"
    },
    {
        imageSrc: "https://picsum.photos/200/303",
        title: "Film2"
    },
    {
        imageSrc: "https://picsum.photos/200/304",
        title: "Film2"
    },
    {
        imageSrc: "https://picsum.photos/200/305",
        title: "Film2"
    },
    {
        imageSrc: "https://picsum.photos/201/300",
        title: "Film2"
    },
    {
        imageSrc: "https://picsum.photos/202/300",
        title: "Film2"
    },
    {
        imageSrc: "https://picsum.photos/203/300",
        title: "Film2"
    },
    {
        imageSrc: "https://picsum.photos/204/300",
        title: "Film2"
    }
]
const MovieLibrary = () => {
    return (
        <Box sx={{ flexGrow: 1, marginTop: 3 }}>
            <Grid container spacing={2} justifyContent={"center"}>
                {
                    movies.map(movie => {
                        return (
                            <Grid item>
                                <MovieTile imageSrc={movie.imageSrc} title={movie.title} />
                            </Grid>
                        )
                    })
                }
            </Grid>
        </Box>
    )
}

export default MovieLibrary;