from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image
import io
import torch

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load model
processor = ViTImageProcessor.from_pretrained("trpakov/vit-face-expression")
model = ViTForImageClassification.from_pretrained("trpakov/vit-face-expression")
model.eval()

original_emotions = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

emotion_mapping = {
    "Angry": "Angry",
    "Disgust": "Angry",
    "Fear": "Sad",
    "Happy": "Happy",
    "Sad": "Sad",
    "Surprise": "Happy",
    "Neutral": "Neutral"
}

@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    img_bytes = file.read()
    img = Image.open(io.BytesIO(img_bytes))

    img = img.convert("RGB")
    img = img.resize((224, 224))

    inputs = processor(img, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits[0]

    # Print raw logits for debugging
    print("Raw logits:", logits.tolist())

    predicted_idx = logits.argmax(-1).item()
    original_emotion = original_emotions[predicted_idx]

    confidence = torch.softmax(logits, dim=-1)[predicted_idx].item() * 100

    # Low confidence → Neutral (helps reduce wrong "Sad" on subtle smiles)
    if confidence < 60:
        final_emotion = "Neutral"
    else:
        final_emotion = emotion_mapping.get(original_emotion, original_emotion)

    response = jsonify({
        "emotion": final_emotion,
        "confidence": f"{confidence:.1f}%",
        "original": original_emotion
    })
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)