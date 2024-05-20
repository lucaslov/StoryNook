import React, { useState } from 'react';
import { Container, TextField, Button, List, ListItem, ListItemText, Dialog, DialogTitle, DialogContent, Typography, CircularProgress, Box } from '@mui/material';
import axios from 'axios';

interface QueryResponsePair {
  query: string;
  response: string;
  context: any;
}

const Chat: React.FC = () => {
  const [query, setQuery] = useState('');
  const [responses, setResponses] = useState<QueryResponsePair[]>([]);
  const [selectedContext, setSelectedContext] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (query.trim() === '') return;

    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/llm-recommend', null, { params: { user_input: query } });
      setResponses([{ query, response: response.data.llmResponse, context: response.data.context }, ...responses]);
      setQuery('');
    } catch (error) {
      console.error('Error fetching recommendation:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleShowContext = (context: any) => {
    setSelectedContext(context);
  };

  const handleCloseContext = () => {
    setSelectedContext(null);
  };

  return (
    <Container style={{ marginTop: '2rem', textAlign: 'center' }}>
      <TextField
        label="Enter your movie query"
        variant="outlined"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        style={{ marginBottom: '1rem', width: '40em' }}
      />
      <Button variant="contained" color="primary" onClick={handleSubmit} style={{ marginLeft: '1rem' }}>
        Submit
      </Button>

      {loading && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            zIndex: 9999,
          }}
        >
          <CircularProgress />
        </Box>
      )}

      <List style={{ marginTop: '2rem', width: '90%', margin: '0 auto' }}>
        {responses.map((pair, index) => (
          <ListItem key={index} alignItems="flex-start" style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '1rem', marginBottom: '1rem' }}>
            <ListItemText
              primary={<Typography variant="h6">{`Query: ${pair.query}`}</Typography>}
              secondary={
                <>
                  <Typography variant="body1" style={{ marginTop: '0.5rem' }}>{`Response: ${pair.response}`}</Typography>
                  <Button
                    variant="contained"
                    color="secondary"
                    onClick={() => handleShowContext(pair.context)}
                    style={{ marginTop: '0.5rem', float: 'right' }}
                  >
                    Show Context
                  </Button>
                </>
              }
            />
          </ListItem>
        ))}
      </List>

      <Dialog open={!!selectedContext} onClose={handleCloseContext} maxWidth="md" fullWidth>
        <DialogTitle>Context</DialogTitle>
        <DialogContent>
          <pre>{JSON.stringify(selectedContext, null, 2)}</pre>
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default Chat;
