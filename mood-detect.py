import streamlit as st
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image
import torch
import os

@st.cache_resource
def load_model():
    processor = ViTImageProcessor.from_pretrained("trpakov/vit-face-expression")
    model = ViTForImageClassification.from_pretrained("trpakov/vit-face-expression")
    return processor, model

processor, model = load_model()

emotions = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

st.title("Mood Detection - Test")

uploaded_file = st.file_uploader("Upload photo", type=["jpg", "png", "jpeg"])
webcam = st.camera_input("Take photo")

img = None
if uploaded_file is not None:
    img = Image.open(uploaded_file)
elif webcam is not None:
    img = Image.open(webcam)

if img is not None:
    st.image(img, caption="Your photo", use_column_width=True)

    inputs = processor(img.convert("RGB"), return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    predicted_idx = logits.argmax(-1).item()
    emotion = emotions[predicted_idx]
    confidence = torch.softmax(logits, dim=-1)[0][predicted_idx].item() * 100

    st.success(f"Detected: {emotion} ({confidence:.1f}%)")

    music_map = {
        "Happy": "music/happy.mp3",
        "Sad": "music/calm.mp3",
    }
    music_file = music_map.get(emotion)
    if music_file and os.path.exists(music_file):
        st.audio(music_file, format="audio/mp3")