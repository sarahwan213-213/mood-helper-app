# Mood Helper

AI-Powered Facial Emotion Detection for Youth Mental Well-being

Final Year Honours Project | HKBU | 2025–2026

---

## How to Run

Open **two terminals** at the same time.

**Terminal 1 — AI Backend**
```bash
source venv/bin/activate
python mood_api.py
```

**Terminal 2 — Frontend**
```bash
cd node-website
node server.js
```

Then open **http://localhost:3000** in your browser.

> Both terminals must be running at the same time.

---

## About

A web application that detects facial emotions in real time using a Vision Transformer (ViT) model and provides personalised mental wellness recommendations.

## Features

- Real-time facial emotion detection via webcam or photo upload
- Personalised music, meditation and workout recommendations
- Mood Journal with local storage
- Weekly mood stats dashboard
- Daily check-in streak system
- Dark mode support
- Emergency mental health support (HK hotlines)

## Model

- Architecture: ViT-Base/16 fine-tuned on RAF-DB
- Test Accuracy: 84.91% | Weighted F1: 0.8486
- Classes: Angry / Happy / Sad / Calm

## Tech Stack

- Backend: Python, Flask, HuggingFace Transformers, PyTorch
- Frontend: HTML5, CSS3, Vanilla JavaScript, Node.js, Express

## Privacy

All images are processed locally. No data is stored or transmitted externally.