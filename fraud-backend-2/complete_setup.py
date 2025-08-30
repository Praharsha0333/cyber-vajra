#!/usr/bin/env python3
"""
Complete Setup Script for Enhanced URL Fraud Detection System
Installs dependencies, sets up directories, and provides testing capabilities
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("=" * 70)
    print("🛡️  ENHANCED URL FRAUD DETECTION SYSTEM SETUP")
    print("=" * 70)
    print("Multi-Modal Analysis with Brand Impersonation Detection")
    print("Components: Domain + Content + Reputation + Visual Analysis")
    print("=" * 70)

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements():
    """Install required Python packages"""
    print("\n📦 Installing Required Packages...")
    print("-" * 40)
    
    # Core requirements
    requirements = [
        'flask>=2.3.0',
        'flask-cors>=4.0.0',
        'requests>=2.28.0',
        'beautifulsoup4>=4.11.0',
        'python-whois>=0.7.0',
        'selenium>=4.0.0',
        'opencv-python>=4.5.0',
        'pillow>=9.0.0',
        'imagehash>=4.2.0',
        'scikit-learn>=1.1.0',
        'numpy>=1.21.0',
        'pandas>=1.3.0',
        'joblib>=1.1.0',
        'chromedriver-autoinstaller>=0.6.0'
    ]
    
    failed_packages = []
    
    for package in requirements:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n⚠️  Failed to install: {', '.join(failed_packages)}")
        print("   Try installing manually: pip install <package_name>")
        return False
    
    print("✅ All packages installed successfully!")
    return True

def setup_chromedriver():
    """Setup ChromeDriver for Selenium"""
    print("\n🌐 Setting up ChromeDriver for Visual Analysis...")
    print("-" * 45)
    
    try:
        import chromedriver_autoinstaller
        chromedriver_autoinstaller.install()
        print("✅ ChromeDriver installed successfully")
        
        # Test Chrome installation
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.quit()
            print("✅ Chrome WebDriver test successful")
            return True
        except Exception as e:
            print(f"❌ Chrome WebDriver test failed: {e}")
            print("   Make sure Google Chrome is installed")
            return False
            
    except Exception as e:
        print(f"❌ ChromeDriver setup failed: {e}")
        print("   Manual installation required:")
        print("   1. Download ChromeDriver from https://chromedriver.chromium.org/")
        print("   2. Add to your system PATH")
        return False

def create_directory_structure():
    """Create necessary directories"""
    print("\n📁 Creating Directory Structure...")
    print("-" * 35)
    
    directories = [
        'analyzers',
        'services', 
        'routes',
        'models',
        'data',
        'data/raw',
        'data/processed',
        'data/phishing',
        'data/legitimate',
        'visual_data',
        'visual_data/screenshots',
        'visual_data/phishing_templates',
        'visual_data/cache',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}/")
    
    # Create __init__.py files for Python packages
    init_files = ['analyzers/__init__.py', 'services/__init__.py', 'routes/__init__.py']
    for init_file in init_files:
        Path(init_file).touch(exist_ok=True)
        print(f"✅ Created: {init_file}")
    
    return True

def create_sample_config():
    """Create sample configuration files"""
    print("\n⚙️  Creating Configuration Files...")
    print("-" * 35)
    
    # Sample environment configuration
    env_content = """# Environment Configuration for URL Fraud Detection System
# Copy this to .env and update with your actual values

# VirusTotal API Key (optional but recommended)
# Get your free API key from: https://www.virustotal.com/gui/join-us
VIRUSTOTAL_API_KEY=your_virustotal_api_key_here

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Analysis Settings
SCREENSHOT_TIMEOUT=30
CACHE_DURATION_HOURS=24
MAX_BULK_URLS=50

# Trusted Domains (comma-separated)
TRUSTED_DOMAINS=google.com,microsoft.com,apple.com,github.com
"""
    
    with open('.env.sample', 'w') as f:
        f.write(env_content)
    print("✅ Created: .env.sample")
    
    # Sample brand colors configuration
    brand_colors = {
        "paypal": {
            "primary": [[0, 112, 191], [9, 45, 66]],
            "secondary": [[255, 205, 37]],
            "tolerance": 30
        },
        "amazon": {
            "primary": [[255, 153, 0], [35, 47, 62]],
            "secondary": [[146, 208, 80]],
            "tolerance": 25
        },
        "microsoft": {
            "primary": [[0, 120, 215], [16, 124, 16]],
            "secondary": [[255, 185, 0], [229, 20, 0]],
            "tolerance": 20
        }
    }
    
    os.makedirs('visual_data', exist_ok=True)
    with open('visual_data/brand_colors.json', 'w') as f:
        json.dump(brand_colors, f, indent=2)
    print("✅ Created: visual_data/brand_colors.json")
    
    return True

def create_requirements_file():
    """Create requirements.txt file"""
    requirements_content = """# Enhanced URL Fraud Detection System Requirements

# Core Flask components
flask>=2.3.0
flask-cors>=4.0.0
werkzeug>=2.3.0

# HTTP and Web scraping
requests>=2.28.0
beautifulsoup4>=4.11.0
urllib3>=1.26.0

# Domain analysis
python-whois>=0.7.0

# Visual analysis
selenium>=4.0.0
opencv-python>=4.5.0
pillow>=9.0.0
imagehash>=4.2.0

