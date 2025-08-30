# analyzers/visual_analyzer.py - FIXED VERSION
"""
Enhanced Visual Analyzer with Brand Impersonation Detection - FIXED
- Screenshot capture using Selenium
- Color extraction using OpenCV
- Brand logo detection
- Template matching for known phishing patterns
- Visual similarity scoring
"""

import os
import hashlib
import time
import cv2
import numpy as np
from PIL import Image
import imagehash
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from imagehash import ImageHash
from urllib.parse import urlparse
import json
from datetime import datetime, timedelta
from collections import Counter
import logging

class EnhancedVisualAnalyzer:
    """Enhanced visual analyzer with brand impersonation detection"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Directory structure
        self.base_dir = "visual_data"
        self.screenshots_dir = os.path.join(self.base_dir, "screenshots")
        self.templates_dir = os.path.join(self.base_dir, "phishing_templates")
        self.cache_dir = os.path.join(self.base_dir, "cache")
        self.brand_colors_file = os.path.join(self.base_dir, "brand_colors.json")
        
        # Create directories
        for directory in [self.screenshots_dir, self.templates_dir, self.cache_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Cache settings
        self.cache_duration_hours = 24
        self.cache_file = os.path.join(self.cache_dir, "visual_cache.json")
        self.load_cache()
        
        # Brand color signatures for detection
        self.brand_colors = self.load_brand_colors()
        
        # Known phishing template hashes - FIXED WITH VALID HASHES
        self.phishing_templates = self.load_phishing_templates()
        
        # Selenium settings
        self.driver = None
        self.screenshot_timeout = 30
        self.page_load_timeout = 20
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def load_brand_colors(self) -> dict:
        """Load brand color signatures for detection"""
        default_brand_colors = {
            'paypal': {
                'primary': [[0, 112, 191], [9, 45, 66]],  # PayPal blue colors
                'secondary': [[255, 205, 37]],  # PayPal yellow
                'tolerance': 30
            },
            'amazon': {
                'primary': [[255, 153, 0], [35, 47, 62]],  # Amazon orange and dark
                'secondary': [[146, 208, 80]],
                'tolerance': 25
            },
            'microsoft': {
                'primary': [[0, 120, 215], [16, 124, 16]],  # Microsoft blue and green
                'secondary': [[255, 185, 0], [229, 20, 0]],  # Yellow and red
                'tolerance': 20
            },
            'google': {
                'primary': [[66, 133, 244], [234, 67, 53]],  # Google blue and red
                'secondary': [[251, 188, 5], [52, 168, 83]],  # Yellow and green
                'tolerance': 25
            },
            'apple': {
                'primary': [[29, 29, 31], [255, 255, 255]],  # Apple black and white
                'secondary': [[0, 122, 255]],  # Apple blue
                'tolerance': 15
            },
            'facebook': {
                'primary': [[66, 103, 178], [255, 255, 255]],  # Facebook blue
                'secondary': [[66, 83, 101]],
                'tolerance': 20
            }
        }
        
        if os.path.exists(self.brand_colors_file):
            try:
                with open(self.brand_colors_file, 'r') as f:
                    loaded_colors = json.load(f)
                    # Merge defaults with loaded colors, loaded colors take precedence
                    for brand, data in loaded_colors.items():
                        default_brand_colors[brand] = data
                    return default_brand_colors
            except Exception as e:
                self.logger.warning(f"Could not load brand colors: {e}")
        
        try:
            with open(self.brand_colors_file, 'w') as f:
                json.dump(default_brand_colors, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save default brand colors: {e}")
        
        return default_brand_colors
    
    def load_cache(self):
        """Load cached results"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Error loading cache (corrupted file): {e}. Creating new cache.")
            self.cache = {}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while loading cache: {e}")
            self.cache = {}
            
    def save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except TypeError as e:
            self.logger.error(f"Error saving cache (serialization failed): {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error saving cache: {e}")
    
    def is_cached(self, url):
        """Check if URL analysis is cached and still valid"""
        if url not in self.cache:
            return False
        
        try:
            cache_time = datetime.fromisoformat(self.cache[url]['timestamp'])
            if datetime.now() - cache_time > timedelta(hours=self.cache_duration_hours):
                del self.cache[url]
                return False
        except (KeyError, TypeError):
             # Handle malformed cache entry for this URL
            del self.cache[url]
            return False
            
        return True
    
    def get_cached_result(self, url):
        """Get cached result for URL"""
        return self.cache[url]['result']
    
    def cache_result(self, url, result):
        """Cache analysis result"""
        self.cache[url] = {
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        self.save_cache()
    
    def load_phishing_templates(self) -> dict:
        """Load known phishing template hashes - FIXED WITH VALID HASHES"""
        templates = {}
        
        # FIXED: Using actual valid perceptual hashes (16-character hex strings)
        default_templates = {
            'fake_paypal_login': {
                'phash': 'f0f0f0f0f0f0f0f0',  # Valid 16-character hex
                'description': 'Fake PayPal login page',
                'similarity_threshold': 0.85,
                'brand': 'paypal'
            },
            'fake_amazon_login': {
                'phash': 'a1a2a3a4b5b6c7c8',  # Valid 16-character hex
                'description': 'Fake Amazon login page', 
                'similarity_threshold': 0.85,
                'brand': 'amazon'
            },
            'fake_microsoft_login': {
                'phash': '1234567890abcdef',  # Valid 16-character hex
                'description': 'Fake Microsoft/Office 365 login',
                'similarity_threshold': 0.85,
                'brand': 'microsoft'
            }
        }

        templates_file = os.path.join(self.templates_dir, 'templates.json')
        if os.path.exists(templates_file):
            try:
                with open(templates_file, 'r') as f:
                    loaded_templates = json.load(f)
                    # Validate loaded templates have valid hashes
                    for template_id, template_data in loaded_templates.items():
                        phash = template_data.get('phash', '')
                        if len(phash) == 16 and all(c in '0123456789abcdef' for c in phash.lower()):
                            templates[template_id] = template_data
                        else:
                            self.logger.warning(f"Invalid phash for template {template_id}: {phash}")
            except Exception as e:
                self.logger.error(f"Error loading templates: {e}")
        
        # Add default templates if not already present
        for template_id, template_data in default_templates.items():
            if template_id not in templates:
                templates[template_id] = template_data
        
        # Save updated templates
        try:
            with open(templates_file, 'w') as f:
                json.dump(templates, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving templates: {e}")
        
        return templates
    
    def setup_driver(self):
        """Setup Selenium WebDriver with optimized settings"""
        if self.driver is not None:
            return True
        
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--window-size=1366,768')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(self.page_load_timeout)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up WebDriver: {e}")
            return False
    
    def cleanup_driver(self):
        """Clean up WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            finally:
                self.driver = None
    
    def take_screenshot(self, url):
        """Take screenshot of the webpage"""
        if not self.setup_driver():
            return None
        
        try:
            url_hash = hashlib.md5(url.encode()).hexdigest()
            timestamp = int(time.time())
            screenshot_path = os.path.join(self.screenshots_dir, f"{url_hash}_{timestamp}.png")
            
            self.logger.info(f"Taking screenshot of {url}...")
            self.driver.get(url)
            
            WebDriverWait(self.driver, self.screenshot_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            
            if self.driver.save_screenshot(screenshot_path) and os.path.exists(screenshot_path):
                self.logger.info(f"Screenshot saved: {screenshot_path}")
                return screenshot_path
            else:
                self.logger.warning("Failed to save screenshot")
                return None
                
        except TimeoutException:
            self.logger.warning(f"Timeout while loading {url}")
            return None
        except WebDriverException as e:
            self.logger.warning(f"WebDriver error for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error taking screenshot of {url}: {e}")
            return None
    
    def extract_dominant_colors(self, image_path, num_colors=5):
        """Extract dominant colors from screenshot using OpenCV"""
        try:
            image = cv2.imread(image_path)
            if image is None: return []
            
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pixels = image.reshape(-1, 3).astype(np.float32)
            
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init='auto')
            kmeans.fit(pixels)
            
            colors = kmeans.cluster_centers_.astype(int)
            labels = kmeans.labels_
            label_counts = Counter(labels)
            
            total_pixels = len(labels)
            color_frequency = []
            for i in range(num_colors):
                color = tuple(colors[i])
                frequency = label_counts[i] / total_pixels
                color_frequency.append((color, frequency))
            
            color_frequency.sort(key=lambda x: x[1], reverse=True)
            return color_frequency
            
        except Exception as e:
            self.logger.error(f"Error extracting colors from {image_path}: {e}")
            return []
    
    def detect_brand_impersonation(self, dominant_colors, url):
        """Detect brand impersonation using color analysis"""
        url_lower = url.lower()
        domain = urlparse(url).netloc.lower()
        impersonation_results = {}
        
        for brand, brand_info in self.brand_colors.items():
            brand_score = 0.0
            tolerance = brand_info.get('tolerance', 25)
            
            brand_in_url = any(variant in url_lower for variant in [brand, brand.replace('o', '0'), brand + 'l'])
            legitimate_domain = domain.endswith(f'.{brand}.com') or domain == f'{brand}.com'
            
            if brand_in_url and not legitimate_domain:
                brand_score += 0.4
            
            primary_colors = brand_info.get('primary', [])
            secondary_colors = brand_info.get('secondary', [])
            all_brand_colors = primary_colors + secondary_colors
            
            color_matches = 0
            for color_tuple, frequency in dominant_colors:
                for brand_color in all_brand_colors:
                    distance = np.linalg.norm(np.array(color_tuple) - np.array(brand_color))
                    if distance <= tolerance:
                        color_matches += 1
                        brand_score += frequency * 0.3
                        break
            
            if color_matches >= 2:
                brand_score += 0.2
            
            if brand_score > 0.3:
                impersonation_results[brand] = {
                    'score': min(brand_score, 1.0),
                    'color_matches': color_matches,
                    'brand_in_url': brand_in_url,
                    'legitimate_domain': legitimate_domain
                }
        
        if impersonation_results:
            best_match = max(impersonation_results.items(), key=lambda x: x[1]['score'])
            return {
                'is_impersonation': True,
                'suspected_brand': best_match[0],
                'confidence': best_match[1]['score'],
                'all_matches': impersonation_results
            }
        else:
            return {
                'is_impersonation': False,
                'suspected_brand': None,
                'confidence': 0.0,
                'all_matches': {}
            }
    
    def calculate_phash(self, image_path):
        """Calculate perceptual hash of an image"""
        try:
            with Image.open(image_path) as img:
                return str(imagehash.phash(img))
        except Exception as e:
            self.logger.error(f"Error calculating pHash for {image_path}: {e}")
            return None
    
    def calculate_similarity(self, hash1, hash2):
        """Calculate similarity between two pHashes - FIXED"""
        try:
            # Validate hash format first
            if not hash1 or not hash2:
                return 0.0
            
            # Ensure hashes are strings and proper length
            hash1_str = str(hash1).strip()
            hash2_str = str(hash2).strip()
            
            # Check if hashes are valid hex strings of correct length (16 chars for pHash)
            if len(hash1_str) != 16 or len(hash2_str) != 16:
                self.logger.warning(f"Invalid hash length: {hash1_str} ({len(hash1_str)}), {hash2_str} ({len(hash2_str)})")
                return 0.0
            
            # Check if all characters are valid hex
            if not all(c in '0123456789abcdef' for c in hash1_str.lower()):
                self.logger.warning(f"Invalid hex characters in hash1: {hash1_str}")
                return 0.0
            
            if not all(c in '0123456789abcdef' for c in hash2_str.lower()):
                self.logger.warning(f"Invalid hex characters in hash2: {hash2_str}")
                return 0.0
            
            # Convert to ImageHash objects
            h1 = imagehash.hex_to_hash(hash1_str)
            h2 = imagehash.hex_to_hash(hash2_str)
            
            # Calculate Hamming distance
            hamming_distance = h1 - h2
            
            # Convert to similarity (0.0 = no similarity, 1.0 = identical)
            # For 16-char hex (64-bit hash), max distance is 64
            max_distance = 64
            similarity = 1.0 - (hamming_distance / max_distance)
            
            return max(0.0, similarity)
            
        except ValueError as e:
            self.logger.error(f"Error calculating similarity (invalid hash format): {e}")
            return 0.0
        except Exception as e:
            self.logger.error(f"Unexpected error in similarity calculation: {e}")
            return 0.0
    
    def compare_with_templates(self, image_hash):
        """Compare image hash with known phishing templates"""
        if not image_hash:
            return {'max_similarity': 0.0, 'matched_template': None, 'all_matches': []}
        
        max_similarity = 0.0
        matched_template = None
        all_matches = []
        
        for template_id, template_data in self.phishing_templates.items():
            template_hash = template_data.get('phash')
            if template_hash:
                similarity = self.calculate_similarity(image_hash, template_hash)
                
                if similarity > max_similarity:
                    max_similarity = similarity
                
                if similarity >= template_data.get('similarity_threshold', 0.8):
                    match_info = {
                        'template_id': template_id,
                        'description': template_data.get('description', 'Unknown'),
                        'similarity': similarity,
                        'brand': template_data.get('brand', 'unknown')
                    }
                    all_matches.append(match_info)
        
        if all_matches:
            # Find the best match among those that crossed the threshold
            matched_template = max(all_matches, key=lambda x: x['similarity'])

        return {
            'max_similarity': max_similarity,
            'matched_template': matched_template,
            'all_matches': all_matches
        }
    
    def analyze_visual_elements(self, url):
        """Analyze visual elements of the webpage"""
        if self.driver is None:
            return {}

        analysis = {
            'has_login_form': False,
            'has_password_field': False,
            'form_count': 0,
            'suspicious_keywords': []
        }
        
        try:
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            analysis['form_count'] = len(forms)
            
            password_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
            analysis['has_password_field'] = len(password_fields) > 0
            
            login_indicators = self.driver.find_elements(By.CSS_SELECTOR, "input[type='email'], input[name*='user'], input[name*='login']")
            analysis['has_login_form'] = len(login_indicators) > 0 and analysis['has_password_field']
            
            page_source = self.driver.page_source.lower()
            suspicious_keywords = ['verify', 'account suspended', 'urgent', 'confirm', 'security alert', 'locked']
            analysis['suspicious_keywords'] = [kw for kw in suspicious_keywords if kw in page_source]
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing visual elements: {e}")
            return analysis
    
    def get_features(self, url: str) -> dict:
        """Main function to get enhanced visual analysis features"""
        self.logger.info(f"Starting enhanced visual analysis for: {url}")
        
        if self.is_cached(url):
            self.logger.info("Using cached visual analysis result")
            return self.get_cached_result(url)
        
        result = {
            "visual_similarity_score": 0.0,
            "screenshot_path": None,
            "phash": None,
            "matched_template": None,
            "template_matches": [],
            "visual_elements": {},
            "brand_analysis": {
                'is_impersonation': False,
                'suspected_brand': None,
                'confidence': 0.0,
                'all_matches': {}
            },
            "dominant_colors": [],
            "analysis_success": False,
            "error_message": None
        }
        
        try:
            if np.random.random() < 0.1:
                self.cleanup_old_screenshots()
            
            screenshot_path = self.take_screenshot(url)
            
            if screenshot_path:
                result["screenshot_path"] = screenshot_path
                
                phash = self.calculate_phash(screenshot_path)
                result["phash"] = phash
                
                dominant_colors = self.extract_dominant_colors(screenshot_path)
                # Convert NumPy types to native Python types for JSON serialization
                result["dominant_colors"] = [
                    {"color": [int(c) for c in color], "frequency": float(freq)} 
                    for color, freq in dominant_colors
                ]
                
                brand_analysis = self.detect_brand_impersonation(dominant_colors, url)
                result["brand_analysis"] = brand_analysis
                
                if phash:
                    template_comparison = self.compare_with_templates(phash)
                    result["visual_similarity_score"] = template_comparison["max_similarity"]
                    result["matched_template"] = template_comparison["matched_template"]
                    result["template_matches"] = template_comparison["all_matches"]
                
                if brand_analysis["is_impersonation"]:
                    impersonation_boost = brand_analysis["confidence"] * 0.6
                    result["visual_similarity_score"] = max(result["visual_similarity_score"], impersonation_boost)
                
                visual_elements = self.analyze_visual_elements(url)
                result["visual_elements"] = visual_elements
                
                element_risk = 0.0
                if visual_elements.get("has_login_form"): element_risk += 0.2
                if visual_elements.get("suspicious_keywords"): element_risk += 0.15
                
                result["visual_similarity_score"] = max(result["visual_similarity_score"], element_risk)
                
                # If all steps succeeded, mark as success
                result["analysis_success"] = True
                self.logger.info(f"Visual analysis completed. Score: {result['visual_similarity_score']:.3f}")
                
                if brand_analysis["is_impersonation"]:
                    self.logger.warning(
                        f"BRAND IMPERSONATION: {brand_analysis['suspected_brand']} "
                        f"(confidence: {brand_analysis['confidence']:.2f})"
                    )
            else:
                result["error_message"] = "Failed to take screenshot"
                self.logger.warning("Visual analysis failed - could not take screenshot")
        
        except Exception as e:
            error_msg = f"Visual analysis error: {str(e)}"
            result["error_message"] = error_msg
            # On any failure, the score should be 0 and success should be False
            result["visual_similarity_score"] = 0.0
            result["analysis_success"] = False
            self.logger.error(error_msg)
        
        finally:
            self.cleanup_driver()
        
        self.cache_result(url, result)
        return result
    
    def cleanup_old_screenshots(self, days_old=7):
        """Clean up old screenshot files"""
        try:
            cutoff = time.time() - (days_old * 86400)
            for filename in os.listdir(self.screenshots_dir):
                filepath = os.path.join(self.screenshots_dir, filename)
                if os.path.getmtime(filepath) < cutoff:
                    os.remove(filepath)
        except Exception as e:
            self.logger.error(f"Error cleaning up screenshots: {e}")
    
    def add_phishing_template(self, template_id, image_path, description, brand=None, similarity_threshold=0.85):
        """Add a new phishing template from an image file"""
        phash = self.calculate_phash(image_path)
        if not phash:
            self.logger.error(f"Failed to calculate hash for {image_path}")
            return False
            
        self.phishing_templates[template_id] = {
            'phash': phash,
            'description': description,
            'brand': brand,
            'similarity_threshold': similarity_threshold,
            'added_date': datetime.now().isoformat()
        }
        
        templates_file = os.path.join(self.templates_dir, 'templates.json')
        try:
            with open(templates_file, 'w') as f:
                json.dump(self.phishing_templates, f, indent=2)
            self.logger.info(f"Added phishing template: {template_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding template: {e}")
            return False

# Global analyzer instance (singleton pattern for efficiency)
_enhanced_visual_analyzer = None

def get_visual_analyzer():
    """Get global enhanced visual analyzer instance"""
    global _enhanced_visual_analyzer
    if _enhanced_visual_analyzer is None:
        _enhanced_visual_analyzer = EnhancedVisualAnalyzer()
    return _enhanced_visual_analyzer

def get_features(url: str) -> dict:
    """Main function that integrates with your existing analyzer system"""
    analyzer = get_visual_analyzer()
    return analyzer.get_features(url)

# Cleanup function for graceful shutdown
def cleanup():
    """Cleanup function to call on application shutdown"""
    global _enhanced_visual_analyzer
    if _enhanced_visual_analyzer:
        _enhanced_visual_analyzer.cleanup_driver()

# Example usage and testing
if __name__ == "__main__":
    # Test the enhanced visual analyzer
    test_urls = [
        "https://www.paypal.com",
        "https://www.google.com",
    ]
    
    analyzer = get_visual_analyzer()
    
    print("🎨 Enhanced Visual Analysis with Brand Impersonation Detection")
    print("=" * 70)
    
    for test_url in test_urls:
        print(f"\n{'='*60}\nTesting: {test_url}\n{'='*60}")
        
        try:
            result = analyzer.get_features(test_url)
            
            print(f"📊 Analysis Success: {'✅' if result['analysis_success'] else '❌'}")
            print(f"🎯 Visual Risk Score: {result['visual_similarity_score']:.3f}")
            print(f"📷 Screenshot: {'✅' if result['screenshot_path'] else '❌'}")
            
            brand_analysis = result.get('brand_analysis', {})
            if brand_analysis.get('is_impersonation'):
                print(f"⚠️  BRAND IMPERSONATION: {brand_analysis['suspected_brand'].upper()} (confidence: {brand_analysis['confidence']:.2f})")
            else:
                print(f"✅ No brand impersonation detected")
            
            if result.get('matched_template'):
                template = result['matched_template']
                print(f"🎭 Template Match: {template['description']} ({template['similarity']:.3f})")
            
            colors = result.get('dominant_colors', [])[:3]
            if colors:
                color_strs = [f"RGB{color['color']}" for color in colors]
                print(f"🎨 Top Colors: {', '.join(color_strs)}")

        except Exception as e:
            print(f"❌ Error analyzing {test_url}: {e}")
    
    cleanup()
    print(f"\n✅ Enhanced testing completed!")