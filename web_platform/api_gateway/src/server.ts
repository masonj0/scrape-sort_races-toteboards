import dotenv from 'dotenv';
dotenv.config(); // Load environment variables from .env file

import express from 'express';
import raceRoutes from './routes/races';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Mount the race routes
app.use('/api', raceRoutes);

app.get('/', (req, res) => {
  res.send('Checkmate API Gateway is running.');
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
