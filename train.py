import torch
from datasets import load_from_disk
from transformers import ViTImageProcessor, ViTForImageClassification, TrainingArguments, Trainer
import numpy as np
from sklearn.metrics import accuracy_score

device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

# Load the new 4-class dataset
dataset = load_from_disk("fer2013_4class")

processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")
model = ViTForImageClassification.from_pretrained(
    "google/vit-base-patch16-224-in21k",
    num_labels=4,  # Only 4 emotions
    ignore_mismatched_sizes=True
)
model.to(device)

# Preprocess images
def preprocess(examples):
    images = [img.convert("RGB") if img.mode != "RGB" else img for img in examples["image"]]
    inputs = processor(images, return_tensors="pt")
    examples["pixel_values"] = inputs["pixel_values"]
    return examples

dataset = dataset.map(preprocess, batched=True, remove_columns=["image"])

training_args = TrainingArguments(
    output_dir="./emotion_model_4class",
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=5,                 # More epochs for better accuracy
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_steps=100,
    learning_rate=2e-5,
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    greater_is_better=True,
    report_to="none",
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return {"accuracy": accuracy_score(labels, predictions)}

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    compute_metrics=compute_metrics,
)

print("Starting training with 4 emotions (Happy, Neutral, Sad, Angry)...")
trainer.train()

trainer.save_model("my_emotion_model_4class")
processor.save_pretrained("my_emotion_model_4class")
print("✅ Training finished! New model saved in 'my_emotion_model_4class'")