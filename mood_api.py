from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image
import io
import torch
import torch.nn.functional as F
 
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
 
# ── Model ─────────────────────────────────────────────────────────────────────
MODEL_PATH = "./my_emotion_model"
 
processor = ViTImageProcessor.from_pretrained(MODEL_PATH)
model     = ViTForImageClassification.from_pretrained(MODEL_PATH)
model.eval()
 
# Class order matches config.json id2label exactly:
# {"0": "Angry", "1": "Happy", "2": "Sad", "3": "Calm"}
OUTPUT_CLASSES = ["Angry", "Happy", "Sad", "Calm"]
 
# ── Temperature ───────────────────────────────────────────────────────────────
# T=2.0 softens overconfident Calm predictions under webcam conditions
# without making the distribution so flat it loses discriminative power.
TEMPERATURE = 2.0
 
# ── Calibration weights ───────────────────────────────────────────────────────
# Conservative inverse-frequency adjustment.
# Kept close to 1.0 to avoid overcorrection.
# Order: [Angry, Happy, Sad, Calm]
#
#   Angry : slightly boosted (underrepresented, 11.6% of training data)
#   Happy : slightly reduced (overrepresented, 49.4% of training data)
#   Sad   : slightly boosted (18.4% of training data)
#   Calm  : baseline 1.00
_RAW_WEIGHTS  = torch.tensor([1.10, 0.80, 1.10, 1.00], dtype=torch.float32)
CALIB_WEIGHTS = _RAW_WEIGHTS / _RAW_WEIGHTS.sum()   # normalise to sum = 1
 
# ── Confidence threshold ──────────────────────────────────────────────────────
LOW_CONFIDENCE_THRESHOLD = 40.0
 
 
# ── Prediction endpoint ───────────────────────────────────────────────────────
@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
 
    # CORS preflight
    if request.method == 'OPTIONS':
        resp = jsonify({})
        resp.headers['Access-Control-Allow-Origin']  = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return resp
 
    # Input validation
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400
 
    file      = request.files['file']
    img_bytes = file.read()
 
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception as e:
        return jsonify({"error": f"Invalid image: {str(e)}"}), 400
 
    # ── Step 1: Inference ────────────────────────────────────────────────────
    # ViTImageProcessor handles resizing to 224x224 internally.
    inputs = processor(img, return_tensors="pt")
 
    with torch.no_grad():
        logits = model(**inputs).logits[0]   # shape: (4,)
 
    print("Raw logits        :", [f"{x:.4f}" for x in logits.tolist()])
 
    # ── Step 2: Temperature Scaling ──────────────────────────────────────────
    # Divide logits by T before softmax → softer probability distribution.
    scaled_logits = logits / TEMPERATURE
    temp_probs    = F.softmax(scaled_logits, dim=-1)
 
    print("Temp-scaled probs :", [f"{x:.4f}" for x in temp_probs.tolist()])
 
    # ── Step 3: Conservative Calibration ────────────────────────────────────
    # Light reweighting to partially correct RAF-DB class imbalance.
    cal_probs = temp_probs * CALIB_WEIGHTS
    cal_probs = cal_probs / cal_probs.sum()   # re-normalise
 
    print("Cal probs         :", [f"{x:.4f}" for x in cal_probs.tolist()])
 
    # ── Step 4: Argmax — never overridden ───────────────────────────────────
    pred_idx       = cal_probs.argmax().item()
    predicted      = OUTPUT_CLASSES[pred_idx]
    confidence     = cal_probs[pred_idx].item() * 100.0
    low_confidence = confidence < LOW_CONFIDENCE_THRESHOLD
 
    # ── Step 5: Build response ───────────────────────────────────────────────
    # UI bars use CALIBRATED probs → always consistent with the predicted label.
    all_scores = {
        cls: round(cal_probs[i].item() * 100.0, 1)
        for i, cls in enumerate(OUTPUT_CLASSES)
    }
 
    # Raw (original logit softmax) scores for research / evaluation page.
    raw_scores = {
        cls: round(F.softmax(logits, dim=-1)[i].item() * 100.0, 1)
        for i, cls in enumerate(OUTPUT_CLASSES)
    }
 
    print(f"Predicted         : {predicted}  |  Confidence: {confidence:.1f}%  |  Low-conf: {low_confidence}")
    print("All scores        :", all_scores)
    print("---")
 
    resp = jsonify({
        "emotion":        predicted,
        "confidence":     round(confidence, 1),
        "all_scores":     all_scores,     # calibrated — drives UI bars
        "raw_scores":     raw_scores,     # original softmax — for research
        "top_class":      predicted,
        "low_confidence": low_confidence,
    })
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
 
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
 