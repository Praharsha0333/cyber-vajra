#!/usr/bin/env python3
"""
Complete Setup and Training Script for URL Fraud Detection System
This script handles the entire setup process including dependencies, datasets, and training
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

class SetupManager:
    """Manages the complete setup and training process"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.requirements_file = "requirements.txt"
        self.python_cmd = sys.executable
        
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("🐍 Checking Python version...")
        version = sys.version_info
        
        if version.major == 3 and version.minor >= 7:
            print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} detected")
            return True
        else:
            print(f"  ✗ Python 3.7+ required, found {version.major}.{version.minor}.{version.micro}")
            return False
    
    def create_requirements_file(self):
        """Create requirements.txt with all dependencies"""
        print("\n📝 Creating requirements.txt...")
        
        requirements = """# Core dependencies
flask==2.3.3
flask-cors==4.0.0
requests==2.31.0
pandas==2.0.3
numpy==1.24.3

# Machine Learning
scikit-learn==1.3.0
joblib==1.3.2

# URL Analysis
python-whois==0.8.0
tldextract==3.4.4
beautifulsoup4==4.12.2

# Visual Analysis (optional but recommended)
selenium==4.11.2
opencv-python==4.8.0.76
pillow==10.0.0
imagehash==4.3.1
chromedriver-autoinstaller==0.6.2

# Data Processing
openpyxl==3.1.2  # For Excel files
xlrd==2.0.1      # For older Excel files

# Optional for better performance
python-Levenshtein==0.21.1  # For string similarity
validators==0.20.0          # For URL validation

# Development tools (optional)
pytest==7.4.0
black==23.7.0
pylint==2.17.5
"""
        
        with open(self.requirements_file, 'w') as f:
            f.write(requirements)
        
        print(f"  ✓ Created {self.requirements_file}")
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print("\n📦 Installing dependencies...")
        
        try:
            # Upgrade pip first
            print("  Upgrading pip...")
            subprocess.check_call([self.python_cmd, "-m", "pip", "install", "--upgrade", "pip"])
            
            # Install requirements
            print("  Installing packages from requirements.txt...")
            subprocess.check_call([self.python_cmd, "-m", "pip", "install", "-r", self.requirements_file])
            
            print("  ✓ All dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Installation failed: {e}")
            print("\n  Try installing manually:")
            print(f"    {self.python_cmd} -m pip install -r requirements.txt")
            return False
    
    def create_directory_structure(self):
        """Create necessary directory structure"""
        print("\n📁 Creating directory structure...")
        
        directories = [
            "models",
            "data",
            "data/raw",
            "data/processed",
            "training_logs",
            "visual_data",
            "visual_data/screenshots",
            "visual_data/cache",
            "visual_data/phishing_templates",
            "analyzers",
            "services",
            "routes",
            "uploaded_apks"
        ]
        
        for directory in directories:
            path = self.project_root / directory
            path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ {directory}/")
    
    def check_chrome_driver(self):
        """Check and install ChromeDriver for Selenium"""
        print("\n🌐 Checking ChromeDriver...")
        
        try:
            import chromedriver_autoinstaller
            chromedriver_autoinstaller.install()
            print("  ✓ ChromeDriver installed/updated")
            return True
        except Exception as e:
            print(f"  ⚠️ ChromeDriver setup failed: {e}")
            print("  Visual analysis will not be available")
            return False
    
    def download_datasets(self):
        """Download training datasets"""
        print("\n📊 Downloading datasets...")
        
        # Check if download script exists
        if not os.path.exists("download_datasets.py"):
            print("  ⚠️ download_datasets.py not found")
            print("  Please ensure all scripts are in the project directory")
            return False
        
        try:
            # Run the download script
            result = subprocess.run(
                [self.python_cmd, "download_datasets.py", "--all"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                print("  ✓ Datasets downloaded successfully")
                return True
            else:
                print(f"  ⚠️ Dataset download completed with warnings")
                return True
                
        except subprocess.TimeoutExpired:
            print("  ⚠️ Dataset download timed out")
            print("  You can manually run: python download_datasets.py --all")
            return False
        except Exception as e:
            print(f"  ✗ Dataset download failed: {e}")
            return False
    
    def train_models(self):
        """Train the ML models"""
        print("\n🤖 Training models...")
        
        # Check for training script
        if not os.path.exists("train_models.py"):
            print("  ⚠️ train_models.py not found")
            return False
        
        # Find available datasets
        processed_dir = self.project_root / "data" / "processed"
        
        if not processed_dir.exists():
            print("  ⚠️ No processed datasets found")
            print("  Creating sample datasets for training...")
            
            # Use sample datasets
            result = subprocess.run(
                [self.python_cmd, "train_models.py", "--sample"],
                capture_output=True,
                text=True
            )
        else:
            # Find CSV files in processed directory
            csv_files = list(processed_dir.glob("*.csv"))
            
            if not csv_files:
                print("  ⚠️ No CSV files found in data/processed/")
                print("  Using sample datasets...")
                result = subprocess.run(
                    [self.python_cmd, "train_models.py", "--sample"],
                    capture_output=True,
                    text=True
                )
            else:
                print(f"  Found {len(csv_files)} datasets")
                # Use balanced dataset if available, otherwise use all
                balanced_file = processed_dir / "balanced_dataset.csv"
                
                if balanced_file.exists():
                    print("  Using balanced dataset for training...")
                    dataset_files = [str(balanced_file)]
                else:
                    dataset_files = [str(f) for f in csv_files[:3]]  # Use up to 3 datasets
                
                result = subprocess.run(
                    [self.python_cmd, "train_models.py"] + dataset_files,
                    capture_output=True,
                    text=True
                )
        
        # Check result
        if result.returncode == 0:
            print("  ✓ Models trained successfully")
            
            # Check if models were created
            models_dir = self.project_root / "models"
            model_files = list(models_dir.glob("*.joblib"))
            
            if model_files:
                print(f"  ✓ Created {len(model_files)} model files:")
                for model_file in model_files:
                    size = model_file.stat().st_size / 1024  # KB
                    print(f"    - {model_file.name} ({size:.1f} KB)")
            
            return True
        else:
            print("  ✗ Model training failed")
            print("\nError output:")
            print(result.stderr)
            return False
    
    def test_system(self):
        """Test the complete system"""
        print("\n🧪 Testing the system...")
        
        try:
            # Test imports
            print("  Testing imports...")
            from services.enhanced_url_checker import EnhancedURLChecker
            
            # Initialize checker
            print("  Initializing URL checker...")
            checker = EnhancedURLChecker()
            
            # Test with sample URLs
            test_urls = [
                "https://www.google.com",
                "http://suspicious-paypal.tk",
                "https://microsoft-update.ml/verify"
            ]
            
            print("  Testing URL analysis...")
            for url in test_urls:
                result = checker.check_url_risk(url)
                status = result.get('overall_status', 'error')
                risk = int(result.get('risk_score', 0) * 100)
                print(f"    {url}: {status} ({risk}%)")
            
            print("  ✓ System test passed")
            return True
            
        except Exception as e:
            print(f"  ✗ System test failed: {e}")
            return False
    
    def create_run_script(self):
        """Create a simple run script"""
        print("\n📝 Creating run script...")
        
        if platform.system() == "Windows":
            script_name = "run.bat"
            script_content = f"""@echo off
echo Starting URL Fraud Detection System...
{self.python_cmd} app.py
pause
"""
        else:
            script_name = "run.sh"
            script_content = f"""#!/bin/bash
echo "Starting URL Fraud Detection System..."
{self.python_cmd} app.py
"""
        
        with open(script_name, 'w') as f:
            f.write(script_content)
        
        if platform.system() != "Windows":
            os.chmod(script_name, 0o755)
        
        print(f"  ✓ Created {script_name}")
    
    def run_setup(self):
        """Run the complete setup process"""
        print("\n" + "=" * 60)
        print("🚀 URL FRAUD DETECTION SYSTEM - COMPLETE SETUP")
        print("=" * 60)
        
        steps = [
            ("Python Version Check", self.check_python_version),
            ("Create Requirements File", self.create_requirements_file),
            ("Install Dependencies", self.install_dependencies),
            ("Create Directory Structure", self.create_directory_structure),
            ("Setup ChromeDriver", self.check_chrome_driver),
            ("Download Datasets", self.download_datasets),
            ("Train Models", self.train_models),
            ("Test System", self.test_system),
            ("Create Run Script", self.create_run_script)
        ]
        
        results = {}
        
        for step_name, step_func in steps:
            print(f"\n{'='*60}")
            print(f"Step: {step_name}")
            print("="*60)
            
            try:
                result = step_func()
                results[step_name] = result
                
                if not result and step_name in ["Python Version Check", "Install Dependencies"]:
                    print(f"\n❌ Critical step '{step_name}' failed. Stopping setup.")
                    break
                    
            except Exception as e:
                print(f"\n❌ Error in {step_name}: {e}")
                results[step_name] = False
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 SETUP SUMMARY")
        print("=" * 60)
        
        for step_name, result in results.items():
            status = "✓" if result else "✗"
            print(f"  {status} {step_name}")
        
        success_count = sum(1 for r in results.values() if r)
        total_count = len(results)
        
        if success_count == total_count:
            print("\n✅ SETUP COMPLETED SUCCESSFULLY!")
            print("\n📖 How to use the system:")
            print("  1. Start the Flask server:")
            print(f"     {self.python_cmd} app.py")
            print("     or use: ./run.sh (Linux/Mac) or run.bat (Windows)")
            print("\n  2. Access the API:")
            print("     http://localhost:5001")
            print("\n  3. Test with curl:")
            print('     curl -X POST http://localhost:5001/api/analyze_url \\')
            print('       -H "Content-Type: application/json" \\')
            print('       -d \'{"url": "http://suspicious-site.com"}\'')
            print("\n  4. Train with new datasets:")
            print("     python train_models.py dataset1.csv dataset2.csv")
            
        elif success_count >= total_count * 0.7:
            print(f"\n⚠️ Setup partially completed ({success_count}/{total_count} steps)")
            print("The system should work but some features may be limited.")
        else:
            print(f"\n❌ Setup failed ({success_count}/{total_count} steps completed)")
            print("Please check the errors above and try again.")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup and Train URL Fraud Detection System")
    parser.add_argument('--skip-download', action='store_true', 
                       help='Skip dataset download')
    parser.add_argument('--skip-training', action='store_true',
                       help='Skip model training')
    parser.add_argument('--minimal', action='store_true',
                       help='Minimal setup (no datasets/training)')
    
    args = parser.parse_args()
    
    manager = SetupManager()
    
    if args.minimal:
        print("Running minimal setup (no datasets or training)...")
        manager.check_python_version()
        manager.create_requirements_file()
        manager.install_dependencies()
        manager.create_directory_structure()
        manager.create_run_script()
    else:
        # Modify setup based on arguments
        if args.skip_download:
            manager.download_datasets = lambda: True
        if args.skip_training:
            manager.train_models = lambda: True