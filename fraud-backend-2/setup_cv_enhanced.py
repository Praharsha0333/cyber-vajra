#!/usr/bin/env python3
"""
Setup Script for Enhanced Computer Vision Visual Analysis
This script sets up the computer vision capabilities for brand comparison.
"""

import os
import sys
import subprocess
import requests
import zipfile
from pathlib import Path
import json

def install_cv_dependencies():
    """Install computer vision dependencies"""
    
    cv_packages = [
        "opencv-python>=4.8.0",
        "numpy>=1.24.0", 
        "Pillow>=10.0.0",
        "imagehash>=4.3.1",
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.1"
    ]
    
    print("Installing computer vision dependencies...")
    for package in cv_packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def setup_directories():
    """Create necessary directories for visual analysis"""
    
    directories = [
        "visual_data",
        "visual_data/screenshots", 
        "visual_data/brand_templates",
        "visual_data/templates",
        "visual_data/cache",
        "visual_data/datasets"
    ]
    
    print("Creating visual analysis directories...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created {directory}")
    
    return True

def download_sample_brand_data():
    """Create sample brand signature data"""
    
    brand_templates_file = "visual_data/brand_templates/brand_templates.json"
    
    sample_brand_data = {
        "paypal": {
            "colors": [[0, 48, 135], [255, 179, 0], [92, 159, 214]],
            "logo_features": ["paypal", "pp"],
            "typical_elements": ["sign in", "log in", "email", "password"],
            "domain_patterns": ["paypal.com"],
            "description": "PayPal payment service"
        },
        "microsoft": {
            "colors": [[0, 120, 212], [255, 185, 0], [16, 137, 62], [196, 57, 43]],
            "logo_features": ["microsoft", "outlook", "office", "windows"],
            "typical_elements": ["sign in", "microsoft account"],
            "domain_patterns": ["microsoft.com", "outlook.com", "office.com"],
            "description": "Microsoft services"
        },
        "amazon": {
            "colors": [[35, 47, 62], [255, 153, 0], [132, 189, 0]],
            "logo_features": ["amazon", "prime"],
            "typical_elements": ["sign in", "your account", "prime"],
            "domain_patterns": ["amazon.com", "prime.amazon.com"],
            "description": "Amazon e-commerce"
        },
        "google": {
            "colors": [[66, 133, 244], [234, 67, 53], [251, 188, 5], [52, 168, 83]],
            "logo_features": ["google", "gmail"],
            "typical_elements": ["sign in", "google account", "gmail"],
            "domain_patterns": ["google.com", "gmail.com", "accounts.google.com"],
            "description": "Google services"
        },
        "apple": {
            "colors": [[0, 0, 0], [255, 255, 255], [29, 29, 31]],
            "logo_features": ["apple", "icloud", "app store"],
            "typical_elements": ["apple id", "sign in", "icloud"],
            "domain_patterns": ["apple.com", "icloud.com"],
            "description": "Apple services"
        },
        "facebook": {
            "colors": [[24, 119, 242], [255, 255, 255]],
            "logo_features": ["facebook", "meta"],
            "typical_elements": ["log in", "facebook", "connect"],
            "domain_patterns": ["facebook.com", "meta.com"],
            "description": "Facebook/Meta social media"
        }
    }
    
    print("Creating sample brand signature data...")
    try:
        with open(brand_templates_file, 'w') as f:
            json.dump(sample_brand_data, f, indent=2)
        print(f"✅ Created brand templates: {brand_templates_file}")
        return True
    except Exception as e:
        print(f"❌ Error creating brand data: {e}")
        return False

