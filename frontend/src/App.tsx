import './App.css';
import MenuBar from './components/MenuBar';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { green, grey } from '@mui/material/colors';
import MovieLibrary from './components/MovieLibrary';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: green[900],
    },
    secondary: {
      main: grey[800],
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <MenuBar />
      <MovieLibrary />
    </ThemeProvider>
  )
}

export default App;
