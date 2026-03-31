
# Mood Helper App

**HKBU Final Year Project 2026**  
A simple and friendly web application that helps young people check their mood every day and receive gentle support.

---

### Main Features

- AI Emotion Detection (camera or upload photo)
- Automatic redirect to emotion support pages (Angry / Sad / Happy / Calm)
- Meditation, Relaxing Music, and Workout Videos for each emotion
- Mood Journal with notes
- Daily Streak & Motivation
- Dashboard and Calendar
- Emergency Support (Hong Kong helplines)

---

### How to Run the App

1. Unzip the project folder.

2. Open **Terminal** (Mac) or **Command Prompt** (Windows) and go to the project root folder (`mood-helper-app`).

3. **Start the AI Backend** (must run first):
   ``
   cd ..                          
   source venv/bin/activate       
   python mood_api.py
   ```
   Wait until you see: `* Running on http://127.0.0.1:5001`

4. **Start the Website** (open a **new Terminal** window):
   ```bash
   cd node-website
   node server.js
   ```
   You should see: `Website running at http://localhost:3000`

5. Open your browser and visit:  
   **http://localhost:3000**

---

### How to Use

- Click **"Let's check your mood now"** on the home page.
- Take a photo or upload an image.
- The AI will detect your emotion and redirect you.
- You can manually correct the emotion if needed, then click **"Save to Mood Journal"**.
- All records are saved in the browser (localStorage).

---

### Notes

- The AI model takes a few seconds to load the first time you run `python mood_api.py`.
- All mood records are saved only in your browser. Clearing browser data will delete all records.
- This project uses transfer learning to train the emotion model.



