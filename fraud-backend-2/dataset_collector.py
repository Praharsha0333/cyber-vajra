import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import logging
from urllib.parse import urlparse
import time
import concurrent.futures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def collect_indian_websites():
    """Collect and analyze Indian websites for training data"""
    # Legitimate sources
    legitimate_sources = [
        'https://www.india.gov.in/website-directory',
        'https://www.rbi.org.in/Scripts/BS_ViewMasterDirection.aspx?Id=11507',
        'https://www.meity.gov.in/content/national-portal-india'
    ]
    
    # Known phishing sources (from PhishTank API)
    phishtank_api = "http://data.phishtank.com/data/online-valid.json"
    
    legitimate_data = []
    phishing_data = []
    
    # Collect legitimate websites
    for source in legitimate_sources:
        try:
            response = requests.get(source)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')
            
            for link in links:
                href = link.get('href', '')
                if href.endswith('.in') or '.gov.in' in href or '.nic.in' in href:
                    legitimate_data.append({
                        'url': href,
                        'type': 'legitimate',
                        'source': source,
                        'collected_at': datetime.now().isoformat()
                    })
        except Exception as e:
            print(f"Error collecting legitimate data from {source}: {str(e)}")
            
    # Collect phishing data
    try:
        response = requests.get(phishtank_api)
        phish_data = response.json()
        
        for entry in phish_data:
            if '.in' in entry['url'] or 'india' in entry['url'].lower():
                phishing_data.append({
                    'url': entry['url'],
                    'type': 'phishing',
                    'source': 'phishtank',
                    'verified': entry['verified'],
                    'collected_at': datetime.now().isoformat()
                })
    except Exception as e:
        print(f"Error collecting phishing data: {str(e)}")
        
    # Save collected data
    dataset = legitimate_data + phishing_data
    df = pd.DataFrame(dataset)
    
    # Save to CSV
    df.to_csv('datasets/indian_websites.csv', index=False)
    
    # Save to JSON for easy loading
    with open('datasets/indian_websites.json', 'w') as f:
        json.dump(dataset, f, indent=2)
        
    print(f"Collected {len(legitimate_data)} legitimate and {len(phishing_data)} phishing URLs")
    
if __name__ == "__main__":
    collect_indian_websites()