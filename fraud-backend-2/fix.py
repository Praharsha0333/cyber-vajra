#!/usr/bin/env python3
"""
Quick Fix Script - Install All Dependencies for Best Visual Analysis
Installs OpenCV and all required packages for advanced visual analysis
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a single package with proper error handling"""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '--upgrade', package
        ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode() if e.stderr else "Unknown error"
        print(f"❌ Failed to install {package}: {error_output}")
        return False

def main():
    """Main installation function for best visual analysis"""
    print("🎯 Installing COMPLETE Visual Analysis System")
    print("=" * 55)
    print("This includes OpenCV for advanced brand impersonation detection")
    print("=" * 55)
    
    # All packages needed for the best visual analyzer
    packages = [
        # Core Flask and web
        'flask>=2.3.0',
        'flask-cors>=4.0.0',
        'werkzeug>=2.3.0',
        'requests>=2.28.0',
        'beautifulsoup4>=4.11.0',
        
        # Domain analysis
        'python-whois>=0.7.0',
        
        # Visual analysis (the good stuff!)
        'selenium>=4.15.0',
        'opencv-python>=4.8.0',  # Advanced computer vision
        'pillow>=10.0.0',
        'imagehash>=4.3.1',      # The missing package!
        
        # Machine learning for color clustering
        'scikit-learn>=1.3.0',
        'numpy>=1.24.0',
        'pandas>=2.0.0',
        'joblib>=1.3.0',
        
        # Browser automation
        'chromedriver-autoinstaller>=0.6.0',
        
        # Additional utilities
        'python-dotenv>=1.0.0'
    ]
    
    print("📦 Installing packages for ADVANCED visual analysis...")
    print("   (This may take a few minutes - OpenCV is large)")
    print()
    
    failed_packages = []
    
    for i, package in enumerate(packages, 1):
        print(f"[{i}/{len(packages)}] {package.split('>=')[0]}")
        if not install_package(package):
            failed_packages.append(package)
    
    # Test critical imports
    print("\n🧪 Testing Advanced Visual Analysis Components...")
    critical_tests = [
        ('cv2', 'OpenCV for computer vision'),
        ('imagehash', 'ImageHash for perceptual hashing'),
        ('sklearn.cluster', 'Scikit-learn for color clustering'),
        ('selenium', 'Selenium for web automation'),
        ('PIL', 'Pillow for image processing'),
        ('numpy', 'NumPy for numerical operations')
    ]
    
    all_working = True
    for module, description in critical_tests:
        try:
            __import__(module)
            print(f"✅ {description}")
        except ImportError as e:
            print(f"❌ {description}: {e}")
            all_working = False
    
    # Test ChromeDriver setup
    print("\n🌐 Testing ChromeDriver Setup...")
    try:
        import chromedriver_autoinstaller
        chromedriver_autoinstaller.install()
        
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://www.google.com')
        title = driver.title
        driver.quit()
        
        print(f"✅ ChromeDriver working (tested with: {title})")
        
    except Exception as e:
        print(f"❌ ChromeDriver setup failed: {e}")
        print("   Install Google Chrome browser if not already installed")
        all_working = False
    
    # Results summary
    print("\n" + "="*60)
    print("📋 INSTALLATION RESULTS:")
    
    if failed_packages:
        print(f"❌ Failed packages: {len(failed_packages)}")
        for pkg in failed_packages:
            print(f"   • {pkg}")
        print("\n💡 Try manual installation:")
        for pkg in failed_packages:
            print(f"   pip install {pkg}")
    else:
        print("✅ All packages installed successfully!")
    
    if all_working:
        print("✅ All visual analysis components working!")
        print("\n🎯 ADVANCED FEATURES NOW AVAILABLE:")
        print("   ✅ Screenshot capture with Selenium")
        print("   ✅ Brand color detection with OpenCV")
        print("   ✅ Perceptual hashing for template matching")  
        print("   ✅ Advanced color clustering analysis")
        print("   ✅ Brand impersonation detection")
        print("   ✅ Visual similarity scoring")
        
        print("\n🚀 Ready to run:")
        print("   python demo.py   # Test with advanced visual analysis")
        print("   python app.py    # Start server with full features")
        
        return True
    else:
        print("❌ Some components not working properly")
        print("   Basic functionality may still work")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 SUCCESS! Advanced visual analysis system ready!")
    else:
        print("\n⚠️  Setup completed with some issues - check errors above")