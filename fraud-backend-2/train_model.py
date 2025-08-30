import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import joblib
import warnings
import os
import glob
from datetime import datetime

warnings.filterwarnings('ignore')

def train_and_evaluate_model(feature_file: str):
    """Loads features, trains a new model, combines it with existing models, and evaluates the ensemble."""
    try:
        # --- Define models directory and ensure it exists ---
        MODELS_DIR = 'models'
        os.makedirs(MODELS_DIR, exist_ok=True)
        
        # --- Load and VALIDATE existing models ---
        existing_model_files = glob.glob(os.path.join(MODELS_DIR, 'model_*.joblib'))
        estimators = []
        if existing_model_files:
            print(f"Found {len(existing_model_files)} existing models. Loading and validating them for ensemble...")
            for i, model_path in enumerate(existing_model_files):
                try:
                    model = joblib.load(model_path)
                    if hasattr(model, 'predict'):
                        estimators.append((f'existing_model_{i}', model))
                    else:
                        print(f"Warning: File '{model_path}' is not a valid classifier model. Skipping.")
                except Exception as e:
                    print(f"Warning: Could not load model {model_path}. Skipping. Error: {e}")
        else:
            print("No existing models found. Training from scratch...")

        # --- Load the dataset ---
        print(f"\nLoading dataset from '{feature_file}'...")
        
        # Check if file exists
        if not os.path.exists(feature_file):
            print(f"Error: File '{feature_file}' not found!")
            print("Please run 'python generate_features.py' first to create the features file.")
            return
        
        # Drop non-feature columns that might exist in some datasets
        all_cols = pd.read_csv(feature_file, nrows=0).columns.tolist()
        cols_to_drop = [col for col in ['FILENAME', 'URL', 'Domain', 'TLD', 'Title'] if col in all_cols]
        
        if cols_to_drop:
            print(f"Ignoring non-feature columns: {cols_to_drop}")
            df = pd.read_csv(feature_file).drop(columns=cols_to_drop)
        else:
            df = pd.read_csv(feature_file)
            
        print(f"Successfully loaded '{feature_file}' with {df.shape[0]} rows and {df.shape[1]} columns.")

        # --- Find the target column ---
        target_column = None
        possible_target_names = ['label_numeric', 'Type', 'phishing', 'label']
        for name in possible_target_names:
            if name in df.columns:
                target_column = name
                break
        
        if not target_column:
            print(f"\nError: Could not find a valid target column in '{feature_file}'.")
            print(f"Available columns: {df.columns.tolist()}")
            print("Expected target column names: label_numeric, Type, phishing, or label")
            return
            
        print(f"Detected target column: '{target_column}'")
        
        # Check class distribution
        print(f"\nClass distribution in target column '{target_column}':")
        print(df[target_column].value_counts())
        
        if df[target_column].nunique() < 2:
            print("\n--- DATA VALIDATION ERROR ---")
            print(f"Error: The dataset contains only one class in the '{target_column}' column.")
            print("A binary classifier needs both positive and negative examples.")
            return

        X = df.drop(columns=[target_column])
        y = df[target_column]

        # --- Robust Data Cleaning Step ---
        print("\nCleaning data...")
        for col in X.columns:
            X[col] = pd.to_numeric(X[col], errors='coerce')
        X.fillna(0, inplace=True)
        print("Data cleaning complete. All feature columns are now numeric.")
        
        # --- Save the feature columns list ---
        feature_list_filename = os.path.join(MODELS_DIR, 'model_features.joblib')
        joblib.dump(X.columns.tolist(), feature_list_filename)
        print(f"✅ Feature list saved to '{feature_list_filename}'")
        print(f"   Total features: {len(X.columns)}")

        # --- Split data for training and testing ---
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        print(f"\nData split into {len(X_train)} training samples and {len(X_test)} testing samples.")

        # --- Define a new model to be trained ---
        print("\nTraining new Random Forest model...")
        new_model = RandomForestClassifier(
            n_estimators=100, 
            random_state=42, 
            n_jobs=-1,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2
        )
        
        # Train the new model
        new_model.fit(X_train, y_train)
        
        # Save the new model with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_model_filename = os.path.join(MODELS_DIR, f'model_{timestamp}.joblib')
        joblib.dump(new_model, new_model_filename)
        print(f"✅ New model saved to '{new_model_filename}'")
        
        # Add to estimators for ensemble
        estimators.append((f'new_model_{timestamp}', new_model))

        # --- Create and evaluate ensemble if multiple models exist ---
        if len(estimators) > 1:
            print(f"\nCreating ensemble with {len(estimators)} models...")
            ensemble = VotingClassifier(estimators=estimators, voting='soft', n_jobs=-1)
            ensemble.fit(X_train, y_train)
            
            # Save the ensemble
            ensemble_filename = os.path.join(MODELS_DIR, 'ensemble_model.joblib')
            joblib.dump(ensemble, ensemble_filename)
            print(f"✅ Ensemble model saved to '{ensemble_filename}'")
            
            # Use ensemble for evaluation
            model_to_evaluate = ensemble
            model_name = "Ensemble"
        else:
            # Only one model, save it as the ensemble too
            ensemble_filename = os.path.join(MODELS_DIR, 'ensemble_model.joblib')
            joblib.dump(new_model, ensemble_filename)
            print(f"✅ Single model saved as ensemble to '{ensemble_filename}'")
            
            # Use the single model for evaluation
            model_to_evaluate = new_model
            model_name = "Random Forest"
        
        # --- Evaluate the model's performance ---
        print(f"\n--- {model_name} Model Evaluation ---")
        
        # Make predictions
        y_pred = model_to_evaluate.predict(X_test)
        y_pred_proba = model_to_evaluate.predict_proba(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Accuracy on Test Set: {accuracy:.4f} ({accuracy*100:.2f}%)")
        
        # Classification report
        print("\n--- Classification Report ---")
        print(classification_report(y_test, y_pred, 
                                  target_names=['Legitimate (0)', 'Phishing (1)']))
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Create visualization
        plt.figure(figsize=(10, 8))
        
        # Plot confusion matrix
        plt.subplot(2, 2, 1)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['Legitimate', 'Phishing'], 
                   yticklabels=['Legitimate', 'Phishing'])
        plt.title(f'{model_name} Confusion Matrix')
        plt.ylabel('Actual Label')
        plt.xlabel('Predicted Label')
        
        # Plot feature importance (if available)
        if hasattr(model_to_evaluate, 'feature_importances_'):
            plt.subplot(2, 2, 2)
            feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': model_to_evaluate.feature_importances_
            }).sort_values('importance', ascending=False).head(10)
            
            plt.barh(feature_importance['feature'], feature_importance['importance'])
            plt.xlabel('Importance')
            plt.title('Top 10 Feature Importances')
            plt.gca().invert_yaxis()
        
        # Save the plot
        plot_filename = 'model_evaluation.png'
        plt.tight_layout()
        plt.savefig(plot_filename)
        print(f"\n✅ Evaluation plots saved to '{plot_filename}'")
        
        # Print summary
        print("\n" + "="*50)
        print("TRAINING COMPLETE!")
        print("="*50)
        print(f"✅ Model saved to: {ensemble_filename}")
        print(f"✅ Features list saved to: {feature_list_filename}")
        print(f"✅ Accuracy: {accuracy*100:.2f}%")
        print(f"✅ The model is ready to use in your Flask application!")
        print("\nNext step: Run 'python app.py' to start the fraud detection server.")

    except FileNotFoundError:
        print(f"\nError: The file '{feature_file}' was not found.")
        print("Please run 'python generate_features.py' first to create the features file.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # Use the output from generate_features.py
    dataset_filename = 'features.csv'
    
    print("🚀 Starting Model Training")
    print("="*50)
    
    train_and_evaluate_model(dataset_filename)