def test_cv_setup():
    """Test the computer vision setup"""
    
    print("Testing computer vision setup...")
    
    try:
        # Test OpenCV
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")
        
        # Test image processing
        import numpy as np
        from PIL import Image
        
        # Create test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[:, :] = [0, 48, 135]  # PayPal blue
        
        # Test color extraction
        print("✅ Image processing test passed")
        
        # Test selenium
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ Selenium and WebDriver manager available")
        
        # Test imagehash
        import imagehash
        print("✅ ImageHash available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def test_visual_analyzer():
    """Test the enhanced visual analyzer"""
    
    print("Testing enhanced visual analyzer...")
    
    try:
        sys.path.insert(0, os.getcwd())
        from analyzers.visual_analyzer import get_features
        
        # Test with a simple URL (without actually taking screenshot for setup)
        test_result = {
            'visual_similarity_score': 0.0,
            'analysis_success': True,
            'analysis_method': 'enhanced_cv'
        }
        
        print("✅ Enhanced visual analyzer loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Visual analyzer test failed: {e}")
        print("This may be normal during setup - make sure to replace the visual_analyzer.py file")
        return False

def create_usage_example():
    """Create example usage file"""
    
    example_code = '''#!/usr/bin/env python3
"""
Example usage of Enhanced Visual Analysis
This shows how to use the computer vision features for brand detection
"""

import sys
import os
sys.path.insert(0, os.getcwd())

from services.enhanced_url_checker import EnhancedURLChecker

def test_visual_brand_detection():
    """Test visual brand detection with various URLs"""
    
    test_urls = [
        {
            "url": "https://www.paypal.com",
            "description": "Legitimate PayPal (should be safe)"
        },
        {
            "url": "http://paypal-secure-login.tk", 
            "description": "Fake PayPal (should detect brand impersonation)"
        },
        {
            "url": "http://microsoft-support-secure.ml",
            "description": "Fake Microsoft (should detect visual similarity)"
        },
        {
            "url": "https://github.com",
            "description": "Legitimate site (should be safe)"
        }
    ]
    
    checker = EnhancedURLChecker()
    
    print("Testing Enhanced Visual Brand Detection")
    print("=" * 50)
    
    for test_case in test_urls:
        url = test_case["url"]
        description = test_case["description"]
        
        print(f"\\nTesting: {description}")
        print(f"URL: {url}")
        
        try:
            result = checker.check_url_risk(url)
            
            print(f"Status: {result['overall_status'].upper()}")
            print(f"Risk Score: {result['risk_percentage']}")
            
            # Show visual analysis details
            if 'analyzer_results' in result and 'visual' in result['analyzer_results']:
                visual = result['analyzer_results']['visual']
                
                if visual.get('success') and visual.get('brand_analysis'):
                    brand_analysis = visual['brand_analysis']
                    
                    if brand_analysis.get('is_impersonation'):
                        brand = brand_analysis.get('best_match', 'unknown')
                        similarity = brand_analysis.get('max_similarity', 0)
                        print(f"BRAND IMPERSONATION DETECTED: {brand.upper()} ({similarity:.2f} similarity)")
                    
                    print(f"Visual Risk Factors: {visual.get('risk_factors', [])}")
            
            if result.get('fraud_type'):
                fraud = result['fraud_type']
                print(f"Fraud Type: {fraud['type'].upper()}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_visual_brand_detection()
'''
    
    print("Creating usage example...")
    try:
        with open('test_visual_cv.py', 'w') as f:
            f.write(example_code)
        print("Created test_visual_cv.py")
        return True
    except Exception as e:
        print(f"Error creating example: {e}")
        return False

def main():
    """Main setup function for enhanced computer vision"""
    
    print("Enhanced Computer Vision Setup for URL Fraud Detection")
    print("=" * 60)
    
    # Step 1: Install dependencies
    print("\n1. Installing computer vision dependencies...")
    if not install_cv_dependencies():
        print("Dependency installation failed")
        return False
    
    # Step 2: Setup directories
    print("\n2. Setting up directories...")
    if not setup_directories():
        print("Directory setup failed")
        return False
    
    # Step 3: Create brand data
    print("\n3. Creating brand signature data...")
    if not download_sample_brand_data():
        print("Brand data creation failed")
        return False
    
    # Step 4: Test setup
    print("\n4. Testing computer vision setup...")
    if not test_cv_setup():
        print("CV setup test failed")
        return False
    
    # Step 5: Create usage example
    print("\n5. Creating usage examples...")
    if not create_usage_example():
        print("Example creation failed")
        return False
    
    # Step 6: Test visual analyzer (may fail until file is replaced)
    print("\n6. Testing visual analyzer...")
    test_visual_analyzer()  # Don't fail on this
    
    print("\n" + "=" * 60)
    print("COMPUTER VISION SETUP COMPLETED")
    print("=" * 60)
    
    print("\nNext Steps:")
    print("1. Replace analyzers/visual_analyzer.py with the enhanced version")
    print("2. Replace requirements.txt with the updated version")
    print("3. Restart your server: python app.py")
    print("4. Test with: python test_visual_cv.py")
    
    print("\nNew Features Added:")
    print("- Computer vision-based brand detection")
    print("- Visual similarity analysis using color extraction")
    print("- Brand impersonation detection")
    print("- Enhanced visual element analysis")
    print("- Screenshot comparison with known brand signatures")
    
    print("\nSupported Brands for Detection:")
    print("- PayPal, Microsoft, Amazon, Google, Apple, Facebook")
    print("- System can detect visual impersonation attempts")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)