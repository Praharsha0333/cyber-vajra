# routes/url_routes.py - FIXED VERSION
from flask import Blueprint, request, jsonify
from services.enhanced_url_checker import EnhancedURLChecker, format_detailed_console_output
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 Initializing Enhanced URL Fraud Detection System...")
try:
    checker = EnhancedURLChecker()
    print("✅ System ready!")
except Exception as e:
    print(f"❌ Failed to initialize checker: {e}")
    checker = None

url_bp = Blueprint("url_routes", __name__)

@url_bp.route("/analyze_url", methods=["POST"])
def analyze_url_endpoint():
    """
    Enhanced URL analysis endpoint with proper error handling.
    """
    try:
        # Check if checker is initialized
        if not checker:
            return jsonify({
                "error": "System not initialized",
                "details": "The fraud detection system is not properly initialized."
            }), 503
        
        # Get and validate input
        data = request.get_json()
        if not data or "url" not in data:
            return jsonify({"error": "URL is required"}), 400
        
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL cannot be empty"}), 400
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Perform analysis
        logger.info(f"Analyzing URL: {url}")
        final_report = checker.check_url_risk(url)
        
        # Log summary for debugging
        print(f"✅ Analysis complete for {url}")
        print(f"   Status: {final_report.get('overall_status')}")
        print(f"   Risk Score: {final_report.get('risk_score')}%")
        print(f"   Time: {final_report.get('analysis_time')}s")
        
        return jsonify(final_report)
        
    except Exception as e:
        logger.error(f"Error in /analyze_url endpoint: {e}", exc_info=True)
        return jsonify({
            "error": "An internal server error occurred",
            "details": str(e)
        }), 500

@url_bp.route("/bulk_analyze", methods=["POST"])
def bulk_analyze_endpoint():
    """
    Analyze multiple URLs at once.
    """
    try:
        if not checker:
            return jsonify({
                "error": "System not initialized",
                "details": "The fraud detection system is not properly initialized."
            }), 503
        
        data = request.get_json()
        if not data or "urls" not in data:
            return jsonify({"error": "URLs list is required"}), 400
        
        urls = data.get("urls", [])
        if not isinstance(urls, list):
            return jsonify({"error": "URLs must be a list"}), 400
        
        if len(urls) > 50:
            return jsonify({"error": "Maximum 50 URLs allowed per request"}), 400
        
        results = []
        for url in urls[:50]:  # Safety limit
            if url and isinstance(url, str):
                url = url.strip()
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                try:
                    result = checker.check_url_risk(url)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "url": url,
                        "overall_status": "error",
                        "risk_score": -1,
                        "reason": f"Analysis failed: {str(e)}",
                        "error": str(e)
                    })
        
        return jsonify({
            "success": True,
            "analyzed_count": len(results),
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error in /bulk_analyze endpoint: {e}", exc_info=True)
        return jsonify({
            "error": "An internal server error occurred",
            "details": str(e)
        }), 500

@url_bp.route("/analyzer_status", methods=["GET"])
def analyzer_status_endpoint():
    """
    Check the status of all analyzers.
    """
    try:
        status = {
            "system_online": checker is not None,
            "ml_model_loaded": checker.models_loaded if checker else False,
            "analyzers": {
                "domain": True,
                "content": True,
                "reputation": True,
                "network": True,
                "visual": True
            }
        }
        
        # Check for specific dependencies
        try:
            import cv2
            status["opencv_available"] = True
        except ImportError:
            status["opencv_available"] = False
        
        try:
            import selenium
            status["selenium_available"] = True
        except ImportError:
            status["selenium_available"] = False
        
        # Check for API keys
        import os
        status["virustotal_api_configured"] = bool(os.getenv('VIRUSTOTAL_API_KEY'))
        
        # Model details if loaded
        if checker and checker.models_loaded:
            status["model_features_count"] = len(checker.model_features) if checker.model_features else 0
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error in /analyzer_status endpoint: {e}")
        return jsonify({
            "error": "Failed to get status",
            "details": str(e)
        }), 500

@url_bp.route("/demo", methods=["GET"])
def demo_endpoint():
    """
    Run demo analysis on sample URLs.
    """
    try:
        if not checker:
            return jsonify({
                "error": "System not initialized",
                "details": "The fraud detection system is not properly initialized."
            }), 503
        
        demo_urls = [
            {"url": "https://www.google.com", "expected": "legitimate", "description": "Trusted search engine"},
            {"url": "http://suspicious-paypal-login.tk", "expected": "risky", "description": "Suspicious domain mimicking PayPal"},
            {"url": "https://github.com", "expected": "legitimate", "description": "Trusted code repository"}
        ]
        
        results = []
        for demo in demo_urls:
            try:
                analysis = checker.check_url_risk(demo["url"])
                results.append({
                    "url": demo["url"],
                    "description": demo["description"],
                    "expected_status": demo["expected"],
                    "actual_status": analysis.get("overall_status"),
                    "risk_score": analysis.get("risk_score"),
                    "match": analysis.get("overall_status") == demo["expected"]
                })
            except Exception as e:
                results.append({
                    "url": demo["url"],
                    "description": demo["description"],
                    "error": str(e)
                })
        
        # Calculate accuracy
        matches = sum(1 for r in results if r.get("match", False))
        total = len([r for r in results if "match" in r])
        accuracy = (matches / total * 100) if total > 0 else 0
        
        return jsonify({
            "demo_results": results,
            "accuracy": f"{accuracy:.1f}%",
            "summary": f"{matches}/{total} predictions matched expected results"
        })
        
    except Exception as e:
        logger.error(f"Error in /demo endpoint: {e}")
        return jsonify({
            "error": "Demo failed",
            "details": str(e)
        }), 500

@url_bp.route("/health", methods=["GET"])
def health_endpoint():
    """
    Simple health check endpoint.
    """
    return jsonify({
        "status": "healthy" if checker else "unhealthy",
        "timestamp": time.time(),
        "ml_model": "loaded" if (checker and checker.models_loaded) else "not_loaded"
    })