# train_content_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
import os

print("Starting Content Model training process...")

# --- 1. Load The Local Dataset ---
DATASET_PATH = "data/processed/phishing_site_urls.csv"

try:
    df = pd.read_csv(DATASET_PATH)
except FileNotFoundError:
    print(f"🔴 ERROR: Dataset not found at '{DATASET_PATH}'")
    print("Please download the dataset from Kaggle and place it in the correct folder.")
    exit()

# Process the columns
df.rename(columns={'URL': 'url', 'Label': 'label'}, inplace=True)
df['label'] = df['label'].apply(lambda x: 1 if x == 'bad' else 0)
df.dropna(subset=['url'], inplace=True)
print(f"Loaded {len(df)} URLs.")

X = df['url']
y = df['label']

# --- 2. Feature Extraction & Training ---
print("Extracting text features and training model...")
vectorizer = TfidfVectorizer()
X_features = vectorizer.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_features, y, test_size=0.2, random_state=42)
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# --- 3. Evaluate and Save ---
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Content Model Accuracy: {accuracy * 100:.2f}%")

os.makedirs('models', exist_ok=True)
joblib.dump(model, 'models/content_model.joblib')
joblib.dump(vectorizer, 'models/content_vectorizer.joblib')
print("\n✅ Content model and vectorizer saved to 'models/' directory.")