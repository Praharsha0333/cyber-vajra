# analyzers/reputation_analyzer.py - FIXED VERSION WITH BETTER DEBUGGING

import os
import base64
import requests
from urllib.parse import urlparse
import time
import logging
from pysafebrowsing import SafeBrowsing

# Setup logging for debugging
logger = logging.getLogger(__name__)

# Load API key from environment variables with fallback
API_KEY = os.getenv('VIRUSTOTAL_API_KEY')
VT_API_URL = "https://www.virustotal.com/api/v3/urls"

# Simple blacklist for common malicious domains (fallback)
KNOWN_MALICIOUS_DOMAINS = {
    # Common phishing/malware domains - update this list periodically
    'malicious-site.tk',
    'phishing-example.ml',
    'fake-paypal.ga',
    'suspicious-domain.cf',
    'suspicious-paypal-login.tk',
    'paypal-verify-account.tk',
    'amazon-security.ml',
    'amazon-verify.ml',
    # Add more as needed
}

# Known safe domains (whitelist)
KNOWN_SAFE_DOMAINS = {
    'google.com', 'youtube.com', 'facebook.com', 'twitter.com', 'instagram.com',
    'wikipedia.org', 'github.com', 'stackoverflow.com', 'microsoft.com', 
    'apple.com', 'amazon.com', 'netflix.com', 'linkedin.com', 'reddit.com',
    'paypal.com', 'ebay.com', 'adobe.com', 'dropbox.com', 'spotify.com',
    'starbucks.com', 'mcdonalds.com', 'coca-cola.com', 'nike.com', 'adidas.com'
}

def check_domain_whitelist(domain):
    """Check if domain is in our safe list"""
    try:
        # Remove www. prefix for checking
        clean_domain = domain.lower().replace('www.', '')
        
        # Check exact matches
        if clean_domain in KNOWN_SAFE_DOMAINS:
            return True
        
        # Check if it's a subdomain of a known safe domain
        for safe_domain in KNOWN_SAFE_DOMAINS:
            if clean_domain.endswith('.' + safe_domain):
                return True
        
        return False
    except:
        return False

# ... (keep other imports and code) ...

def query_google_safe_browsing(url: str) -> dict:
    """Queries the Google Safe Browsing API using the pysafebrowsing library."""
    api_key = os.getenv('GOOGLE_SAFE_BROWSING_API_KEY')
    if not api_key:
        return {"is_known_threat": False, "threat_type": "api_key_missing", "error": None}
    
    try:
        sb = SafeBrowsing(api_key) # CORRECTED CLASS NAME
        response = sb.lookup_urls([url])
        
        # Check if the URL is in the response dictionary, meaning it's a threat
        if url in response and response[url].get('malicious'):
            threat_info = response[url]
            return {
                "is_known_threat": True,
                "threat_type": threat_info.get("threat_type", "Unknown"),
                "error": None
            }
            
        return {"is_known_threat": False, "threat_type": None, "error": None}

    except Exception as e:
        return {"is_known_threat": False, "threat_type": None, "error": str(e)}
    

def check_domain_blacklist(domain):
    """Check if domain is in our malicious list"""
    try:
        clean_domain = domain.lower().replace('www.', '')
        return clean_domain in KNOWN_MALICIOUS_DOMAINS
    except:
        return False

