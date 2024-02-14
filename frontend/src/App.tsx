import './App.css';
import MenuBar from './components/MenuBar';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { green, grey } from '@mui/material/colors';
import MovieLibrary from './components/MovieLibrary';
import { Route, Routes } from 'react-router';
import Home from './components/Home';
import MovieSuggestions from './components/MovieSuggestions';
import Chat from './components/Chat';

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
      <Routes>
        <Route path='/' element={<Home />}/>
        <Route path='/MovieLibrary' element={<MovieLibrary />}/>
        <Route path='/MovieSuggestions' element={<MovieSuggestions />}/>
        <Route path='/Chat' element={<Chat />}/>
      </Routes>
    </ThemeProvider>
  )
}

export default App;
