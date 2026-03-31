from datasets import load_from_disk

print("Loading original dataset...")
dataset = load_from_disk("fer2013_dataset")

# Map to 4 classes only:
# 0 = Angry (includes original Angry + Disgust)
# 1 = Happy (includes original Happy + Surprise)
# 2 = Sad (includes original Sad + Fear)
# 3 = Neutral
def remap_to_4classes(examples):
    old_labels = examples["label"]
    new_labels = []
    for label in old_labels:
        if label in [0, 1]:      # Angry + Disgust
            new_labels.append(0)
        elif label in [3, 5]:    # Happy + Surprise
            new_labels.append(1)
        elif label in [2, 4]:    # Fear + Sad
            new_labels.append(2)
        else:                    # Neutral
            new_labels.append(3)
    examples["label"] = new_labels
    return examples

print("Filtering and remapping to 4 classes...")
new_dataset = dataset.map(remap_to_4classes, batched=True)

print("Saving new 4-class dataset...")
new_dataset.save_to_disk("fer2013_4class")

print("Done! New dataset saved as 'fer2013_4class'")
print("You now have only 4 emotions: Angry, Happy, Sad, Neutral")