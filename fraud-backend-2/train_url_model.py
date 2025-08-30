# train_url_model.py

import pandas as pd
import os
from services.enhanced_url_checker import EnhancedURLChecker

def detect_columns(df):
    """Auto-detect URL and label columns from dataset"""
    url_candidates = ['url', 'URL', 'Url', 'website', 'Website', 'domain', 'Domain', 'hostname', 'Hostname']
    label_candidates = ['label', 'Label', 'class', 'Class', 'result', 'Result', 'phishing', 'Phishing', 'status', 'Status']
    
    url_col = None
    label_col = None
    
    for col in df.columns:
        if col.strip() in url_candidates:
            url_col = col
        if col.strip() in label_candidates:
            label_col = col
    
    return url_col, label_col

def main():
    print("=== URL Phishing Detection Model Training ===\n")
    
    checker = EnhancedURLChecker()
    
    dataset_path = input("Enter path to your Kaggle phishing dataset CSV file: ").strip()
    
    if not os.path.exists(dataset_path):
        print(f"❌ File not found: {dataset_path}")
        print("\n💡 Popular Kaggle datasets for phishing detection:")
        print("1. 'Phishing Website Dataset' by Shashwat Tiwari")
        print("2. 'Website Phishing Dataset' by Ali Mezher")  
        print("3. 'Phishing Websites Dataset' by Ananya Podder")
        return
    
    print(f"📂 Loading dataset from: {dataset_path}")
    
    try:
        df = pd.read_csv(dataset_path)
        print(f"\n📊 Dataset preview (first 5 rows):")
        print(df.head())
        print(f"\n📋 Columns available: {list(df.columns)}")
        print(f"📈 Total rows in dataset: {len(df)}")
    except Exception as e:
        print(f"❌ Error reading dataset: {e}")
        return
    
    # Detect URL + label columns
    url_col, label_col = detect_columns(df)
    
    if not url_col or not label_col:
        print("\n❌ Could not auto-detect URL/Label columns.")
        print("👉 Please rename your dataset to have:")
        print("   - URL column: 'url' or 'domain'")
        print("   - Label column: 'label' or 'phishing'")
        return
    
    print(f"\n✅ Detected URL column: {url_col}")
    print(f"✅ Detected Label column: {label_col}")
    
    # Confirm before training
    response = input(f"\n🚀 Start training? This may take several minutes. (y/n): ").lower()
    if response != 'y':
        print("Training cancelled.")
        return
    
    print("\n🔧 Starting model training...")
    success = checker.train_model(dataset_path, save_model=True)
    
    if success:
        print("\n✅ Model training completed successfully!")
        print("📁 Model saved to 'models/' directory")
        
        print("\n🧪 Testing model with sample URLs...")
        test_urls = [
            "https://www.google.com",
            "https://www.wikipedia.org",
            "https://github.com",
            "http://bit.ly/suspicious-link",
            "https://paypal-verify-account.tk",
            "http://amazon-security.ml"
        ]
        
        for url in test_urls:
            try:
                result = checker.check_url_risk(url)
                status_emoji = "✅" if result['overall_status'] == 'legitimate' else "⚠️" if result['overall_status'] == 'suspicious' else "❌"
                print(f"{status_emoji} {url}")
                print(f"   Status: {result['overall_status']} (Score: {result['risk_score']}, Confidence: {result['confidence']})")
            except Exception as e:
                print(f"❌ Error testing {url}: {e}")
        
        print("\n🎉 Setup complete! You can now use the EnhancedURLChecker in your application.")
    
    else:
        print("\n❌ Model training failed. Please check dataset format and try again.")

if __name__ == "__main__":
    main()
