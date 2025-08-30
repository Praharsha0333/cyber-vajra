# setup_visual_analyzer.py

import os
import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Install required packages"""
    packages = [
        'selenium>=4.0.0',
        'Pillow>=8.0.0',
        'ImageHash>=4.2.0',
        'numpy>=1.20.0',
        'chromedriver-autoinstaller>=0.6.0'
    ]
    
    print("Installing required packages...")
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing {package}: {e}")
            return False
    
    return True

def setup_chromedriver():
    """Setup ChromeDriver automatically"""
    try:
        import chromedriver_autoinstaller
        print("Setting up ChromeDriver...")
        chromedriver_autoinstaller.install()
        print("✅ ChromeDriver setup completed")
        return True
    except Exception as e:
        print(f"❌ Error setting up ChromeDriver: {e}")
        print("Please install ChromeDriver manually:")
        print("1. Download from https://chromedriver.chromium.org/")
        print("2. Add to your PATH")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        'visual_data',
        'visual_data/screenshots',
        'visual_data/phishing_templates',
        'visual_data/cache'
    ]
    
    print("Creating directories...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def test_visual_analyzer():
    """Test the visual analyzer setup"""
    try:
        print("Testing Visual Analyzer...")
        from analyzers.visual_analyzer import get_features
        
        # Test with a safe URL
        test_url = "https://www.google.com"
        print(f"Testing with URL: {test_url}")
        
        result = get_features(test_url)
        
        if result.get('analysis_success', False):
            print("✅ Visual Analyzer test successful!")
            print(f"Screenshot path: {result.get('screenshot_path', 'None')}")
            print(f"pHash: {result.get('phash', 'None')}")
            print(f"Similarity score: {result.get('visual_similarity_score', 0)}")
            return True
        else:
            print("❌ Visual Analyzer test failed")
            print(f"Error: {result.get('error_message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Visual Analyzer: {e}")
        return False

def create_sample_integration():
    """Create a sample integration file"""
    integration_code = '''# sample_integration.py - Example of how to use the Visual Analyzer

from analyzers.visual_analyzer import get_features, cleanup
from enhanced_url_checker import EnhancedURLChecker

def test_visual_integration():
    """Test visual analyzer with URL checker"""
    
    # Test URLs
    test_urls = [
        "https://www.google.com",
        "https://www.coursera.org",
        "https://github.com"
    ]
    
    # Initialize URL checker
    checker = EnhancedURLChecker()
    
    for url in test_urls:
        print(f"\\n--- Analyzing: {url} ---")
        
        # Get visual features
        visual_result = get_features(url)
        print(f"Visual Analysis Success: {visual_result.get('analysis_success', False)}")
        print(f"Visual Similarity Score: {visual_result.get('visual_similarity_score', 0):.3f}")
        print(f"Screenshot Path: {visual_result.get('screenshot_path', 'None')}")
        
        if visual_result.get('matched_template'):
            print(f"⚠️  Matched Phishing Template: {visual_result['matched_template']['description']}")
        
        # Get full URL risk assessment (this will now include visual analysis)
        full_result = checker.check_url_risk(url)
        print(f"Overall Status: {full_result['overall_status']}")
        print(f"Risk Score: {full_result['risk_score']}")
    
    # Cleanup
    cleanup()
    print("\\n✅ Integration test completed!")

if __name__ == "__main__":
    test_visual_integration()
'''
    
    with open('sample_integration.py', 'w') as f:
        f.write(integration_code)
    
    print("✅ Created sample_integration.py")

def main():
    """Main setup function"""
    print("=== Visual Analyzer Setup ===\\n")
    
    # Check if analyzers directory exists
    if not os.path.exists('analyzers'):
        print("Creating analyzers directory...")
        os.makedirs('analyzers', exist_ok=True)
        
        # Create __init__.py if it doesn't exist
        init_file = 'analyzers/__init__.py'
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# Analyzers package\\n')
    
    # Step 1: Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements. Please install manually.")
        return False
    
    # Step 2: Setup ChromeDriver
    if not setup_chromedriver():
        print("⚠️  ChromeDriver setup failed. You may need to install it manually.")
    
    # Step 3: Create directories
    create_directories()
    
    # Step 4: Create sample integration
    create_sample_integration()
    
    # Step 5: Test (optional)
    test_choice = input("\\n🧪 Would you like to test the Visual Analyzer now? (y/n): ").lower().strip()
    if test_choice == 'y':
        success = test_visual_analyzer()
        if not success:
            print("\\n⚠️  Testing failed, but setup is complete. Check your ChromeDriver installation.")
    
    print("\\n🎉 Visual Analyzer setup completed!")
    print("\\n📋 Next steps:")
    print("1. Replace your current analyzers/visual_analyzer.py with the new implementation")
    print("2. Run: python sample_integration.py (to test integration)")
    print("3. The visual analyzer will now work with your existing URL checker!")
    
    print("\\n💡 Features added:")
    print("- Screenshot capture using Selenium")
    print("- pHash calculation for image similarity")
    print("- Template matching against known phishing sites")
    print("- Visual element analysis (forms, inputs, etc.)")
    print("- Caching for performance")
    print("- Automatic cleanup of old screenshots")
    
    return True

if __name__ == "__main__":
    main()