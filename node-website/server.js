const express = require('express');
const path = require('path');

const app = express();
const port = 3000;

console.log("Starting server...");

app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
  console.log("Home page requested");
  res.sendFile(path.join(__dirname, 'public', 'mood.html'));
});

app.get('/mood.html', (req, res) => {
  console.log("Mood page requested");
  res.sendFile(path.join(__dirname, 'public', 'mood.html'));
});

app.listen(port, () => {
  console.log(`✅ SUCCESS! Website is running at http://localhost:${port}`);
  console.log(`   Open your browser and go to: http://localhost:3000`);
});