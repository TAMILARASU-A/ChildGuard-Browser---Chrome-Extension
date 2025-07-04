from flask import Flask, jsonify, request
from flask_cors import CORS
import face_recognition
import cv2
import os
import numpy as np
import smtplib
from email.mime.text import MIMEText
import threading
import time
import requests
from bs4 import BeautifulSoup

# ML imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import joblib
import pickle

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")

# --- Flask and CORS ---
app = Flask(__name__)
CORS(app)

# --- Email Settings ---
EMAIL_FROM = "arasu9725@gmail.com"
EMAIL_TO = "2403717662221041@cit.edu.in"
EMAIL_PASSWORD = "ligo mhya aqad wgou"

# --- Load blacklist and unsafe words ---
try:
    with open("restricted_sites.txt", "r") as f:
        RESTRICTED_SITES = [line.strip().lower() for line in f if line.strip()]
except FileNotFoundError:
    print("⚠️  restricted_sites.txt not found!")
    RESTRICTED_SITES = []

try:
    with open("unsafe_words.txt", "r") as f:
        UNSAFE_WORDS = [line.strip().lower() for line in f if line.strip()]
except FileNotFoundError:
    print("⚠️  unsafe_words.txt not found!")
    UNSAFE_WORDS = []

# --- Face recognition setup ---
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
                print(f"✅ Loaded face for: {label} ({filename})")
            else:
                print(f"⚠️  No face found in: {img_path}")
print(f"🎯 Total known faces loaded: {len(known_encodings)}")

current_user = {"identity": "unknown"}

# --- ML Model Setup ---

# Paths (adjust if needed)
driver_path = r"C:\Users\91701\Desktop\mldemo\cbrowser\chromedriver-win64\chromedriver.exe"
model_path_lstm = "lstm_toxicity_model.h5"
model_path_xgb = "xgb_model.pkl"
vectorizer_path = "tfidf_vectorizer.pkl"
tokenizer_path = "tokenizer.pkl"

# Setup headless selenium webdriver (for dynamic content)
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# Load models
model_lstm = load_model(model_path_lstm)
model_xgb = joblib.load(model_path_xgb)
vectorizer = joblib.load(vectorizer_path)
with open(tokenizer_path, "rb") as f:
    tokenizer = pickle.load(f)

max_len = 150  # must match your LSTM training

# --- Helper Functions for ML Checking ---

def get_text_from_url(url):
    try:
        driver.get(url)
        time.sleep(3)  # wait for JS content
        soup = BeautifulSoup(driver.page_source, "html.parser")
        return soup.get_text()
    except Exception as e:
        print("❌ Failed to load page:", e)
        return ""

def ml_check_url_safety(url):
    text = get_text_from_url(url).lower()
    if not text.strip():
        print("❌ No content found for ML check.")
        return False  # treat no content as safe here or handle as needed

    # XGBoost prediction
    tfidf_features = vectorizer.transform([text])
    xgb_pred = model_xgb.predict(tfidf_features)[0]

    # LSTM prediction
    seq = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=max_len)
    lstm_pred = model_lstm.predict(padded)[0][0]

    print(f"🔎 ML Results - XGBoost: {'unsafe' if xgb_pred == 1 else 'safe'}, LSTM: {lstm_pred:.2f}")

    # Return True if unsafe (block), else False
    return (xgb_pred == 1) or (lstm_pred >= 0.5)

# --- Email alert ---
def send_email_alert(site):
    msg = MIMEText(f"⚠️ ALERT: A child tried to access: {site} (Blocked due to unsafe content)")
    msg["Subject"] = "Kids Safety Alert - Unsafe Content Blocked"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
        print("✅ Email alert sent")
    except Exception as e:
        print("❌ Failed to send email:", e)

# --- Content word analyzer ---
def analyze_content(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text().lower()
        for word in UNSAFE_WORDS:
            if word in text_content:
                print(f"🔥 Unsafe word '{word}' found in content of: {url}")
                return True
        return False
    except Exception as e:
        print(f"❌ Error processing content of {url}: {e}")
        return False

# --- API Endpoints ---
@app.route("/")
def index():
    return "✅ Kids Safety Backend Running!"

@app.route("/who_is_using")
def who_is_using():
    return jsonify(current_user)

@app.route("/check_site", methods=["POST"])
def check_site():
    data = request.get_json()
    url = data.get("url", "").lower()
    print(f"[CHECKING URL] {url}")

    if current_user["identity"] == "child":
        # Check URL blacklist first
        for site in RESTRICTED_SITES:
            if site in url:
                send_email_alert(url)
                return jsonify({"blocked": True})

        # Check unsafe words list
        if analyze_content(url):
            send_email_alert(url)
            return jsonify({"blocked": True})

        # Run ML model check on URL content
        if ml_check_url_safety(url):
            send_email_alert(url)
            return jsonify({"blocked": True})

    # Allow if no conditions triggered block
    return jsonify({"blocked": False})

# --- Face recognition ---
def detect_identity():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ Error: Webcam not accessible.")
        return "no_frame"
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("❌ Failed to capture frame from webcam.")
        return "no_frame"

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    print(f"🔍 Detected {len(face_encodings)} face(s).")

    for face_encoding in face_encodings:
        distances = face_recognition.face_distance(known_encodings, face_encoding)
        print("📏 Face distances:", distances)
        if len(distances) == 0:
            continue
        best_match_index = np.argmin(distances)
        if distances[best_match_index] < 0.6:
            identity = known_labels[best_match_index]
            print(f"✅ Match found: {identity}")
            return identity
    print("❓ No match found.")
    return "unknown"

def run_face_loop():
    while True:
        identity = detect_identity()
        current_user["identity"] = identity
        print("Detected identity:", identity)
        time.sleep(2000)  # check every 20 seconds (adjust as needed)

if __name__ == "__main__":
    threading.Thread(target=run_face_loop, daemon=True).start()
    app.run(port=5000)
