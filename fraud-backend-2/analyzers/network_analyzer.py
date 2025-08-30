# analyzers/network_analyzer.py

import requests
import dns.resolver
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def get_network_features(url: str) -> dict:
    """
    Fetches the webpage and analyzes its content, links, headers, and DNS records.
    """
    features = {
        "is_reachable": False,
        "final_url": url,
        "has_csp_header": False,
        "has_hsts_header": False,
        "has_xfo_header": False,
        "outgoing_link_ratio": -1.0,
        "dns_has_mx_record": False,
        "dns_has_spf_record": False,
        "network_error": None
    }

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()

        features["is_reachable"] = True
        features["final_url"] = response.url

        # 1. HTTP Header Analysis
        features["has_csp_header"] = "content-security-policy" in response.headers
        features["has_hsts_header"] = "strict-transport-security" in response.headers
        features["has_xfo_header"] = "x-frame-options" in response.headers

        # 2. Outgoing Link Analysis
        soup = BeautifulSoup(response.content, 'html.parser')
        domain = urlparse(features["final_url"]).netloc
        
        internal_links = 0
        external_links = 0
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href', '')
            if href.startswith(('http', '//')):
                link_domain = urlparse(href).netloc
                if domain in link_domain:
                    internal_links += 1
                else:
                    external_links += 1
        
        total_links = internal_links + external_links
        if total_links > 0:
            features["outgoing_link_ratio"] = external_links / total_links

        # 3. DNS Record Analysis
        try:
            domain_to_check = urlparse(features["final_url"]).netloc
            mx_records = dns.resolver.resolve(domain_to_check, 'MX')
            features["dns_has_mx_record"] = len(mx_records) > 0
            txt_records = dns.resolver.resolve(domain_to_check, 'TXT')
            features["dns_has_spf_record"] = any("v=spf1" in str(r) for r in txt_records)
        except Exception:
            # If DNS lookup fails, features remain False, which is fine
            pass

    except requests.RequestException as e:
        features["network_error"] = f"Request failed: {str(e)}"
    
    return features