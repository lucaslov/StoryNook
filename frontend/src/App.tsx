import './App.css';
import { Route, Routes } from 'react-router';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { green, grey } from '@mui/material/colors';
import CssBaseline from '@mui/material/CssBaseline';

import MenuBar from './components/MenuBar';
import MovieLibrary from './components/MovieLibrary';
import Home from './components/Home';
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
        <Route path='/Chat' element={<Chat />}/>
      </Routes>
    </ThemeProvider>
  )
}

export default App;
