import pandas as pd
from urllib.parse import urlparse
import re

# Define suspicious keywords globally so they're available in error handling
SUSPICIOUS_KEYWORDS = ['login', 'secure', 'account', 'webscr', 'cmd', 'bin', 
                       'verification', 'signin', 'paypal', 'banking']

def normalize_labels(label):
    """
    Converts common text labels into a standard numeric format (1 for bad, 0 for good).
    This function is case-insensitive and handles numeric labels too.
    """
    # Convert to string and lowercase for comparison
    label_str = str(label).lower().strip()
    
    # Handle numeric labels directly
    if label_str in ['0', '0.0']:
        return 0
    elif label_str in ['1', '1.0']:
        return 1
    
    # Lists of keywords for bad/good URLs
    bad_keywords = ['phishing', 'bad', 'malicious', 'spam', 'fraud', 'scam']
    good_keywords = ['legitimate', 'good', 'benign', 'safe', 'clean', 'normal']
    
    # Check for exact matches first
    if label_str in bad_keywords:
        return 1
    elif label_str in good_keywords:
        return 0
    
    # Check if any keyword is contained in the label
    for keyword in bad_keywords:
        if keyword in label_str:
            return 1
    
    for keyword in good_keywords:
        if keyword in label_str:
            return 0
    
    # If we can't determine, print the label for debugging
    print(f"Warning: Could not normalize label '{label}'. Skipping.")
    return None

def find_column(df, possible_names):
    """Finds the first matching column name from a list of possibilities, case-insensitively."""
    df_columns_lower = {col.lower(): col for col in df.columns}
    for name in possible_names:
        if name.lower() in df_columns_lower:
            return df_columns_lower[name.lower()]
    return None

def safe_urlparse(url):
    """Safely parse URLs, handling various edge cases."""
    try:
        # Clean the URL
        url = str(url).strip()
        
        # Handle special characters that might cause issues
        # Remove any brackets that might cause IPv6 issues
        if '[' in url and ']' in url:
            # This might be a malformed IPv6 URL, try to clean it
            url = url.replace('[', '').replace(']', '')
        
        # Add protocol if missing
        if not re.match(r'^https?://', url):
            url = 'http://' + url
        
        # Try to parse
        parsed = urlparse(url)
        
        # If parsing succeeded but no hostname, try to extract it manually
        if not parsed.hostname:
            # Try to extract domain from URL manually
            match = re.search(r'(?:https?://)?([^/\s]+)', url)
            if match:
                hostname = match.group(1)
            else:
                hostname = ''
        else:
            hostname = parsed.hostname
            
        return parsed, hostname
        
    except Exception:
        # If all else fails, return empty parsed object and hostname
        return None, ''

def generate_features(url: str) -> dict:
    """Extracts numerical features from a given URL."""
    features = {}
    url = str(url).strip()  # Ensure url is a clean string
    
    try:
        # Use safe parsing
        parsed_url, hostname = safe_urlparse(url)
        
        # Extract path component
        path_component = ''
        if hostname and hostname in url:
            hostname_index = url.find(hostname)
            if hostname_index != -1:
                path_start_index = hostname_index + len(hostname)
                path_component = url[path_start_index:]
        elif parsed_url and parsed_url.path:
            path_component = parsed_url.path

        # Calculate features
        features['url_length'] = len(url)
        features['hostname_length'] = len(hostname) if hostname else 0
        features['subdomain_count'] = hostname.count('.') if hostname else 0
        features['has_ip_address'] = 1 if re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', hostname) else 0
        features['path_length'] = len(path_component)
        features['directory_count'] = path_component.count('/')
        features['count_hyphen'] = url.count('-')
        features['count_at'] = url.count('@')
        features['count_question'] = url.count('?')
        features['count_percent'] = url.count('%')
        features['count_dot'] = url.count('.')
        features['count_equal'] = url.count('=')
        features['count_http'] = url.lower().count('http')
        features['count_www'] = url.lower().count('www')
        
        # Check for suspicious keywords
        url_lower = url.lower()
        for keyword in SUSPICIOUS_KEYWORDS:
            features[f'has_{keyword}'] = 1 if keyword in url_lower else 0
            
    except Exception as e:
        # If any error occurs, return zeros for all features
        print(f"Warning: Error processing URL '{url[:50]}...': {str(e)[:100]}")
        
        # Create default features with zeros
        features = {
            'url_length': len(url) if url else 0,
            'hostname_length': 0,
            'subdomain_count': 0,
            'has_ip_address': 0,
            'path_length': 0,
            'directory_count': 0,
            'count_hyphen': url.count('-') if url else 0,
            'count_at': url.count('@') if url else 0,
            'count_question': url.count('?') if url else 0,
            'count_percent': url.count('%') if url else 0,
            'count_dot': url.count('.') if url else 0,
            'count_equal': url.count('=') if url else 0,
            'count_http': url.lower().count('http') if url else 0,
            'count_www': url.lower().count('www') if url else 0
        }
        
        # Add keyword features
        for keyword in SUSPICIOUS_KEYWORDS:
            features[f'has_{keyword}'] = 0
        
    return features

