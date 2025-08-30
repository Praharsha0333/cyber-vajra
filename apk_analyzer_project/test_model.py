import pickle
import json
import os
import glob
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# ==============================================================================
# MODEL EVALUATION SCRIPT
# ==============================================================================

def evaluate_model():
    """
    Loads the trained model, the full dataset, and evaluates the model's
    performance with a detailed report and a confusion matrix visualization.
    """
    print("--- Starting Model Evaluation ---")

    # --- 1. Load the Trained Model and Feature List ---
    print("Loading 'apk_classifier.pkl' and 'features.json'...")
    try:
        with open("apk_classifier.pkl", "rb") as f:
            model = pickle.load(f)
        with open("features.json", "r") as f:
            feature_list = json.load(f)
    except FileNotFoundError:
        print("\n❌ Error: Model or features file not found.")
        print("Please run 'train_model.py' first to create the model.")
        return

    # --- 2. Load the Full, Real Dataset ---
    # This uses the same logic as train_model.py to ensure consistency.
    print("Loading the full dataset for testing...")
    try:
        data_frames = []
        base_path = 'dataset'
        categories = {
            'Adware': 'malware', 'Benign': 'benign', 'Ransomware': 'malware',
            'Scareware': 'malware', 'SMSmalware': 'malware'
        }
        for category, label in categories.items():
            folder_path = os.path.join(base_path, category)
            all_csv_files = glob.glob(f"{folder_path}/**/*.csv", recursive=True)
            for f in all_csv_files:
                try:
                    df_temp = pd.read_csv(f, encoding='utf-8', on_bad_lines='skip')
                    df_temp['class'] = label
                    data_frames.append(df_temp)
                except Exception:
                    continue 
        df = pd.concat(data_frames, ignore_index=True)
        # Drop any rows with missing data and the old 'Label' column if it exists
        df = df.dropna().drop(columns=['Label'], errors='ignore')
    except Exception as e:
        print(f"\n❌ Error: Could not load the dataset. Please ensure the 'dataset' folder is structured correctly. Details: {e}")
        return

    # --- 3. Prepare the Data for Prediction ---
    # Ensure the test data has the same columns in the same order as the training data.
    print("Preparing feature vectors...")
    df_features = pd.DataFrame(columns=feature_list)
    df_combined = pd.concat([df_features, df], ignore_index=True, sort=False).fillna(0)
    
    X_test = df_combined[feature_list]
    y_true = df_combined['class']

    # --- 4. Make Predictions ---
    print("Making predictions on the full dataset...")
    y_pred = model.predict(X_test)

    # --- 5. Show Evaluation Metrics ---
    print("\n✅ --- Evaluation Report --- ✅")
    print("This report shows how well the model performed on the full dataset.\n")
    print(classification_report(y_true, y_pred, target_names=['benign', 'malware']))

    # --- 6. Generate and Save Confusion Matrix ---
    print("Generating confusion matrix visualization...")
    cm = confusion_matrix(y_true, y_pred, labels=['benign', 'malware'])
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Predicted Benign', 'Predicted Malware'], 
                yticklabels=['Actual Benign', 'Actual Malware'])
    plt.title('Confusion Matrix')
    plt.ylabel('Actual Class')
    plt.xlabel('Predicted Class')
    
    # Save the plot to a file instead of trying to show it
    plt.savefig('confusion_matrix.png')
    print("\n✅ Confusion matrix saved to 'confusion_matrix.png'")
    print("---------------------------------")


if __name__ == '__main__':
    evaluate_model()

