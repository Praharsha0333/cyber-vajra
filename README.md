# CyberVajra – AI-Powered Security Analyzer
CyberVajra is a proactive Indian-made cybersecurity app designed to detect and classify malicious websites and mobile applications. It combines a modern Flutter frontend with a sophisticated Python backend to provide real-time, user-friendly security analysis.

This repository contains the complete source code for the CyberVajra project.

# The Problem We Solve
The primary problem that this application addresses is the reactive nature of existing fraud detection systems. Current methods predominantly rely on post-incident analysis, where fraudulent websites and malicious applications are only identified and flagged after they have caused harm to users, such as financial loss or data theft. This reactive approach is inherently inefficient and fails to prevent the initial damage.

Our solution, the CyberVajra application, provides a fundamental shift to a proactive security model. The system acts as a preventative layer by intelligently analyzing URLs and APK files before a user interacts with them. By leveraging a multi-layered AI approach, it can detect, classify, and flag potential threats in real-time, effectively mitigating risk and empowering users to make informed decisions.

In essence, this application solves the critical issue of digital vulnerability by transforming the security paradigm from damage control to preventative protection, thereby safeguarding the integrity of digital transactions and user data.

# Who Is This App For?
CyberVajra is designed for any individual or organization that wants to navigate the digital world more safely. Our target audience includes:

Everyday Internet Users: Anyone who shops online, uses social media, or receives links via email and messaging apps.

Parents and Guardians: To help protect children from accessing unsafe websites or downloading malicious apps.

Less Tech-Savvy Individuals: An easy-to-use tool for those who may not be able to spot the technical signs of a scam themselves.

Small Businesses: To protect employees from phishing attacks that could compromise company data.

# Core Features
Our system uses a multi-layered approach, combining static analysis, live threat intelligence, and machine learning to provide a robust verdict on both URLs and APKs.

<details>
<summary><strong> Web Analyzer Features</strong></summary>

Domain Analyzer: Extracts and analyzes domain information using WHOIS lookups, SSL certificate validation, and domain age checks.

Content Analyzer: Performs lexical feature extraction on the website's content and uses ML models to detect phishing language patterns.

Visual Analyzer: Compares screenshots of suspicious websites against known legitimate sites to detect visual similarities indicative of phishing.

Reputation Check: Correlates the domain and IP against leading threat intelligence databases, including VirusTotal and Google Safe Browsing.

ML-based AI Prediction: An ensemble model provides a final verdict on the likelihood of the URL being a phishing site, with detailed risk indicators.

</details>

<details>
<summary><strong> APK Analyzer Features</strong></summary>

APK Metadata Extractor: Parses the app's manifest to extract its package name, version, and developer's digital signature.

Permission Analyzer: Flags dangerous permissions using a weighted scoring system to identify potential Spyware, Trojans, or Toll Fraud.

String/Code Scan: Scans the app's internal code for embedded phishing keywords (e.g., "password", "bank").

Reputation Check: Looks up the APK's unique file hash against the VirusTotal API to check for flags from over 70 antivirus engines.

ML-based AI Prediction: Deploys a LightGBM model trained on a real-world malware dataset to provide an independent verdict on the app's safety.

</details>

Tech Stack
Frontend: Flutter (Dart), Material Design, Provider/Riverpod

Backend: Python, Flask

Machine Learning: scikit-learn, LightGBM, Pandas

Analysis Libraries: Androguard, Requests, python-whois, Selenium

 Integrated Setup Guide: From Zero to Running
This guide will walk you through setting up the entire application, from the backend server to the frontend mobile app. Follow these steps in order.

# Prerequisites

Before you begin, make sure you have the following installed on your system:

Git

Python 3.8+

Flutter SDK

Homebrew (for macOS users, to install required libraries)

Step 1: Get the Code

First, clone the entire project repository to your local machine.

git clone <your-repository-url>
cd <repository-folder-name>

Step 2: Set Up and Run the Backend Server

The backend is the "brain" of the app. It needs to be running before the frontend can work.

Navigate to the Backend Folder:

cd backend/

Create Your Python Sandbox (Virtual Environment):
This keeps the project's libraries separate and clean.

python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
On Windows, use: venv\Scripts\activate

Your terminal prompt will now start with (venv).

Install All Required Libraries:

pip install -r requirements.txt

macOS Note: If you see an error about libomp.dylib during this step, run brew install libomp and try again.

Download the AI Training Data:
The APK analyzer's AI needs to learn from real-world data.

Download: Get the category ZIP files from the University of New Brunswick's dataset page.

Unzip: Unzip each category (Adware, Benign, etc.) into the backend/dataset/ folder.

Train the AI Model (One-time step):
This step creates the apk_classifier.pkl file that the analyzer uses.

python train_model.py

Set Your API Keys:
For full functionality, you need a free API key from VirusTotal.

export VIRUSTOTAL_API_KEY="YourApiKeyHere"

Note: You must run this export command every time you open a new terminal session to run the server.

Run the Backend Server!

python api_server.py

The server will start. Look for a line that says Running on http://192.168.X.X:8000. Note this IP address and keep this terminal window open!

Step 3: Set Up and Connect the Frontend App

Now we will get the Flutter app running and connect it to your live backend.

Open a New Terminal Window:
Do not close your running server. Open a second, separate terminal.

Navigate to the Frontend Folder:

cd frontend/

Install Flutter Packages:

flutter pub get

Connect the App to Your Backend:
This is the crucial integration step. Open the file lib/services/api_service.dart (or your equivalent) in your code editor. Find the baseUrl variable and replace the placeholder IP with the one from your running backend server.

// lib/services/api_service.dart
static const baseUrl = "[http://192.168.](http://192.168.)X.X:8000"; // <-- Use YOUR backend's IP here

Run the Flutter App!
Connect your phone or start an emulator and run:

flutter run

The app will now be able to communicate with your local backend server. You are all set!

 Contributing
Fork the repo

Create your feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

 License
This project is licensed under the MIT License.

# 🇮🇳 Made in India
 CyberVajra is 100% Indian-made, developed to strengthen digital security without relying on foreign cyber tools.

