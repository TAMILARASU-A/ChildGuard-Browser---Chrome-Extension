import face_recognition
import cv2
import os
import numpy as np

dataset_path = "dataset"
known_encodings = []
known_labels = []

for label in os.listdir(dataset_path):
    person_dir = os.path.join(dataset_path, label)
    if not os.path.isdir(person_dir):
        continue

    for filename in os.listdir(person_dir):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(person_dir, filename)
            image = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                known_labels.append(label)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

def detect_identity():
    """Captures a frame from the webcam and identifies the person."""
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to capture frame from webcam.")
        return "no_frame"

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    print(f"🔍 Detected {len(face_encodings)} face(s).")

    for face_encoding in face_encodings:
        distances = face_recognition.face_distance(known_encodings, face_encoding)
        print("📏 Face distances:", distances)

        if len(distances) == 0:
            continue

        best_match_index = np.argmin(distances)
        if distances[best_match_index] < 0.6:  # Confidence threshold
            identity = known_labels[best_match_index]
            print(f"✅ Match found: {identity}")
            return identity

    print("❓ No match found.")
    return "unknown"



