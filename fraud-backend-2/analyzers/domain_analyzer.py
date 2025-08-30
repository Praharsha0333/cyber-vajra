# analyzers/domain_analyzer.py (Fixed with proper error handling)

import os
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime
import tldextract
import re

try:
    import joblib
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'domain_model.joblib')
    if os.path.exists(model_path):
        model = joblib.load(model_path)
    else:
        model = None
except (ImportError, FileNotFoundError):
    model = None

def get_domain_age(domain):
    """Get domain age with multiple fallbacks"""
    try:
        # Try python-whois first
        import whois
        w = whois.whois(domain)
        creation_date = w.creation_date
        
        if isinstance(creation_date, list):
            creation_date = creation_date[0] if creation_date else None
        
        if creation_date:
            age = (datetime.now() - creation_date).days
            return max(age, 0)  # Ensure non-negative
        else:
            return -1
    except:
        # Fallback: estimate based on domain patterns
        return estimate_domain_age(domain)

def estimate_domain_age(domain):
    """Estimate domain age based on patterns (fallback method)"""
    try:
        # Heuristic: newer domains often have numbers or suspicious patterns
        suspicious_patterns = [
            r'\d{4}',  # Year in domain (often recent)
            r'-\d+$',  # Ends with dash and numbers
            r'\d{2,}',  # Multiple consecutive digits
        ]
        
        # Check for suspicious patterns
        for pattern in suspicious_patterns:
            if re.search(pattern, domain):
                return 30  # Assume relatively new
        
        # Well-known old domains
        old_domains = [
            'google', 'yahoo', 'microsoft', 'apple', 'amazon',
            'facebook', 'twitter', 'wikipedia', 'github', 'stackoverflow'
        ]
        
        if any(old_domain in domain.lower() for old_domain in old_domains):
            return 5000  # Very old
        
        # Default: assume moderately aged
        return 365
        
    except:
        return -1

def analyze_domain_structure(domain):
    """Analyze domain structure for suspicious patterns"""
    features = {}
    
    try:
        # Extract domain parts
        extracted = tldextract.extract(domain)
        subdomain = extracted.subdomain
        domain_name = extracted.domain
        suffix = extracted.suffix
        
        # Domain length analysis
        features['domain_length'] = len(domain)
        features['subdomain_count'] = len(subdomain.split('.')) if subdomain else 0
        
        # Suspicious patterns
        features['has_numbers'] = bool(re.search(r'\d', domain_name))
        features['has_hyphens'] = '-' in domain_name
        features['hyphen_count'] = domain_name.count('-')
        
        # Suspicious TLD
        suspicious_tlds = ['tk', 'ml', 'ga', 'cf', 'pw', 'top', 'click', 'download', 'space']
        features['suspicious_tld'] = suffix.lower() in suspicious_tlds
        
        # Brand impersonation check
        brand_keywords = [
            'paypal', 'amazon', 'microsoft', 'google', 'apple', 'facebook',
            'netflix', 'spotify', 'instagram', 'twitter', 'linkedin'
        ]
        features['brand_impersonation'] = any(brand in domain_name.lower() for brand in brand_keywords)
        
        # URL shortener check
        shorteners = ['bit.ly', 'tinyurl', 't.co', 'goo.gl', 'ow.ly', 'short.link']
        features['is_shortener'] = domain.lower() in shorteners
        
        # Entropy calculation (randomness indicator)
        import math
        if domain_name:
            entropy = -sum(p * math.log2(p) for p in 
                          [domain_name.count(c)/len(domain_name) for c in set(domain_name)] if p > 0)
            features['domain_entropy'] = entropy
        else:
            features['domain_entropy'] = 0
        
        return features
        
    except Exception as e:
        # Return safe defaults
        return {
            'domain_length': len(domain),
            'subdomain_count': 0,
            'has_numbers': False,
            'has_hyphens': False,
            'hyphen_count': 0,
            'suspicious_tld': False,
            'brand_impersonation': False,
            'is_shortener': False,
            'domain_entropy': 0,
            'analysis_error': str(e)
        }

