import express from 'express';
import http from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import { DatabaseService } from './services/DatabaseService';
import raceRoutes from './routes/races'; // Assuming this provides REST as well

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: "*", methods: ["GET", "POST"] }
});
const dbService = new DatabaseService();

app.use(cors());
app.use(express.json());
app.use('/api', raceRoutes);

// --- Real-time WebSocket Logic ---
io.on('connection', (socket) => {
  console.log('A client connected to the WebSocket.');
  socket.on('disconnect', () => {
    console.log('A client disconnected.');
  });
});

// Poll the database for changes and emit updates to all clients
setInterval(async () => {
  try {
    const qualifiedRaces = await dbService.getQualifiedRaces();
    io.emit('races:updated', qualifiedRaces);
  } catch (error) {
    console.error('Error polling for database updates:', error);
  }
}, 5000); // Poll every 5 seconds

const PORT = process.env.PORT || 8080;
server.listen(PORT, () => {
  console.log(`API Gateway and WebSocket server running on port ${PORT}`);
});