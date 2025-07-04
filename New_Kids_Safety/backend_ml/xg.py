import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import joblib
import pickle

# Set paths
driver_path = r"C:\Users\91701\Desktop\mldemo\cbrowser\chromedriver-win64\chromedriver.exe"
model_path_lstm = "lstm_toxicity_model.h5"
model_path_xgb = "xgb_model.pkl"
vectorizer_path = "tfidf_vectorizer.pkl"
tokenizer_path = "tokenizer.pkl"

# Selenium setup
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(service=Service(driver_path), options=options)

# Load models
model_lstm = load_model(model_path_lstm)
model_xgb = joblib.load(model_path_xgb)
vectorizer = joblib.load(vectorizer_path)
with open(tokenizer_path, "rb") as f:
    tokenizer = pickle.load(f)

max_len = 150  # must match training

def get_text_from_url(url):
    try:
        driver.get(url)
        time.sleep(3)  # Wait for full JS to load
        soup = BeautifulSoup(driver.page_source, "html.parser")
        return soup.get_text()
    except Exception as e:
        print("❌ Failed to load page:", e)
        return ""

def check_url_safety(url):
    print(f"\n🌐 Checking: {url}")
    text = get_text_from_url(url).lower()

    if not text.strip():
        print("❌ No content found.")
        return

    # XGBoost prediction
    tfidf_features = vectorizer.transform([text])
    xgb_pred = model_xgb.predict(tfidf_features)[0]

    # LSTM prediction
    seq = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=max_len)
    lstm_pred = model_lstm.predict(padded)[0][0]

    # Combine logic
    print(f"🔎 XGBoost: {'unsafe' if xgb_pred == 1 else 'safe'}, LSTM: {lstm_pred:.2f}")
    if xgb_pred == 1 or lstm_pred >= 0.5:
        print("❌ not allowed (unsafe)")
    else:
        print("✅ allowed (safe)")

# === Main loop ===
while True:
    url = input("\n🔗 Enter a URL to check (or 'exit'): ").strip()
    if url.lower() == "exit":
        break
    check_url_safety(url)

driver.quit()
