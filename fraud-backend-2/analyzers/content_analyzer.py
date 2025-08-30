# analyzers/content_analyzer.py (Fixed with proper error handling)

import os
import re
from urllib.parse import urlparse, parse_qs
import string

try:
    import joblib
    base_dir = os.path.dirname(__file__)
    model_path = os.path.join(base_dir, '..', 'models', 'content_model.joblib')
    vectorizer_path = os.path.join(base_dir, '..', 'models', 'content_vectorizer.joblib')
    
    if os.path.exists(model_path) and os.path.exists(vectorizer_path):
        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
    else:
        model = None
        vectorizer = None
except (ImportError, FileNotFoundError):
    model = None
    vectorizer = None

def analyze_url_patterns(url):
    """Analyze URL patterns for phishing indicators"""
    features = {}
    
    try:
        # Basic URL length
        features['url_length'] = len(url)
        features['long_url'] = len(url) > 100
        
        # Parse URL components
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        query = parsed.query.lower()
        
        # Suspicious keywords in URL
        phishing_keywords = [
            'verify', 'confirm', 'update', 'suspend', 'secure', 'alert',
            'warning', 'expire', 'lock', 'urgent', 'immediate', 'action',
            'account', 'billing', 'payment', 'signin', 'login', 'auth'
        ]
        
        full_url_lower = url.lower()

         # Find and store the actual keywords found in the URL
        found_keywords = [keyword for keyword in phishing_keywords if keyword in full_url_lower]
        features['phishing_keywords'] = len(found_keywords)
        features['suspicious_keywords_found'] = found_keywords # Store the list
        features['has_phishing_keywords'] = len(found_keywords) > 0

        keyword_count = sum(1 for keyword in phishing_keywords if keyword in full_url_lower)
        features['phishing_keywords'] = keyword_count
        features['has_phishing_keywords'] = keyword_count > 0
        
        # Domain analysis
        features['domain_length'] = len(domain)
        features['has_subdomain'] = len(domain.split('.')) > 2
        features['domain_has_numbers'] = bool(re.search(r'\d', domain))
        features['domain_has_hyphens'] = '-' in domain
        
        # Path analysis
        features['path_length'] = len(path)
        features['path_depth'] = len([p for p in path.split('/') if p])
        
        # Query parameters
        features['has_query_params'] = bool(query)
        if query:
            params = parse_qs(query)
            features['query_param_count'] = len(params)
            
            # Suspicious query parameters
            suspicious_params = ['redirect', 'url', 'link', 'goto', 'target', 'continue']
            features['suspicious_params'] = any(param in query for param in suspicious_params)
        else:
            features['query_param_count'] = 0
            features['suspicious_params'] = False
        
        # URL shortener patterns
        shortener_domains = [
            'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly', 
            'short.link', 'tiny.cc', 'is.gd', 'buff.ly'
        ]
        features['is_shortener'] = domain in shortener_domains
        
        # Suspicious TLD
        tld = domain.split('.')[-1] if '.' in domain else ''
        suspicious_tlds = ['tk', 'ml', 'ga', 'cf', 'pw', 'top', 'click']
        features['suspicious_tld'] = tld in suspicious_tlds
        
        # IP address instead of domain
        ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        features['uses_ip'] = bool(re.search(ip_pattern, domain))
        
        # Special characters
        special_chars = set(url) - set(string.ascii_letters + string.digits + '.-_/?&=:')
        features['special_char_count'] = len(special_chars)
        features['has_special_chars'] = len(special_chars) > 5
        
        # Brand impersonation
        brands = [
            'paypal', 'amazon', 'microsoft', 'google', 'apple', 'facebook',
            'netflix', 'spotify', 'instagram', 'twitter', 'linkedin', 'ebay'
        ]
        
        # Check for brand names in suspicious contexts
        brand_impersonation = False
        for brand in brands:
            if brand in domain:
                # Check if it's the real domain
                real_domains = [f'{brand}.com', f'www.{brand}.com']
                if domain not in real_domains:
                    brand_impersonation = True
                    break
        
        features['brand_impersonation'] = brand_impersonation
        
        return features
        
    except Exception as e:
        # Return safe defaults
        return {
            'url_length': len(url) if url else 0,
            'long_url': False,
            'phishing_keywords': 0,
            'suspicious_keywords_found': [], 
            'has_phishing_keywords': False,
            'domain_length': 0,
            'has_subdomain': False,
            'domain_has_numbers': False,
            'domain_has_hyphens': False,
            'path_length': 0,
            'path_depth': 0,
            'has_query_params': False,
            'query_param_count': 0,
            'suspicious_params': False,
            'is_shortener': False,
            'suspicious_tld': False,
            'uses_ip': False,
            'special_char_count': 0,
            'has_special_chars': False,
            'brand_impersonation': False,
            'analysis_error': str(e)
        }