def calculate_domain_risk_score(features):
    """Calculate risk score based on domain features"""
    risk_score = 0.0
    
    # Age-based risk
    domain_age = features.get('domain_age', -1)
    if domain_age == -1:
        risk_score += 0.1  # Unknown age penalty
    elif domain_age < 30:
        risk_score += 0.4  # Very new domain
    elif domain_age < 90:
        risk_score += 0.2  # New domain
    elif domain_age > 365 * 2:
        risk_score -= 0.1  # Old domain bonus
    
    # SSL check
    if not features.get('has_ssl', True):
        risk_score += 0.3
    
    # Domain structure risks
    if features.get('suspicious_tld', False):
        risk_score += 0.3
    
    if features.get('brand_impersonation', False):
        risk_score += 0.4
    
    if features.get('is_shortener', False):
        risk_score += 0.2
    
    # Length and complexity
    domain_length = features.get('domain_length', 0)
    if domain_length > 50:
        risk_score += 0.2
    elif domain_length < 5:
        risk_score += 0.1
    
    # Hyphen abuse
    hyphen_count = features.get('hyphen_count', 0)
    if hyphen_count > 2:
        risk_score += 0.2
    elif hyphen_count > 0:
        risk_score += 0.1
    
    # High entropy (random strings)
    entropy = features.get('domain_entropy', 0)
    if entropy > 3.5:
        risk_score += 0.15
    
    # Subdomain abuse
    subdomain_count = features.get('subdomain_count', 0)
    if subdomain_count > 2:
        risk_score += 0.1
    
    return min(max(risk_score, 0.0), 1.0)

def get_features(url: str) -> dict:
    """Main function to analyze domain and return features"""
    try:
        # Parse URL
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        if not domain:
            return {
                "error": "Invalid URL - no domain found",
                "domain_risk": 0.5,
                "domain_age": -1,
                "has_ssl": False,
                "domain_length": 0
            }
        
        # Basic features
        basic_features = {
            'has_ssl': url.startswith('https://'),
            'domain_length': len(domain),
        }
        
        # Get domain age
        basic_features['domain_age'] = get_domain_age(domain)
        
        # Analyze domain structure
        structure_features = analyze_domain_structure(domain)
        
        # Combine all features
        all_features = {**basic_features, **structure_features}
        
        # Calculate risk score
        if model is not None:
            try:
                # Prepare features for ML model
                feature_df = pd.DataFrame([{
                    'domain_age': all_features.get('domain_age', -1),
                    'has_ssl': int(all_features.get('has_ssl', False)),
                    'domain_length': all_features.get('domain_length', 0)
                }])
                
                # Get model prediction
                prediction = model.predict(feature_df)[0]
                all_features['domain_risk'] = int(prediction)
                
            except Exception as e:
                # Fallback to rule-based scoring
                all_features['domain_risk_score'] = calculate_domain_risk_score(all_features)
                all_features['domain_risk'] = 1 if all_features['domain_risk_score'] > 0.5 else 0
                all_features['model_error'] = str(e)
        else:
            # No model available - use rule-based scoring
            all_features['domain_risk_score'] = calculate_domain_risk_score(all_features)
            all_features['domain_risk'] = 1 if all_features['domain_risk_score'] > 0.5 else 0
            all_features['model_status'] = 'not_available'
        
        return all_features
        
    except Exception as e:
        # Return safe fallback
        return {
            "error": f"Domain analysis failed: {str(e)}",
            "domain_risk": 0.5,
            "domain_age": -1,
            "has_ssl": url.startswith('https://') if url else False,
            "domain_length": len(urlparse(url).netloc) if url else 0,
            "analysis_method": "error_fallback"
        }