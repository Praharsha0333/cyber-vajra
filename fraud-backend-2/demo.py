#!/usr/bin/env python3
'''
Demo script for Enhanced URL Fraud Detection System
Tests the system with sample URLs
'''

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_demo():
    print("🔍 Enhanced URL Fraud Detection - Demo")
    print("=" * 50)
    
    try:
        from services.enhanced_url_checker import EnhancedURLChecker, format_detailed_console_output
        
        # Initialize checker
        checker = EnhancedURLChecker()
        
        # Demo URLs
        demo_urls = [
            ("https://www.google.com", "Trusted legitimate site"),
            ("https://github.com", "Popular legitimate site"), 
            ("http://paypal-verify-account.tk", "Fake PayPal phishing"),
            ("https://amazon-security.ml", "Fake Amazon phishing"),
            ("http://bit.ly/suspicious-link", "Suspicious short URL")
        ]
        
        print(f"Testing {len(demo_urls)} sample URLs...\n")
        
        for i, (url, description) in enumerate(demo_urls, 1):
            print(f"[{i}/{len(demo_urls)}] {description}")
            print(f"URL: {url}")
            print("-" * 60)
            
            try:
                result = checker.check_url_risk(url)
                format_detailed_console_output(result)
            except Exception as e:
                print(f"❌ Error analyzing {url}: {e}\n")
        
        print("✅ Demo completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you've run the setup script first")
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    run_demo()