def calculate_content_risk_score(features):
    """Calculate risk score based on content features"""
    risk_score = 0.0
    
    # URL length risk
    if features.get('long_url', False):
        risk_score += 0.15
    
    # Phishing keywords
    keyword_count = features.get('phishing_keywords', 0)
    if keyword_count > 0:
        risk_score += min(keyword_count * 0.1, 0.3)
    
    # Suspicious domain features
    if features.get('domain_has_hyphens', False):
        risk_score += 0.1
    
    if features.get('suspicious_tld', False):
        risk_score += 0.25
    
    if features.get('uses_ip', False):
        risk_score += 0.3
    
    if features.get('is_shortener', False):
        risk_score += 0.2
    
    if features.get('brand_impersonation', False):
        risk_score += 0.4
    
    # Query parameter risks
    if features.get('suspicious_params', False):
        risk_score += 0.2
    
    if features.get('query_param_count', 0) > 5:
        risk_score += 0.1
    
    # Path complexity
    if features.get('path_depth', 0) > 4:
        risk_score += 0.1
    
    # Special characters
    if features.get('has_special_chars', False):
        risk_score += 0.1
    
    return min(max(risk_score, 0.0), 1.0)

def get_features(url: str) -> dict:
    """Analyzes the URL string and returns a risk score"""
    
    if not url or not isinstance(url, str):
        return {
            "error": "Invalid URL provided",
            "content_risk_prediction": 0,
            "content_risk_score": 0.5
        }
    
    try:
        # Analyze URL patterns
        pattern_features = analyze_url_patterns(url)
        
        # If we have trained models, use them
        if model is not None and vectorizer is not None:
            try:
                # Use the loaded vectorizer to transform the URL
                url_features = vectorizer.transform([url])
                
                # Predict and get the probability of it being phishing
                prediction = model.predict(url_features)
                probability = model.predict_proba(url_features)[0]
                
                # Get probability of phishing class (class 1)
                phishing_prob = probability[1] if len(probability) > 1 else probability[0]
                
                result = {
                    "content_risk_prediction": int(prediction[0]),
                    "content_risk_score": round(phishing_prob, 3),
                    "pattern_features": pattern_features,
                    "model_used": True
                }
                
            except Exception as model_error:
                # Fallback to rule-based scoring if model fails
                risk_score = calculate_content_risk_score(pattern_features)
                result = {
                    "content_risk_prediction": 1 if risk_score > 0.5 else 0,
                    "content_risk_score": round(risk_score, 3),
                    "pattern_features": pattern_features,
                    "model_used": False,
                    "model_error": str(model_error)
                }
        else:
            # No model available - use rule-based scoring
            risk_score = calculate_content_risk_score(pattern_features)
            result = {
                "content_risk_prediction": 1 if risk_score > 0.5 else 0,
                "content_risk_score": round(risk_score, 3),
                "pattern_features": pattern_features,
                "model_used": False,
                "model_status": "not_available"
            }
        
        return result
        
    except Exception as e:
        # Return safe fallback
        return {
            "error": f"Content analysis failed: {str(e)}",
            "content_risk_prediction": 0,
            "content_risk_score": 0.1,
            "analysis_method": "error_fallback"
        }