# app.py - Complete Flask Application for Multi-Modal URL Fraud Detection - FIXED
"""
Complete Flask Application with Enhanced Multi-Modal URL Fraud Detection
Features:
- Domain Analysis (WHOIS + SSL)
- Content Analysis (Pattern matching + ML)
- Reputation Analysis (VirusTotal)
- Visual Analysis (Screenshots + Brand impersonation detection)
- Individual scorer display
- Fraud type classification
- Bulk analysis capabilities
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import sys
import logging
from datetime import datetime

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our enhanced components
try:
    from services.enhanced_url_checker import EnhancedURLChecker
    from routes.url_routes import url_bp
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required files are in the correct directories")
    sys.exit(1)

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app, origins=["*"])
    
    # Configuration
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['JSON_SORT_KEYS'] = False
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Register blueprints
    app.register_blueprint(url_bp, url_prefix='/api')
    
    # Root endpoint with API documentation
    @app.route('/')
    def index():
        """API documentation and status page"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Enhanced URL Fraud Detection API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; margin-bottom: 40px; }
                .title { color: #2c3e50; margin-bottom: 10px; }
                .subtitle { color: #7f8c8d; }
                .section { margin: 30px 0; }
                .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }
                .method { background: #3498db; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px; }
                .method.post { background: #e74c3c; }
                .method.get { background: #27ae60; }
                .example { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 14px; overflow-x: auto; }
                .feature { background: #fff; border: 1px solid #ddd; padding: 15px; margin: 10px; border-radius: 5px; }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
                .status.online { background: #d5f4e6; color: #27ae60; }
                .status.offline { background: #fad5d5; color: #e74c3c; }
                .analyzer-weights { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }
                .weight-card { text-align: center; padding: 15px; background: #3498db; color: white; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 class="title">🛡️ Enhanced URL Fraud Detection API</h1>
                    <p class="subtitle">Multi-Modal Analysis with Brand Impersonation Detection</p>
                    <div class="status online">✅ System Online - {{ timestamp }}</div>
                </div>

                <div class="section">
                    <h2>🔍 Analysis Components</h2>
                    <div class="analyzer-weights">
                        <div class="weight-card">
                            <h3>Reputation</h3>
                            <p><strong>35%</strong></p>
                            <small>VirusTotal API</small>
                        </div>
                        <div class="weight-card">
                            <h3>Domain</h3>
                            <p><strong>25%</strong></p>
                            <small>WHOIS + SSL</small>
                        </div>
                        <div class="weight-card">
                            <h3>Content</h3>
                            <p><strong>20%</strong></p>
                            <small>Pattern Analysis</small>
                        </div>
                        <div class="weight-card">
                            <h3>Visual</h3>
                            <p><strong>20%</strong></p>
                            <small>Brand Detection</small>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>📡 API Endpoints</h2>
                    
                    <div class="endpoint">
                        <span class="method post">POST</span> <strong>/api/analyze_url</strong>
                        <p>Analyze a single URL for fraud indicators with security report format</p>
                        <div class="example">
POST /api/analyze_url
Content-Type: application/json

{
    "url": "https://example.com"
}

Response Format:
{
  "url": "https://example.com",
  "overall_status": "legitimate|suspicious|risky",
  "risk_score": 15,
  "reason": "Explanation of the risk assessment",
  "details": {
    "content_analysis": {...},
    "domain_analysis": {...},
    "reputation_analysis": {...},
    "visual_analysis": {...}
  },
  "user_tip": "Contextual advice for the user"
}
                        </div>
                    </div>

                    <div class="endpoint">
                        <span class="method post">POST</span> <strong>/api/bulk_analyze</strong>
                        <p>Analyze multiple URLs (max 50 per request)</p>
                        <div class="example">
POST /api/bulk_analyze
Content-Type: application/json

{
    "urls": ["https://site1.com", "https://site2.com"]
}
                        </div>
                    </div>

                    <div class="endpoint">
                        <span class="method get">GET</span> <strong>/api/analyzer_status</strong>
                        <p>Check system status and analyzer availability</p>
                    </div>

                    <div class="endpoint">
                        <span class="method get">GET</span> <strong>/api/demo</strong>
                        <p>Run demo analysis on sample URLs</p>
                    </div>

                    <div class="endpoint">
                        <span class="method get">GET</span> <strong>/api/health</strong>
                        <p>Health check endpoint</p>
                    </div>
                </div>

                <div class="section">
                    <h2>🎯 Security Report Format</h2>
                    <p>All analysis endpoints now return a standardized security report with:</p>
                    <div class="example">
{
  "url": "analyzed URL",
  "overall_status": "legitimate|suspicious|risky",
  "risk_score": "integer 0-100",
  "reason": "human-readable explanation",
  "details": {
    "content_analysis": {
      "content_risk_prediction": "0 or 1",
      "content_risk_score": "0.0-1.0",
      "suspicious_keywords_found": ["array of keywords"]
    },
    "domain_analysis": {
      "domain": "extracted domain",
      "domain_age_days": "integer or -1",
      "domain_length": "integer",
      "has_ssl": "0 or 1",
      "domain_risk": "0 or 1"
    },
    "reputation_analysis": {
      "is_on_blacklist": "true/false",
      "virustotal_positives": "integer",
      "reported_by_users": "integer"
    },
    "visual_analysis": {
      "screenshot_path": "path or 'not_available'",
      "visual_similarity_score": "0.0-1.0",
      "brand_impersonation_detected": "true/false"
    }
  },
  "user_tip": "contextual advice based on risk level"
}
                    </div>
                </div>

                <div class="section">
                    <h2>🚀 Key Features</h2>
                    <div class="grid">
                        <div class="feature">
                            <h3>🌍 Domain Analysis</h3>
                            <p>WHOIS lookup, domain age verification, SSL certificate validation</p>
                        </div>
                        <div class="feature">
                            <h3>📝 Content Analysis</h3>
                            <p>URL pattern matching, suspicious keyword detection, ML classification</p>
                        </div>
                        <div class="feature">
                            <h3>🛡️ Reputation Check</h3>
                            <p>VirusTotal API integration for threat intelligence</p>
                        </div>
                        <div class="feature">
                            <h3>👁️ Visual Analysis</h3>
                            <p>Screenshot capture, brand impersonation detection using color analysis</p>
                        </div>
                        <div class="feature">
                            <h3>🎯 Security Reports</h3>
                            <p>Standardized JSON format with detailed breakdowns and user guidance</p>
                        </div>
                        <div class="feature">
                            <h3>🔍 Fraud Classification</h3>
                            <p>Automatic classification: Phishing, Scam, Malware, or Clone site</p>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>⚙️ Setup Instructions</h2>
                    <div class="example">
# 1. Install dependencies
pip install flask flask-cors selenium opencv-python scikit-learn
pip install pillow imagehash requests beautifulsoup4 python-whois

# 2. Setup environment variables (optional)
export VIRUSTOTAL_API_KEY="your_api_key_here"

# 3. Install ChromeDriver
pip install chromedriver-autoinstaller

# 4. Run the application
python app.py
                    </div>
                </div>

                <div class="section">
                    <h2>📊 Risk Categories</h2>
                    <div class="grid">
                        <div class="feature" style="border-left-color: #27ae60;">
                            <h3>✅ Legitimate (0-25)</h3>
                            <p>Safe to visit, no fraud indicators detected</p>
                        </div>
                        <div class="feature" style="border-left-color: #f39c12;">
                            <h3>⚠️ Suspicious (25-60)</h3>
                            <p>Some risk indicators present, proceed with caution</p>
                        </div>
                        <div class="feature" style="border-left-color: #e74c3c;">
                            <h3>❌ Risky (60-100)</h3>
                            <p>High fraud probability, avoid visiting</p>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return render_template_string(html_template, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"))
    
    # Global error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error', 'message': str(error)}), 500
    
    return app

def main():
    """Main function to run the Flask application"""
    print("🚀 Starting Enhanced URL Fraud Detection System")
    print("=" * 60)
    
    # Check dependencies
    try:
        import cv2
        print("✅ OpenCV available for visual analysis")
    except ImportError:
        print("⚠️  OpenCV not available - install with: pip install opencv-python")
    
    try:
        import selenium
        print("✅ Selenium available for screenshots")
    except ImportError:
        print("⚠️  Selenium not available - install with: pip install selenium")
    
    try:
        from sklearn.cluster import KMeans
        print("✅ Scikit-learn available for color analysis")
    except ImportError:
        print("⚠️  Scikit-learn not available - install with: pip install scikit-learn")
    
    # Create directories
    directories = ['models', 'visual_data', 'visual_data/screenshots', 'visual_data/cache']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Directory ready: {directory}")
    
    # Create Flask app
    app = create_app()
    
    # Display startup information
    print("\n🌐 API Documentation available at: http://localhost:5001")
    print("🔍 Test endpoint: POST http://localhost:5001/api/analyze_url")
    print("📊 System status: GET http://localhost:5001/api/analyzer_status")
    print("💡 Demo analysis: GET http://localhost:5001/api/demo")
    
    print(f"\n📋 Available endpoints:")
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
        print(f"  {methods:8} {rule.rule}")
    
    print(f"\n🎯 Scoring Weights:")
    print(f"  Reputation: 35% (VirusTotal threat intelligence)")
    print(f"  Domain:     25% (WHOIS + SSL analysis)")
    print(f"  Content:    20% (URL pattern matching)")
    print(f"  Visual:     20% (Brand impersonation detection)")
    
    print(f"\n📄 Response Format: Security Report JSON")
    print(f"  - Standardized structure across all endpoints")
    print(f"  - Risk score as integer (0-100)")
    print(f"  - Contextual user tips")
    print(f"  - Detailed analysis breakdowns")
    
    print(f"\n⚡ Starting server...")
    
    try:
        app.run(
            host="0.0.0.0", 
            port=5001, 
            debug=False,  # Set to False for production
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    main()