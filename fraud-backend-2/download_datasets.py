# download_datasets.py
"""
Dataset Downloader for URL Fraud Detection
Downloads and prepares popular phishing/malicious URL datasets
"""

import os
import requests
import zipfile
import gzip
import shutil
import pandas as pd
from typing import List, Dict
import hashlib

class DatasetDownloader:
    """Download and prepare phishing URL datasets"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.raw_dir = os.path.join(data_dir, "raw")
        self.processed_dir = os.path.join(data_dir, "processed")
        
        # Create directories
        for directory in [self.data_dir, self.raw_dir, self.processed_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Dataset sources
        self.datasets = {
            'phishtank': {
                'name': 'PhishTank Database',
                'url': 'http://data.phishtank.com/data/online-valid.csv.gz',
                'description': 'Verified phishing URLs from PhishTank',
                'format': 'csv.gz',
                'license': 'Free for research'
            },
            'openphish': {
                'name': 'OpenPhish Feed',
                'url': 'https://openphish.com/feed.txt',
                'description': 'Active phishing URLs',
                'format': 'txt',
                'license': 'Free community feed'
            },
            'urlhaus': {
                'name': 'URLhaus Malware URLs',
                'url': 'https://urlhaus.abuse.ch/downloads/csv_recent/',
                'description': 'Recent malware URLs from abuse.ch',
                'format': 'csv',
                'license': 'CC0'
            },
            'uci_phishing': {
                'name': 'UCI Phishing Websites',
                'manual_download': True,
                'url': 'https://archive.ics.uci.edu/ml/datasets/phishing+websites',
                'description': 'UCI ML Repository phishing dataset with features',
                'format': 'arff',
                'license': 'UCI ML Repository'
            }
        }
        
        # Legitimate domains list (for creating balanced datasets)
        self.legitimate_domains = [
            'google.com', 'youtube.com', 'facebook.com', 'amazon.com', 'wikipedia.org',
            'twitter.com', 'instagram.com', 'linkedin.com', 'reddit.com', 'netflix.com',
            'microsoft.com', 'apple.com', 'github.com', 'stackoverflow.com', 'medium.com',
            'spotify.com', 'adobe.com', 'wordpress.org', 'mozilla.org', 'apache.org',
            'ebay.com', 'paypal.com', 'dropbox.com', 'slack.com', 'zoom.us',
            'salesforce.com', 'oracle.com', 'ibm.com', 'intel.com', 'cisco.com',
            'hp.com', 'dell.com', 'lenovo.com', 'samsung.com', 'sony.com',
            'nike.com', 'adidas.com', 'walmart.com', 'target.com', 'bestbuy.com',
            'homedepot.com', 'lowes.com', 'costco.com', 'walgreens.com', 'cvs.com',
            'bankofamerica.com', 'wellsfargo.com', 'chase.com', 'capitalone.com', 'usbank.com',
            'mit.edu', 'stanford.edu', 'harvard.edu', 'yale.edu', 'princeton.edu',
            'cnn.com', 'bbc.com', 'nytimes.com', 'washingtonpost.com', 'reuters.com',
            'espn.com', 'nba.com', 'nfl.com', 'mlb.com', 'nhl.com',
            'airbnb.com', 'uber.com', 'lyft.com', 'doordash.com', 'grubhub.com',
            'booking.com', 'expedia.com', 'tripadvisor.com', 'hotels.com', 'kayak.com',
            'craigslist.org', 'etsy.com', 'pinterest.com', 'quora.com', 'twitch.tv'
        ]