def query_virustotal(url):
    """Query VirusTotal API with proper error handling and debugging"""
    print(f"🔍 VirusTotal API Check: {API_KEY is not None}")
    
    if not API_KEY:
        print("⚠️  VirusTotal API key not configured")
        return {
            "error": "VirusTotal API key not configured",
            "virustotal_positives": 0,
            "api_available": False,
            "scan_status": "api_key_missing"
        }
    
    try:
        # VirusTotal API v3 requires the URL to be base64-encoded
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        
        headers = {
            "x-apikey": API_KEY,
            "User-Agent": "FraudDetectionSystem/1.0"
        }
        
        full_url = f"{VT_API_URL}/{url_id}"
        print(f"🌐 Querying VirusTotal: {full_url[:50]}...")
        
        # Make request with timeout
        response = requests.get(full_url, headers=headers, timeout=15)
        
        print(f"📊 VirusTotal Response Status: {response.status_code}")
        
        if response.status_code == 404:
            # URL not found in VirusTotal database
            print("ℹ️  URL not found in VirusTotal database")
            return {
                "virustotal_positives": 0,
                "virustotal_total": 0,
                "api_available": True,
                "scan_status": "not_found",
                "message": "URL not found in VirusTotal database"
            }
        
        if response.status_code == 429:
            # Rate limit hit
            print("⚠️  VirusTotal API rate limit exceeded")
            return {
                "error": "VirusTotal API rate limit exceeded",
                "virustotal_positives": 0,
                "api_available": True,
                "rate_limited": True,
                "scan_status": "rate_limited"
            }
        
        response.raise_for_status()
        
        # Parse the JSON response
        vt_result = response.json()
        print(f"✅ VirusTotal data received")
        
        # Extract the analysis stats
        data = vt_result.get("data", {})
        attributes = data.get("attributes", {})
        stats = attributes.get("last_analysis_stats", {})
        
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        clean = stats.get("clean", 0)
        undetected = stats.get("undetected", 0)
        total_engines = malicious + suspicious + clean + undetected
        
        positives = malicious + suspicious
        
        print(f"🔍 VirusTotal Results: {positives}/{total_engines} engines flagged as malicious")
        
        return {
            "virustotal_positives": positives,
            "virustotal_total": total_engines,
            "malicious": malicious,
            "suspicious": suspicious,
            "clean": clean,
            "undetected": undetected,
            "api_available": True,
            "scan_status": "found",
            "scan_date": attributes.get("last_analysis_date", ""),
            "reputation_score": min(positives / max(total_engines, 1) * 2, 1.0) if total_engines > 0 else 0.0
        }
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"VirusTotal API HTTP error: {e.response.status_code}"
        print(f"❌ {error_msg}")
        return {
            "error": error_msg,
            "virustotal_positives": 0,
            "api_available": True,
            "scan_status": "http_error"
        }
    
    except requests.exceptions.Timeout:
        error_msg = "VirusTotal API timeout"
        print(f"❌ {error_msg}")
        return {
            "error": error_msg,
            "virustotal_positives": 0,
            "api_available": True,
            "timeout": True,
            "scan_status": "timeout"
        }
    
    except requests.exceptions.RequestException as e:
        error_msg = f"VirusTotal API request failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "error": error_msg,
            "virustotal_positives": 0,
            "api_available": False,
            "scan_status": "request_failed"
        }
    
    except Exception as e:
        error_msg = f"Unexpected error during VirusTotal check: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "error": error_msg,
            "virustotal_positives": 0,
            "api_available": False,
            "scan_status": "unexpected_error"
        }

