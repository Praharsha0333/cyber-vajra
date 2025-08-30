# services/enhanced_url_checker.py - Enhanced Console Output Version
"""
Enhanced URL Checker with comprehensive JSON console output
Including all analyzers and detailed reporting
"""

import time
import os
from urllib.parse import urlparse
from typing import Dict, List, Any
import json
import logging
import joblib
import pandas as pd
import numpy as np
import re

# Import analyzers
from analyzers import domain_analyzer, content_analyzer, visual_analyzer, reputation_analyzer, network_analyzer

class EnhancedURLChecker:
    """Multi-modal URL fraud detection system with ML-based scoring and detailed JSON output."""
    
    def __init__(self):
        self.TRUSTED_DOMAINS = {
            'google.com', 'microsoft.com', 'apple.com', 'amazon.com', 'github.com', 
            'wikipedia.org', 'stackoverflow.com', 'youtube.com', 'facebook.com', 
            'twitter.com', 'linkedin.com', 'paypal.com', 'ebay.com', 'netflix.com', 'instagram.com'
        }
        self.RISK_THRESHOLDS = {'legitimate': 25, 'suspicious': 60, 'risky': 100}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize model variables
        self.model = None
        self.model_features = None
        self.models_loaded = False
        
        # Load the model
        self.load_model()
    
    def load_model(self):
        """Loads the ensemble model and its feature list."""
        model_path = os.path.join('models', 'ensemble_model.joblib')
        features_path = os.path.join('models', 'model_features.joblib')
        
        try:
            if os.path.exists(model_path) and os.path.exists(features_path):
                self.model = joblib.load(model_path)
                self.model_features = joblib.load(features_path)
                self.models_loaded = True
                print(f"✅ ML model loaded successfully with {len(self.model_features)} features")
            else:
                if not os.path.exists(model_path):
                    print(f"⚠️ Model file not found at: {model_path}")
                if not os.path.exists(features_path):
                    print(f"⚠️ Features file not found at: {features_path}")
                print("⚠️ ML predictions will use rule-based fallback")
                self.models_loaded = False
        except Exception as e:
            print(f"❌ Error loading ML model: {e}")
            self.models_loaded = False
    
    def is_trusted_domain(self, url: str) -> bool:
        """Check if the URL belongs to a trusted domain"""
        try:
            domain = urlparse(url).netloc.lower().replace('www.', '')
            return any(domain == trusted or domain.endswith('.' + trusted) for trusted in self.TRUSTED_DOMAINS)
        except Exception:
            return False
    
    def extract_url_features(self, url: str) -> dict:
        """Extract features from URL matching the training features"""
        features = {}
        url = str(url)
        
        # Add protocol if missing
        url_for_parsing = url
        if not re.match(r'^https?://', url_for_parsing):
            url_for_parsing = 'http://' + url_for_parsing
        
        try:
            parsed_url = urlparse(url_for_parsing)
            hostname = parsed_url.hostname if parsed_url.hostname else ''
            
            path_component = ''
            if hostname:
                hostname_index = url.find(hostname)
                if hostname_index != -1:
                    path_start_index = hostname_index + len(hostname)
                    path_component = url[path_start_index:]
            
            # Basic URL features
            features['url_length'] = len(url)
            features['hostname_length'] = len(hostname)
            features['subdomain_count'] = hostname.count('.')
            features['has_ip_address'] = 1 if re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', hostname) else 0
            features['path_length'] = len(path_component)
            features['directory_count'] = path_component.count('/')
            features['count_hyphen'] = url.count('-')
            features['count_at'] = url.count('@')
            features['count_question'] = url.count('?')
            features['count_percent'] = url.count('%')
            features['count_dot'] = url.count('.')
            features['count_equal'] = url.count('=')
            features['count_http'] = url.lower().count('http')
            features['count_www'] = url.lower().count('www')
            
            # Suspicious keywords
            suspicious_keywords = ['login', 'secure', 'account', 'webscr', 'cmd', 'bin', 
                                 'verification', 'signin', 'paypal', 'banking']
            for keyword in suspicious_keywords:
                features[f'has_{keyword}'] = 1 if keyword in url.lower() else 0
        
        except Exception as e:
            self.logger.error(f"Error extracting URL features: {e}")
            return {key: 0 for key in self.model_features} if self.model_features else features
        
        return features
    
    def generate_ml_insights(self, risk_score: int, features_used: dict) -> dict:
        """Generate ML model insights and explanations"""
        insights = {
            "model_type": "Ensemble Random Forest" if self.models_loaded else "Rule-based Fallback",
            "confidence_level": "high" if self.models_loaded else "medium",
            "feature_count": len(self.model_features) if self.model_features else 0,
            "top_risk_indicators": [],
            "ml_recommendation": ""
        }
        
        # Determine top risk indicators
        risk_indicators = []
        if features_used.get('domain_age', 365) < 30:
            risk_indicators.append("Very new domain (high risk)")
        if not features_used.get('has_ssl', True):
            risk_indicators.append("No SSL certificate")
        if features_used.get('has_ip_address'):
            risk_indicators.append("Uses IP address instead of domain")
        if features_used.get('suspicious_keywords_count', 0) > 2:
            risk_indicators.append("Multiple suspicious keywords")
        
        insights["top_risk_indicators"] = risk_indicators[:3]
        
        # Generate ML recommendation
        if risk_score < 25:
            insights["ml_recommendation"] = "Low risk - likely safe to proceed with normal caution"
        elif risk_score < 60:
            insights["ml_recommendation"] = "Medium risk - verify the site's legitimacy before sharing sensitive data"
        else:
            insights["ml_recommendation"] = "High risk - strongly recommend avoiding this site"
        
        return insights
    
    def calculate_weighted_risk_score(self, url: str, domain_f: dict, content_f: dict, 
                                     reputation_f: dict, visual_f: dict, 
                                     network_f: dict, ml_prediction: float = None) -> tuple:
        """
        Calculate a weighted risk score that properly considers all factors
        Returns: (risk_score, reason)
        """
        risk_components = []
        positive_signals = []  # Track good security indicators
        risk_score = 0
        
        # Start with a base score and adjust based on findings
        
        # 1. REPUTATION CHECK - Most Critical (can override everything)
        if reputation_f.get('is_on_blacklist') or reputation_f.get('is_gsb_threat'):
            risk_score = 90  # Immediately high risk
            risk_components.append("Blacklisted/Google Safe Browsing threat")
            return risk_score, "Blacklisted or known threat detected"
        
        vt_positives = reputation_f.get('virustotal_positives', 0)
        if vt_positives > 10:
            risk_score += 60
            risk_components.append(f"VirusTotal: {vt_positives} detections")
        elif vt_positives > 5:
            risk_score += 40
            risk_components.append(f"VirusTotal: {vt_positives} detections")
        elif vt_positives > 0:
            risk_score += 20
            risk_components.append(f"VirusTotal: {vt_positives} detection(s)")
        else:
            positive_signals.append("Clean reputation (0 detections)")
        
        # 2. DOMAIN ANALYSIS - Age and SSL are key indicators
        domain_age = domain_f.get('domain_age', -1)
        
        # Domain age scoring (older = safer)
        if domain_age > 365 * 5:  # More than 5 years
            risk_score -= 15  # Reduce risk for very old domains
            positive_signals.append(f"Established domain ({domain_age//365} years)")
        elif domain_age > 365 * 2:  # More than 2 years
            risk_score -= 10
            positive_signals.append(f"Mature domain ({domain_age//365} years)")
        elif domain_age > 365:  # More than 1 year
            risk_score -= 5
            positive_signals.append("Domain over 1 year old")
        elif domain_age > 90:
            risk_score += 5
        elif domain_age > 30:
            risk_score += 15
            risk_components.append("Relatively new domain")
        elif domain_age > 0:
            risk_score += 30
            risk_components.append(f"Very new domain ({domain_age} days)")
        else:
            risk_score += 10  # Unknown age is slightly suspicious
        
        # SSL Certificate
        if domain_f.get('has_ssl'):
            positive_signals.append("Valid SSL certificate")
        else:
            risk_score += 25
            risk_components.append("No SSL certificate")
        
        # Suspicious domain patterns
        if domain_f.get('suspicious_tld'):
            risk_score += 15
            risk_components.append("Suspicious TLD")
        
        if domain_f.get('uses_ip'):
            risk_score += 20
            risk_components.append("Uses IP address")
        
        # 3. NETWORK ANALYSIS - Security headers are positive signals
        if network_f.get('is_reachable'):
            security_headers = network_f.get('has_security_headers', {})
            security_count = sum([
                security_headers.get('hsts', False),
                security_headers.get('csp', False),
                security_headers.get('x_frame_options', False)
            ])
            
            if security_count >= 3:
                risk_score -= 10  # All security headers present
                positive_signals.append("Strong security headers")
            elif security_count >= 2:
                risk_score -= 5
                positive_signals.append("Good security headers")
            elif security_count == 0:
                risk_score += 10
                risk_components.append("No security headers")
            
            # Check for suspicious redirects
            if network_f.get('suspicious_redirects'):
                risk_score += 15
                risk_components.append("URL redirects detected")
            
            # DNS records (legitimate sites usually have proper DNS)
            dns = network_f.get('dns_records', {})
            if dns.get('has_mx') and dns.get('has_spf'):
                risk_score -= 5
                positive_signals.append("Proper DNS configuration")
        else:
            risk_score += 20
            risk_components.append("Site unreachable")
        
        # 4. CONTENT ANALYSIS - Keywords and patterns
        content_risk = content_f.get('content_risk_score', 0)
        patterns = content_f.get('pattern_features', {})
        
        if content_risk > 0.7:
            risk_score += 20
            risk_components.append("High-risk content patterns")
        elif content_risk > 0.4:
            risk_score += 10
            risk_components.append("Suspicious content patterns")
        
        suspicious_keywords = patterns.get('suspicious_keywords_found', [])
        if len(suspicious_keywords) > 3:
            risk_score += 15
            risk_components.append(f"Multiple suspicious keywords: {', '.join(suspicious_keywords[:3])}")
        elif len(suspicious_keywords) > 0:
            risk_score += 5
            risk_components.append(f"Suspicious keyword(s): {', '.join(suspicious_keywords)}")
        
        # Brand impersonation in URL
        if patterns.get('brand_impersonation'):
            risk_score += 25
            risk_components.append("Possible brand impersonation in URL")
        
        # 5. VISUAL ANALYSIS - Brand impersonation and phishing templates
        visual_brand = visual_f.get('brand_analysis', {})
        if visual_brand.get('is_impersonation'):
            confidence = visual_brand.get('confidence', 0)
            if confidence > 0.7:
                risk_score += 30
                risk_components.append(f"High confidence {visual_brand.get('suspected_brand')} impersonation")
            else:
                risk_score += 15
                risk_components.append(f"Possible {visual_brand.get('suspected_brand')} impersonation")
        
        visual_similarity = visual_f.get('visual_similarity_score', 0)
        if visual_similarity > 0.8:
            risk_score += 25
            risk_components.append("High similarity to known phishing sites")
        elif visual_similarity > 0.6:
            risk_score += 10
            risk_components.append("Some similarity to phishing patterns")
        
        # 6. ML Model Integration (if available)
        if ml_prediction is not None:
            ml_risk = int(ml_prediction * 100)
            # Blend ML with rule-based, but don't let ML override strong signals
            if len(positive_signals) >= 3 and ml_risk > 60:
                # If we have many positive signals, reduce ML impact
                ml_weight = 0.15
            elif len(risk_components) >= 3 and ml_risk < 40:
                # If we have many risk signals, ML shouldn't make it safe
                ml_weight = 0.15
            else:
                # Normal blending
                ml_weight = 0.25
            
            risk_score = int((1 - ml_weight) * risk_score + ml_weight * ml_risk)
        
        # Ensure score is within bounds
        risk_score = max(0, min(100, risk_score))
        
        # Generate comprehensive reason
        if risk_score < 25:
            if positive_signals:
                reason = "Low risk - " + "; ".join(positive_signals[:2])
            else:
                reason = "No significant risk indicators detected"
        elif risk_score < 60:
            if risk_components:
                reason = "Medium risk - " + "; ".join(risk_components[:2])
            else:
                reason = "Some suspicious patterns detected"
        else:
            if risk_components:
                reason = "High risk - " + "; ".join(risk_components[:3])
            else:
                reason = "Multiple risk indicators present"
        
        return risk_score, reason
    
    def check_url_risk(self, url: str) -> Dict[str, Any]:
        """Main URL risk assessment function with comprehensive JSON output"""
        start_time = time.time()
        
        # Quick check for trusted domains
        if self.is_trusted_domain(url):
            trusted_report = {
                'url': url,
                'overall_status': 'legitimate',
                'risk_score': 0,
                'reason': 'Domain is verified and trusted.',
                'analysis_time': round(time.time() - start_time, 2),
                'trusted_domain': True,
                'ml_model_used': False,
                'details': {
                    "content_analysis": {
                        "content_risk_prediction": 0,
                        "content_risk_score": 0.0,
                        "suspicious_keywords_found": []
                    },
                    "domain_analysis": {
                        "domain": urlparse(url).netloc,
                        "domain_age_days": 5000,  # Trusted domains are old
                        "domain_length": len(urlparse(url).netloc),
                        "has_ssl": 1,
                        "domain_risk": 0
                    },
                    "reputation_analysis": {
                        "is_on_blacklist": False,
                        "virustotal_positives": 0,
                        "reported_by_users": 0,
                        "google_safe_browsing": {
                            "is_threat": False,
                            "threat_type": None
                        }
                    },
                    "visual_analysis": {
                        "screenshot_path": "not_required",
                        "visual_similarity_score": 0.0,
                        "brand_impersonation_detected": False
                    },
                    "network_analysis": {
                        "is_reachable": True,
                        "has_security_headers": True,
                        "suspicious_redirects": False
                    }
                },
                'ml_insights': {
                    "model_type": "Trusted domain bypass",
                    "confidence_level": "absolute",
                    "ml_recommendation": "Trusted domain - safe to use"
                },
                'user_tip': 'This is a verified trusted domain. Safe to use with standard security practices.'
            }
            
            # Print comprehensive JSON to console
            print("\n" + "="*80)
            print("🔍 COMPREHENSIVE URL ANALYSIS REPORT")
            print("="*80)
            print(json.dumps(trusted_report, indent=2))
            print("="*80 + "\n")
            
            return trusted_report
        
        self.logger.info(f"Starting comprehensive analysis for: {url}")
        
        try:
            # Run all analyzers
            print(f"\n📊 Running comprehensive analysis for: {url}")
            
            # 1. Domain Analysis
            print("  ↳ Analyzing domain...")
            domain_f = domain_analyzer.get_features(url)
            
            # 2. Content Analysis
            print("  ↳ Analyzing content patterns...")
            content_f = content_analyzer.get_features(url)
            content_patterns = content_f.get('pattern_features', {})
            
            # Extract suspicious keywords properly from pattern_features
            suspicious_keywords = []
            if content_patterns:
                # Keywords are stored in pattern_features.suspicious_keywords_found
                suspicious_keywords = content_patterns.get('suspicious_keywords_found', [])
                # Also check if it's in the main content_f
                if not suspicious_keywords:
                    suspicious_keywords = content_f.get('suspicious_keywords_found', [])
            
            # Debug print to see what we're getting
            if suspicious_keywords:
                print(f"     Found suspicious keywords: {suspicious_keywords}")
            
            # 3. Reputation Analysis (includes Google Safe Browsing)
            print("  ↳ Checking reputation databases...")
            reputation_f = reputation_analyzer.get_features(url)
            
            # 4. Network Analysis
            print("  ↳ Analyzing network characteristics...")
            network_f = network_analyzer.get_network_features(url)
            
            # 5. Visual Analysis
            print("  ↳ Performing visual analysis...")
            visual_f = visual_analyzer.get_features(url)
            
            # Calculate risk score using weighted approach
            ml_prediction = None
            if self.models_loaded and self.model and self.model_features:
                # ML-based scoring
                try:
                    url_features = self.extract_url_features(url)
                    feature_dict = {feature_name: url_features.get(feature_name, 0) 
                                  for feature_name in self.model_features}
                    
                    feature_df = pd.DataFrame([feature_dict])
                    feature_df = feature_df[self.model_features]
                    
                    prediction = self.model.predict(feature_df)[0]
                    probabilities = self.model.predict_proba(feature_df)[0]
                    ml_prediction = probabilities[1] if len(probabilities) > 1 else probabilities[0]
                    ml_used = True
                    
                except Exception as e:
                    self.logger.error(f"ML prediction failed: {e}")
                    ml_used = False
            else:
                ml_used = False
            
            # Use the new weighted scoring that considers all factors properly
            final_risk_score, reason = self.calculate_weighted_risk_score(
                url, domain_f, content_f, reputation_f, visual_f, network_f, ml_prediction
            )
            
            # Determine status
            if final_risk_score < self.RISK_THRESHOLDS['legitimate']:
                status = 'legitimate'
            elif final_risk_score < self.RISK_THRESHOLDS['suspicious']:
                status = 'suspicious'
            else:
                status = 'risky'
            
            # Generate ML insights
            ml_insights = self.generate_ml_insights(final_risk_score, {
                'domain_age': domain_f.get('domain_age', -1),
                'has_ssl': domain_f.get('has_ssl', False),
                'has_ip_address': domain_f.get('uses_ip', False),
                'suspicious_keywords_count': len(content_patterns.get('suspicious_keywords_found', []))
            })
            
            # User tips based on comprehensive analysis
            user_tips = {
                "legitimate": "This website appears safe. Standard security practices apply - verify URLs and use strong passwords.",
                "suspicious": "⚠️ Caution advised! Multiple risk indicators detected. Verify the site's legitimacy before proceeding.",
                "risky": "🚫 HIGH RISK! Strong indicators of fraud detected. Do NOT enter any personal or financial information."
            }
            
            # Build comprehensive report
            comprehensive_report = {
                "url": url,
                "overall_status": status,
                "risk_score": final_risk_score,
                "reason": reason,
                "analysis_time": round(time.time() - start_time, 2),
                "ml_model_used": ml_used,
                "details": {
                    "content_analysis": {
                        "content_risk_prediction": 1 if content_f.get('content_risk_score', 0) > 0.5 else 0,
                        "content_risk_score": round(content_f.get('content_risk_score', 0), 2),
                        "suspicious_keywords_found": suspicious_keywords if suspicious_keywords else [],
                        "phishing_keywords_count": content_patterns.get('phishing_keywords', 0),
                        "has_phishing_keywords": content_patterns.get('has_phishing_keywords', False),
                        "url_patterns": {
                            "has_ip_address": content_patterns.get('uses_ip', False),
                            "is_shortener": content_patterns.get('is_shortener', False),
                            "suspicious_tld": content_patterns.get('suspicious_tld', False),
                            "brand_impersonation": content_patterns.get('brand_impersonation', False),
                            "has_phishing_keywords": content_patterns.get('has_phishing_keywords', False),
                            "special_char_count": content_patterns.get('special_char_count', 0),
                            "url_length": content_patterns.get('url_length', 0),
                            "domain_has_hyphens": content_patterns.get('domain_has_hyphens', False)
                        }
                    },
                    "domain_analysis": {
                        "domain": urlparse(url).netloc,
                        "domain_age_days": domain_f.get('domain_age', -1),
                        "domain_length": domain_f.get('domain_length', 0),
                        "has_ssl": 1 if domain_f.get('has_ssl', False) else 0,
                        "domain_risk": 1 if domain_f.get('domain_risk', 0) > 0.5 else 0,
                        "subdomain_count": domain_f.get('subdomain_count', 0),
                        "domain_entropy": round(domain_f.get('domain_entropy', 0), 2)
                    },
                    "reputation_analysis": {
                        "is_on_blacklist": reputation_f.get('is_on_blacklist', False),
                        "virustotal_positives": reputation_f.get('virustotal_positives', 0),
                        "virustotal_total": reputation_f.get('virustotal_total', 0),
                        "reported_by_users": 0,  # Placeholder for future implementation
                        "google_safe_browsing": {
                            "is_threat": reputation_f.get('is_gsb_threat', False),
                            "threat_type": reputation_f.get('gsb_threat_type', None)
                        },
                        "reputation_score": round(reputation_f.get('reputation_score', 0), 2),
                        "is_whitelisted": reputation_f.get('is_on_whitelist', False)
                    },
                    "visual_analysis": {
                        "screenshot_path": visual_f.get('screenshot_path', 'not_available'),
                        "visual_similarity_score": round(visual_f.get('visual_similarity_score', 0.0), 2),
                        "brand_impersonation_detected": visual_f.get('brand_analysis', {}).get('is_impersonation', False),
                        "suspected_brand": visual_f.get('brand_analysis', {}).get('suspected_brand', None),
                        "impersonation_confidence": round(visual_f.get('brand_analysis', {}).get('confidence', 0), 2),
                        "phishing_template_match": visual_f.get('matched_template', None) is not None,
                        "analysis_success": visual_f.get('analysis_success', False)
                    },
                    "network_analysis": {
                        "is_reachable": network_f.get('is_reachable', False),
                        "final_url": network_f.get('final_url', url),
                        "has_security_headers": {
                            "csp": network_f.get('has_csp_header', False),
                            "hsts": network_f.get('has_hsts_header', False),
                            "x_frame_options": network_f.get('has_xfo_header', False)
                        },
                        "suspicious_redirects": network_f.get('final_url', url) != url,
                        "outgoing_link_ratio": round(network_f.get('outgoing_link_ratio', -1), 2),
                        "dns_records": {
                            "has_mx": network_f.get('dns_has_mx_record', False),
                            "has_spf": network_f.get('dns_has_spf_record', False)
                        }
                    }
                },
                "ml_insights": ml_insights,
                "user_tip": user_tips.get(status, user_tips["suspicious"]),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
            
            # Print comprehensive JSON to console
            print("\n" + "="*80)
            print("🔍 COMPREHENSIVE URL ANALYSIS REPORT")
            print("="*80)
            print(json.dumps(comprehensive_report, indent=2))
            print("="*80)
            
            # Print summary
            print("\n📊 ANALYSIS SUMMARY:")
            print(f"  • Status: {status.upper()}")
            print(f"  • Risk Score: {final_risk_score}%")
            print(f"  • ML Model: {'✅ Used' if ml_used else '❌ Fallback'}")
            print(f"  • Time: {comprehensive_report['analysis_time']}s")
            
            if reputation_f.get('is_gsb_threat'):
                print(f"  ⚠️ GOOGLE SAFE BROWSING ALERT: {reputation_f.get('gsb_threat_type')}")
            
            if visual_f.get('brand_analysis', {}).get('is_impersonation'):
                print(f"  ⚠️ BRAND IMPERSONATION: {visual_f['brand_analysis']['suspected_brand']}")
            
            print("="*80 + "\n")
            
            return comprehensive_report
            
        except Exception as e:
            self.logger.error(f"Error during URL analysis: {e}", exc_info=True)
            error_report = {
                'url': url,
                'overall_status': 'error',
                'risk_score': -1,
                'reason': f'Analysis failed: {str(e)}',
                'analysis_time': round(time.time() - start_time, 2),
                'details': {},
                'user_tip': 'System error occurred. Please try again later.',
                'error': str(e)
            }
            
            print("\n" + "="*80)
            print("❌ ANALYSIS ERROR")
            print("="*80)
            print(json.dumps(error_report, indent=2))
            print("="*80 + "\n")
            
            return error_report
    
    def calculate_rule_based_score(self, url: str, domain_f: dict, content_f: dict, 
                                  reputation_f: dict, visual_f: dict) -> int:
        """Calculate risk score using rules when ML model is not available"""
        risk_score = 0
        
        # Domain analysis (25%)
        if domain_f.get('domain_age', -1) < 30:
            risk_score += 20
        elif domain_f.get('domain_age', -1) < 90:
            risk_score += 10
        
        if not domain_f.get('has_ssl', True):
            risk_score += 15
        
        # Content analysis (20%)
        if content_f.get('content_risk_score', 0) > 0.7:
            risk_score += 20
        elif content_f.get('content_risk_score', 0) > 0.4:
            risk_score += 10
        
        # Reputation analysis (35%)
        if reputation_f.get('is_on_blacklist', False):
            risk_score += 35
        
        if reputation_f.get('virustotal_positives', 0) > 5:
            risk_score += 30
        elif reputation_f.get('virustotal_positives', 0) > 0:
            risk_score += 15
        
        # Visual analysis (20%)
        if visual_f.get('visual_similarity_score', 0) > 0.7:
            risk_score += 20
        elif visual_f.get('visual_similarity_score', 0) > 0.4:
            risk_score += 10
        
        if visual_f.get('brand_analysis', {}).get('is_impersonation', False):
            risk_score += 15
        
        return min(100, risk_score)

# Helper function for console output formatting (for compatibility)
def format_detailed_console_output(result: dict) -> str:
    """Format the analysis result for console display"""
    output = []
    output.append("\n" + "="*80)
    output.append("🔍 URL ANALYSIS REPORT")
    output.append("="*80)
    output.append(json.dumps(result, indent=2))
    output.append("="*80)
    
    # Add summary
    output.append("\n📊 QUICK SUMMARY:")
    output.append(f"  • URL: {result.get('url', 'N/A')}")
    output.append(f"  • Status: {result.get('overall_status', 'N/A').upper()}")
    output.append(f"  • Risk Score: {result.get('risk_score', 'N/A')}%")
    output.append(f"  • Analysis Time: {result.get('analysis_time', 'N/A')}s")
    
    # Add any special alerts
    details = result.get('details', {})
    reputation = details.get('reputation_analysis', {})
    if reputation.get('google_safe_browsing', {}).get('is_threat'):
        output.append(f"  ⚠️ GOOGLE SAFE BROWSING ALERT: {reputation['google_safe_browsing'].get('threat_type')}")
    
    visual = details.get('visual_analysis', {})
    if visual.get('brand_impersonation_detected'):
        output.append(f"  ⚠️ BRAND IMPERSONATION: {visual.get('suspected_brand')}")
    
    output.append(f"\n💡 Tip: {result.get('user_tip', 'N/A')}")
    output.append("="*80 + "\n")
    
    return "\n".join(output)

# Test function
if __name__ == "__main__":
    print("🚀 Testing Enhanced URL Checker with Comprehensive JSON Output")
    print("="*80)
    
    checker = EnhancedURLChecker()
    
    test_urls = [
        "https://www.google.com",
        "http://suspicious-paypal-login.tk/verify",
        "https://secure-account-update.ml/signin",  # Should trigger keywords
        "https://github.com"
    ]
    
    for url in test_urls:
        print(f"\n🔗 Testing: {url}")
        result = checker.check_url_risk(url)
        
        # The JSON is already printed inside check_url_risk method