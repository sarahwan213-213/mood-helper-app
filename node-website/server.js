const express = require('express');
const path = require('path');

const app = express();
const port = 3000;

// Serve all static files from public folder
app.use(express.static(path.join(__dirname, 'public')));

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/mood.html', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'mood.html'));
});

// Fallback - send index.html for any other route
app.use((req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(port, () => {
  console.log(`✅ Your website is running at http://localhost:${port}`);
  console.log(`   Mood detection page → http://localhost:${port}/mood.html`);
});