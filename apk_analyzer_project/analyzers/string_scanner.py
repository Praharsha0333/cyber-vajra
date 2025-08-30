# analyzers/string_scanner.py
import re

from androguard.core.bytecodes.apk import APK

# Regex to find URLs in strings
URL_REGEX = r'(https?://[^\s/$.?#].[^\s]*)'

# Keywords often found in phishing or malicious content
SUSPICIOUS_KEYWORDS = [
    'password', 'credit card', 'account', 'login', 'verify', 'update', 'security', 'bank'
]

def scan_strings(filepath):
    """
    Performs a basic string scan on the APK's DEX files to find URLs and keywords.
    """
    urls_found = []
    keywords_found = {}

    try:
        apk = APK(filepath)
        
        for dex in apk.get_dex():
            for string in dex.get_strings():
                # Find URLs
                urls = re.findall(URL_REGEX, string)
                if urls:
                    urls_found.extend(urls)
                
                # Find Keywords
                for keyword in SUSPICIOUS_KEYWORDS:
                    if keyword in string.lower():
                        keywords_found[keyword] = keywords_found.get(keyword, 0) + 1
                        
    except Exception as e:
        return {'error': f"Error during string scan: {e}"}

    return {
        'urls_found': list(set(urls_found)), # Return unique URLs
        'suspicious_keywords': keywords_found
    }
