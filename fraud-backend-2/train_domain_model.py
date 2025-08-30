# train_domain_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import os
from urllib.parse import urlparse
import whois
from datetime import datetime

print("Starting Domain Model training process...")

# --- 1. Load The Local Dataset ---
DATASET_PATH = "data/processed/phishing_site_urls.csv"

try:
    df = pd.read_csv(DATASET_PATH)
except FileNotFoundError:
    print(f"🔴 ERROR: Dataset not found at '{DATASET_PATH}'")
    print("Please download the dataset from Kaggle and place it in the correct folder.")
    exit()

# The dataset has 'URL' and 'Label' columns. Rename them and process the label.
df.rename(columns={'URL': 'url', 'Label': 'label'}, inplace=True)
df['label'] = df['label'].apply(lambda x: 1 if x == 'bad' else 0)
df.dropna(subset=['url'], inplace=True)

# Let's use a sample of 10,000 for faster training. You can increase this later.
df = df.sample(n=10000, random_state=42)
print(f"Loaded {len(df)} URLs for feature generation.")

# --- 2. Feature Extraction ---
def get_domain_features(url):
    features = {}
    try:
        domain = urlparse(url).netloc
        try:
            w = whois.whois(domain)
            creation_date = w.creation_date
            if creation_date:
                creation_date = creation_date[0] if isinstance(creation_date, list) else creation_date
                age = (datetime.now() - creation_date).days
                features['domain_age'] = age
            else:
                features['domain_age'] = -1
        except Exception:
            features['domain_age'] = -1
        features['has_ssl'] = 1 if url.startswith('https') else 0
        features['domain_length'] = len(domain)
    except Exception:
        features['domain_age'] = -1
        features['has_ssl'] = 0
        features['domain_length'] = -1
    return features

print("Generating domain features... (This may take a while)")
features_list = [get_domain_features(url) for url in df['url']]
features_df = pd.DataFrame(features_list)
print("Feature generation complete.")

X = features_df
y = df['label']

# --- 3. Train, Evaluate, and Save ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("Training the RandomForestClassifier...")
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Domain Model Accuracy: {accuracy * 100:.2f}%")

os.makedirs('models', exist_ok=True)
joblib.dump(model, 'models/domain_model.joblib')
print("✅ Domain model saved to models/domain_model.joblib")