def get_features(url: str) -> dict:
    """
    Queries reputation sources (local lists, Google Safe Browsing, VirusTotal) 
    and returns reputation features with enhanced debugging.
    """
    if not url or not isinstance(url, str):
        return {
            "error": "Invalid URL provided",
            "virustotal_positives": 0,
            "is_on_blacklist": False,
            "is_gsb_threat": False,
            "domain": "",
            "scan_status": "invalid_url"
        }
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        if not domain:
            return { "error": "Could not extract domain from URL", "scan_status": "no_domain" }
        
        print(f"🔍 Reputation Analysis for: {domain}")
        
        result = {
            "domain": domain,
            "is_on_blacklist": False,
            "is_on_whitelist": False,
            "is_gsb_threat": False,
            "gsb_threat_type": None,
            "virustotal_positives": 0,
            "reputation_score": 0.0,
            "scan_status": "analyzing"
        }
        
        # 1. Quick whitelist check
        if check_domain_whitelist(domain):
            print(f"✅ Domain {domain} is in trusted whitelist")
            result.update({"is_on_whitelist": True, "scan_status": "whitelisted"})
            return result
        
        # 2. Quick local blacklist check
        if check_domain_blacklist(domain):
            print(f"❌ Domain {domain} is in known malicious list")
            result.update({
                "is_on_blacklist": True,
                "reputation_score": 1.0,
                "scan_status": "blacklisted"
            })
            return result

        # 3. Query Google Safe Browsing API (High-priority check)
        print(f"🔬 Querying Google Safe Browsing for {url}...")
        gsb_result = query_google_safe_browsing(url)
        if gsb_result.get("is_known_threat"):
            print(f"❌ Google Safe Browsing Alert: {gsb_result.get('threat_type')}")
            result.update({
                "is_on_blacklist": True,
                "is_gsb_threat": True,
                "gsb_threat_type": gsb_result.get('threat_type'),
                "reputation_score": 1.0, # GSB match is high confidence
                "scan_status": "gsb_blacklisted"
            })
            return result # Return immediately if GSB finds a threat

        # 4. Query VirusTotal if other checks are clean
        print(f"🌐 Querying VirusTotal for {url}...")
        vt_result = query_virustotal(url)
        result.update(vt_result)
        
        # Set blacklist status and score based on VirusTotal results
        positives = result.get("virustotal_positives", 0)
        if positives > 0:
            result["is_on_blacklist"] = True
            total = result.get("virustotal_total", 1)
            if total > 0:
                ratio = positives / total
                result["reputation_score"] = min(ratio * 2, 1.0)
            else:
                result["reputation_score"] = min(positives * 0.1, 1.0)
        
        # Finalize status
        if result["reputation_score"] == 0.0 and result.get("scan_status") == "analyzing":
            result["scan_status"] = "clean"

        result["analysis_timestamp"] = time.time()
        
        print("📊 Reputation Analysis Complete:")
        print(f"   - Google Safe Browsing: {'Threat Found' if result['is_gsb_threat'] else 'Clean'}")
        print(f"   - VirusTotal: {result.get('virustotal_positives', 0)} positives")
        print(f"   - Final Reputation Score: {result['reputation_score']:.2f}")
        
        return result
        
    except Exception as e:
        error_msg = f"Reputation analysis failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "error": error_msg,
            "virustotal_positives": 0,
            "is_on_blacklist": False,
            "domain": urlparse(url).netloc if url else "",
            "reputation_score": 0.0,
            "scan_status": "analysis_failed"
        }

def add_to_blacklist(domain):
    """Add a domain to the local blacklist (for manual additions)"""
    try:
        KNOWN_MALICIOUS_DOMAINS.add(domain.lower().replace('www.', ''))
        return True
    except:
        return False

def add_to_whitelist(domain):
    """Add a domain to the local whitelist (for manual additions)"""
    try:
        KNOWN_SAFE_DOMAINS.add(domain.lower().replace('www.', ''))
        return True
    except:
        return False

def get_reputation_stats():
    """Get statistics about the reputation system"""
    return {
        "api_key_configured": bool(API_KEY),
        "whitelist_size": len(KNOWN_SAFE_DOMAINS),
        "blacklist_size": len(KNOWN_MALICIOUS_DOMAINS),
        "virustotal_api_available": bool(API_KEY)
    }

# Test function
if __name__ == "__main__":
    test_urls = [
        "https://www.google.com",
        "https://starbucks.com", 
        "http://suspicious-paypal-login.tk/verify",
        "https://malicious-site.tk"
    ]
    
    print("🔍 Testing Reputation Analyzer")
    print("=" * 50)
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        result = get_features(url)
        
        print(f"📊 Results:")
        for key, value in result.items():
            if not key.startswith('_'):
                print(f"   - {key}: {value}")
        print("-" * 30)