# Machine learning
scikit-learn>=1.1.0
numpy>=1.21.0
pandas>=1.3.0
joblib>=1.1.0

# Browser automation
chromedriver-autoinstaller>=0.6.0

# Development and testing
pytest>=7.0.0
pytest-flask>=1.2.0

# Optional: Environment management
python-dotenv>=0.19.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements_content)
    print("✅ Created: requirements.txt")

def run_system_test():
    """Run basic system functionality test"""
    print("\n🧪 Running System Tests...")
    print("-" * 25)
    
    try:
        # Test imports
        print("Testing imports...")
        
        test_imports = [
            ('flask', 'Flask web framework'),
            ('selenium', 'Web browser automation'),
            ('cv2', 'OpenCV computer vision'),
            ('PIL', 'Python Imaging Library'),
            ('sklearn', 'Machine learning library'),
            ('requests', 'HTTP library'),
            ('whois', 'WHOIS lookup library')
        ]
        
        for module, description in test_imports:
            try:
                __import__(module)
                print(f"✅ {module} - {description}")
            except ImportError as e:
                print(f"❌ {module} - {description} - {e}")
                return False
        
        # Test ChromeDriver
        print("\nTesting ChromeDriver...")
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
        
        if 'Google' in title:
            print(f"✅ ChromeDriver test successful (loaded: {title})")
        else:
            print(f"⚠️  ChromeDriver test unclear (loaded: {title})")
        
        print("\n✅ All system tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def create_demo_script():
    """Create demo script for testing"""
    demo_content = """#!/usr/bin/env python3
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
        
        print(f"Testing {len(demo_urls)} sample URLs...\\n")
        
        for i, (url, description) in enumerate(demo_urls, 1):
            print(f"[{i}/{len(demo_urls)}] {description}")
            print(f"URL: {url}")
            print("-" * 60)
            
            try:
                result = checker.check_url_risk(url)
                format_detailed_console_output(result)
            except Exception as e:
                print(f"❌ Error analyzing {url}: {e}\\n")
        
        print("✅ Demo completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you've run the setup script first")
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    run_demo()
"""
    
    with open('demo.py', 'w') as f:
        f.write(demo_content)
    os.chmod('demo.py', 0o755)  # Make executable
    print("✅ Created: demo.py")

def create_start_script():
    """Create server start script"""
    start_content = """#!/usr/bin/env python3
'''
Start script for Enhanced URL Fraud Detection System
'''

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        from app import main
        main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you've run setup.py first")
    except KeyboardInterrupt:
        print("\\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
"""
    
    with open('start_server.py', 'w') as f:
        f.write(start_content)
    os.chmod('start_server.py', 0o755)  # Make executable
    print("✅ Created: start_server.py")

def display_next_steps():
    """Display next steps for the user"""
    print("\n🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("Next Steps:")
    print("\n1. 🔑 Configure API Keys (Optional but Recommended):")
    print("   - Copy .env.sample to .env")
    print("   - Add your VirusTotal API key for reputation analysis")
    print("   - Get free API key: https://www.virustotal.com/gui/join-us")
    
    print("\n2. 🧪 Test the System:")
    print("   python demo.py")
    
    print("\n3. 🚀 Start the Server:")
    print("   python start_server.py")
    print("   Or: python app.py")
    
    print("\n4. 🌐 Access the API:")
    print("   Documentation: http://localhost:5001")
    print("   Test endpoint: POST http://localhost:5001/api/analyze_url")
    
    print("\n5. 📊 Example API Usage:")
    print("""   curl -X POST http://localhost:5001/api/analyze_url \\
        -H "Content-Type: application/json" \\
        -d '{"url": "https://example.com"}'""")
    
    print("\n📋 Key Features Available:")
    print("   ✅ Domain Analysis (WHOIS + SSL)")
    print("   ✅ Content Analysis (Pattern Matching)")
    print("   ✅ Reputation Analysis (VirusTotal)")
    print("   ✅ Visual Analysis (Screenshots + Brand Detection)")
    print("   ✅ Individual Analyzer Scoring")
    print("   ✅ Fraud Type Classification")
    print("   ✅ Bulk URL Analysis")
    
    print("\n🛠️  Troubleshooting:")
    print("   - If ChromeDriver fails: Install Google Chrome browser")
    print("   - If imports fail: pip install -r requirements.txt")
    print("   - For permission errors: Run with appropriate privileges")
    
    print("\n📚 Documentation:")
    print("   View full API docs at: http://localhost:5001 (after starting server)")

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        print("\n⚠️  Some packages failed to install. Continue anyway? (y/n): ", end="")
        if input().lower() != 'y':
            return False
    
    # Setup ChromeDriver
    setup_chromedriver()
    
    # Create directory structure
    create_directory_structure()
    
    # Create configuration files
    create_sample_config()
    create_requirements_file()
    
    # Create demo and start scripts
    create_demo_script()
    create_start_script()
    
    # Run system tests
    print("\n🧪 Would you like to run system tests? (y/n): ", end="")
    if input().lower() == 'y':
        run_system_test()
    
    # Display next steps
    display_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print(f"\n✅ Setup completed successfully!")
        else:
            print(f"\n❌ Setup completed with errors")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n🛑 Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)