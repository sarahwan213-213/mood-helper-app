const express = require('express');
const app = express();
const port = 3000;

// Serve all files from 'public' folder
app.use(express.static('public'));

// Home page
app.get('/', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cheuk Ying's Mood Helper</title>
  <style>
    body { font-family: Arial; text-align: center; background: #f0f2f6; padding: 50px; margin: 0; }
    h1 { color: #2c3e50; }
    a { color: #3498db; font-weight: bold; margin: 15px; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <h1>Welcome to Cheuk Ying's Personal Website</h1>
  <p>HKBU Final Year Project 2026</p>
  <p>This is my Mood Helper App — AI that detects your emotion and helps your well-being.</p>
  <p>
    <a href="/mood.html">Try Mood Detection</a> | <a href="/about.html">About Me</a>
  </p>
</body>
</html>
  `);
});

app.listen(port, () => {
  console.log(`Your website running at http://localhost:${port}`);
});