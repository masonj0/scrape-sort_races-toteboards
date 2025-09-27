// server.ts - API Gateway and WebSocket Server Skeleton

import express from 'express';
import { createServer } from 'http';
import { Server as SocketServer } from 'socket.io';
import cors from 'cors';

const app = express();
const httpServer = createServer(app);
const io = new SocketServer(httpServer, {
  cors: { origin: "*" }
});

app.use(cors());

app.get('/api/status', (req, res) => {
  res.json({ status: 'API Gateway is online' });
});

io.on('connection', (socket) => {
  console.log(`Client connected: ${socket.id}`);
  socket.on('disconnect', () => {
    console.log(`Client disconnected: ${socket.id}`);
  });
});

const PORT = 8080;
httpServer.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
});