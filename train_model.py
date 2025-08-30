import pandas as pd
import numpy as np
import pickle
import os
import glob
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb

# ==============================================================================
# AI MODEL TRAINING SCRIPT (ADVANCED & TUNED)
# ==============================================================================

def train_model():
    """
    Loads the real dataset, scales features, trains a balanced and tuned 
    LightGBM classifier with early stopping, evaluates its performance, 
    and saves the necessary files.
    """
    print("--- Starting AI model training using the REAL dataset ---")

    # --- STEP 1: LOAD THE REAL DATASET ---
    print("Loading real dataset from the 'dataset/' folder...")
    try:
        data_frames = []
        base_path = 'dataset'
        categories = {
            'Adware': 'malware', 'Benign': 'benign', 'Ransomware': 'malware',
            'Scareware': 'malware', 'SMSmalware': 'malware'
        }
        
        for category, label in categories.items():
            folder_path = os.path.join(base_path, category)
            if not os.path.isdir(folder_path):
                print(f"Warning: Directory not found for category '{category}'. Skipping.")
                continue
            
            all_csv_files = glob.glob(f"{folder_path}/**/*.csv", recursive=True)
            for f in all_csv_files:
                try:
                    df_temp = pd.read_csv(f, encoding='utf-8', on_bad_lines='skip')
                    df_temp['class'] = label
                    data_frames.append(df_temp)
                except Exception as e:
                    print(f"Warning: Could not read file {f}. Skipping. Error: {e}")
                    continue
        
        if not data_frames:
            print("\n❌ Error: No data files were found or loaded from the 'dataset' directory.")
            return

        df = pd.concat(data_frames, ignore_index=True)
        df = df.dropna().drop(columns=['Label'], errors='ignore')
        
        all_columns = [col for col in df.columns if col != 'class']
        features = [col for col in all_columns if pd.api.types.is_numeric_dtype(df[col])]
        
        non_numeric_cols = [col for col in all_columns if col not in features]
        if non_numeric_cols:
            print(f"\nWarning: The following non-numeric columns were found and will be excluded from training: {non_numeric_cols}\n")

    except Exception as e:
        print(f"\n❌ Error: A critical error occurred while loading the dataset. Details: {e}")
        return

    # --- STEP 2: PREPARE DATA FOR TRAINING ---
    print("Preparing data for training...")
    X = df[features]
    y = df['class']

    y_mapped = y.map({'benign': 0, 'malware': 1})

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_mapped, test_size=0.25, random_state=42, stratify=y_mapped
    )

    print("Scaling features to a standard range...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # --- STEP 3: TRAIN THE MODEL (BALANCED, TUNED, WITH EARLY STOPPING) ---
    print("Training the LightGBM Classifier with advanced techniques...")

    # Handle Class Imbalance by calculating the ratio of benign (0) to malware (1) samples.
    # This tells the model to pay more attention to the minority class during training.
    try:
        scale_pos_weight = y_train.value_counts()[0] / y_train.value_counts()[1]
    except ZeroDivisionError:
        scale_pos_weight = 1

    # Use a more tuned LightGBM model for better performance.
    model = lgb.LGBMClassifier(
        n_estimators=1000,          # Train up to 1000 trees, but early stopping will find the best number
        learning_rate=0.05,
        num_leaves=64,
        scale_pos_weight=scale_pos_weight, # Apply the balancing weight
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1
    )
    
    # Train with Early Stopping to prevent overfitting and find the optimal number of trees.
    # The model will stop training if the f1 score on the test set doesn't improve for 100 rounds.
    model.fit(
        X_train_scaled, y_train,
        eval_set=[(X_test_scaled, y_test)],
        eval_metric="f1",
        callbacks=[lgb.early_stopping(100, verbose=True), lgb.log_evaluation(period=100)]
    )

    # --- STEP 4: EVALUATE THE MODEL ---
    print("\n--- Final Model Evaluation ---")
    y_pred = model.predict(X_test_scaled)
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Simple Accuracy on Test Set: {accuracy:.4f}")

    print("\n--- Detailed Performance Metrics on Test Set ---")
    print(classification_report(y_test, y_pred, target_names=['benign', 'malware']))

    # --- STEP 5: SAVE THE MODEL, FEATURES, AND SCALER ---
    print("\nSaving final model, feature list, and scaler...")
    with open('apk_classifier.pkl', 'wb') as f:
        pickle.dump(model, f)
        
    with open('features.json', 'w') as f:
        json.dump(features, f)

    with open('scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
        
    print("✅ Training complete. All necessary files have been saved.")
    print("---------------------------------------------------------")

if __name__ == '__main__':
    train_model()