if __name__ == '__main__':
    # === IMPORTANT: EDIT THIS LINE ===
    input_filename = 'phishing_features.csv'  # <-- Your dataset filename
    output_filename = 'features.csv'
    
    try:
        print(f"Loading data from '{input_filename}'...")
        df = pd.read_csv(input_filename)
        
        print(f"Dataset shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        
        # --- Smart Column Detection ---
        url_col = find_column(df, ['url', 'URL', 'link', 'links', 'website'])
        label_col = find_column(df, ['type', 'Type', 'Label', 'class', 'phishing', 'result', 'label', 'status'])
        
        if not url_col:
            print("\nError: Could not find a URL column.")
            print(f"Available columns: {df.columns.tolist()}")
            print("Please ensure your dataset has a column named 'url', 'URL', or similar.")
            exit(1)
            
        if not label_col:
            print("\nError: Could not find a Label column.")
            print(f"Available columns: {df.columns.tolist()}")
            print("Please ensure your dataset has a column named 'Type', 'Label', 'class', etc.")
            exit(1)
            
        print(f"Detected URL column: '{url_col}'")
        print(f"Detected Label column: '{label_col}'")
        
        # Show sample of labels to understand the format
        print(f"\nSample labels (first few unique values):")
        unique_labels = df[label_col].unique()[:10]
        for label in unique_labels:
            print(f"  - '{label}' (type: {type(label).__name__})")
        
        # Remove rows with missing URLs
        initial_count = len(df)
        df.dropna(subset=[url_col], inplace=True)
        if initial_count != len(df):
            print(f"Removed {initial_count - len(df)} rows with missing URLs")
        
        print(f"\nProcessing {len(df)} URLs...")
        print("This may take a few minutes for large datasets...")
        
        # Process in chunks for better progress tracking
        chunk_size = 10000
        features_list = []
        
        for i in range(0, len(df), chunk_size):
            chunk_end = min(i + chunk_size, len(df))
            chunk = df[url_col].iloc[i:chunk_end]
            
            # Process this chunk
            chunk_features = chunk.apply(generate_features)
            features_list.extend(chunk_features.tolist())
            
            # Show progress
            processed = chunk_end
            percentage = (processed / len(df)) * 100
            print(f"  Processed {processed}/{len(df)} URLs ({percentage:.1f}%)")
        
        # Convert to DataFrame
        print("Converting features to DataFrame...")
        features_df = pd.DataFrame(features_list)
        
        print("Normalizing labels...")
        df['label_numeric'] = df[label_col].apply(normalize_labels)
        
        # Check how many labels were successfully normalized
        before_drop = len(df)
        df.dropna(subset=['label_numeric'], inplace=True)
        after_drop = len(df)
        
        if before_drop != after_drop:
            print(f"Warning: Dropped {before_drop - after_drop} rows with unrecognizable labels")
        
        if len(df) == 0:
            print("\nError: No valid labels found after normalization!")
            print("Please check your label column values.")
            print(f"Expected values like: 'phishing', 'legitimate', '0', '1', etc.")
            exit(1)
        
        # Convert to integer
        df['label_numeric'] = df['label_numeric'].astype(int)
        
        # Reset indices to ensure alignment
        features_df = features_df.reset_index(drop=True)
        df = df.reset_index(drop=True)
        
        # Combine features with labels
        final_df = pd.concat([features_df, df['label_numeric']], axis=1)
        
        # Save to CSV
        print(f"Saving to '{output_filename}'...")
        final_df.to_csv(output_filename, index=False)
        
        # Print summary
        print(f"\n✅ Successfully generated features and saved to '{output_filename}'")
        print(f"Created {len(final_df)} rows:")
        print(f"  - Legitimate URLs (0): {(final_df['label_numeric'] == 0).sum():,}")
        print(f"  - Phishing URLs (1): {(final_df['label_numeric'] == 1).sum():,}")
        
        # Show class distribution
        if len(final_df) > 0:
            phishing_percentage = (final_df['label_numeric'] == 1).sum() / len(final_df) * 100
            print(f"  - Class distribution: {phishing_percentage:.1f}% phishing, {100-phishing_percentage:.1f}% legitimate")
        
        # Show feature summary
        print(f"\nFeature columns created: {len(features_df.columns)}")
        print(f"Feature names: {', '.join(features_df.columns[:5])}... (and {len(features_df.columns)-5} more)")

    except FileNotFoundError:
        print(f"\nError: Input file '{input_filename}' not found.")
        print("Please make sure the file exists in the current directory.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()