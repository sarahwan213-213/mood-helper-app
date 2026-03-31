import streamlit as st
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image
import torch
import os
import pandas as pd
import plotly.express as px

# Load model (pre-trained or your trained one)
@st.cache_resource
def load_model():
    processor = ViTImageProcessor.from_pretrained("trpakov/vit-face-expression")
    model = ViTForImageClassification.from_pretrained("trpakov/vit-face-expression")
    return processor, model

processor, model = load_model()

emotions = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

JOURNAL_FILE = "mood_journal.csv"

if not os.path.exists(JOURNAL_FILE):
    pd.DataFrame(columns=["Timestamp", "Mood", "Note"]).to_csv(JOURNAL_FILE, index=False)

page = st.sidebar.radio("Menu", ["Mood Detection", "Mood Journal", "Chat"])

if page == "Mood Detection":
    st.title("Mood Detection")
    uploaded_file = st.file_uploader("Upload photo", type=["jpg", "png"])
    webcam = st.camera_input("Take photo")

    img = None
    if uploaded_file:
        img = Image.open(uploaded_file)
    elif webcam:
        img = Image.open(webcam)

    if img:
        st.image(img, caption="Your photo")
        inputs = processor(img.convert("RGB"), return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits
        idx = logits.argmax(-1).item()
        emotion = emotions[idx]
        conf = torch.softmax(logits, dim=-1)[0][idx].item() * 100
        st.success(f"Emotion: **{emotion}** ({conf:.1f}%)")

        # Music
        music = {"Happy": "music/happy.mp3", "Sad": "music/calm.mp3"}.get(emotion)
        if music and os.path.exists(music):
            st.audio(music, format="audio/mp3")

elif page == "Mood Journal":
    st.title("Mood Journal")
    note = st.text_area("How are you feeling?")
    if st.button("Save"):
        if note:
            entry = pd.DataFrame({"Timestamp": [pd.Timestamp.now()], "Mood": ["Detected later"], "Note": [note]})
            entry.to_csv(JOURNAL_FILE, mode='a', header=False, index=False)
            st.success("Saved!")
    if os.path.exists(JOURNAL_FILE):
        df = pd.read_csv(JOURNAL_FILE)
        if not df.empty:
            fig = px.bar(df["Mood"].value_counts(), title="Mood Trends")
            st.plotly_chart(fig)

elif page == "Chat":
    st.title("Chat with Me")
    msg = st.text_input("You:")
    if msg:
        if "sad" in msg.lower():
            st.write("I'm sorry you're feeling sad. Want to talk about it?")
        elif "happy" in msg.lower():
            st.write("That's great! What's making you happy?")
        else:
            st.write("I'm listening — tell me more!")