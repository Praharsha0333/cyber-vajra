import argparse
import json
import os
import hashlib
import pickle
import pandas as pd
import numpy as np
import requests
import re 
import logging
from datetime import datetime

# Configure the androguard logger to be less verbose before importing
log = logging.getLogger('androguard')
log.setLevel(logging.CRITICAL)

from androguard.core.apk import APK

# ==============================================================================
# STRING SCANNER LOGIC
# ==============================================================================
def scan_strings(apk_object):
    urls_found = []
    keywords_found = {}
    URL_REGEX = r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))'
    SUSPICIOUS_KEYWORDS = ['password', 'credit card', 'account', 'login', 'verify', 'update', 'security', 'bank', 'ssn', 'social security']
    try:
        all_strings = []
        for dex in apk_object.get_dex():
            if hasattr(dex, 'get_strings'):
                all_strings.extend(dex.get_strings())
        for string in all_strings:
            urls = re.findall(URL_REGEX, string)
            if urls:
                urls_found.extend([url[0] for url in urls])
            for keyword in SUSPICIOUS_KEYWORDS:
                if keyword in string.lower():
                    keywords_found[keyword] = keywords_found.get(keyword, 0) + 1
    except Exception as e:
        return {'error': f"Error during string scan: {e}"}
    return {'urls_found': list(set(urls_found)), 'suspicious_keywords': keywords_found}

# ==============================================================================
# VIRUSTOTAL ANALYZER LOGIC
# ==============================================================================
def get_virustotal_report(file_hash):
    api_key = os.environ.get("VIRUSTOTAL_API_KEY")
    if not api_key:
        return {"error": "VirusTotal API key not found."}
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    headers = {"x-apikey": api_key}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get('data', {})
            attributes = data.get('attributes', {})
            stats = attributes.get('last_analysis_stats', {})
            scan_timestamp = attributes.get('last_analysis_date')
            human_readable_date = datetime.fromtimestamp(scan_timestamp).strftime('%Y-%m-%d %H:%M:%S') if scan_timestamp else "N/A"
            return {'positives': stats.get('malicious', 0) + stats.get('suspicious', 0), 'total': sum(stats.values()), 'scan_date': human_readable_date}
        elif response.status_code == 404:
            return {"status": "File not found in VirusTotal database."}
        else:
            return {"error": f"VirusTotal API error: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Could not connect to VirusTotal: {e}"}

# ==============================================================================
# METADATA EXTRACTOR LOGIC
# ==============================================================================
def extract_metadata(filepath, apk_object):
    try:
        with open(filepath, 'rb') as f:
            sha256_hash = hashlib.sha256(f.read()).hexdigest()
        cert_data_list = apk_object.get_certificates_der_v2() or apk_object.get_certificates_der()
        signature_sha256 = hashlib.sha256(cert_data_list[0]).hexdigest() if cert_data_list else "N/A"
        return {
            'app_name': apk_object.get_app_name(), 'package_name': apk_object.get_package(),
            'version_name': apk_object.get_androidversion_name(), 'permissions': apk_object.get_permissions(),
            'signature_sha256': signature_sha256, 'file_sha256': sha256_hash
        }
    except Exception as e:
        return {'error': f"Could not extract metadata: {e}"}

# ==============================================================================
# COMPARATIVE ANALYZER LOGIC
# ==============================================================================
def compare_with_known_apps(metadata, db_path='known_apps.json'):
    from difflib import SequenceMatcher
    warnings = []
    try:
        with open(db_path, 'r') as f:
            known_apps = json.load(f)
    except FileNotFoundError:
        return [{'type': 'config_error', 'message': 'Known apps database not found.'}]
    apk_pkg, apk_sig, apk_name = metadata.get('package_name'), metadata.get('signature_sha256'), metadata.get('app_name', '').lower()
    for app in known_apps:
        if apk_pkg == app['package_name'] and apk_sig != app['signature_sha256'] and apk_sig != "N/A":
            warnings.append({'type': 'signature_mismatch', 'message': f"Signature does not match official signature for '{app['app_name']}'. This is a strong indicator of a fraudulent clone."})
        if SequenceMatcher(None, apk_name, app['app_name'].lower()).ratio() > 0.85 and apk_pkg != app['package_name']:
            warnings.append({'type': 'impersonation_attempt', 'message': f"App name is very similar to '{app['app_name']}', but has a different package name."})
    return warnings

# ==============================================================================
# RISK SCORING ENGINE LOGIC (Updated with Harsher Confidence Ratings)
# ==============================================================================
MODEL, FEATURES = None, []
if os.path.exists('apk_classifier.pkl') and os.path.exists('features.json'):
    with open('apk_classifier.pkl', 'rb') as f: MODEL = pickle.load(f)
    with open('features.json', 'r') as f: FEATURES = json.load(f)

DANGEROUS_PERMISSIONS = {
    "android.permission.READ_SMS": (15, "Can read all SMS messages, including private conversations and two-factor authentication codes.", "Spyware Risk"),
    "android.permission.SEND_SMS": (20, "Can send SMS messages from your phone without your knowledge, potentially signing you up for costly premium services.", "Toll Fraud Risk"),
    "android.permission.READ_CONTACTS": (10, "Can access and steal your entire contact list.", "Spyware Risk"),
    "android.permission.ACCESS_FINE_LOCATION": (10, "Can track your precise physical location.", "Spyware Risk"),
    "android.permission.RECORD_AUDIO": (15, "Can record audio using the microphone at any time.", "Spyware Risk"),
    "android.permission.CAMERA": (10, "Can access your camera to take pictures or record video without your knowledge.", "Spyware Risk"),
    "android.permission.INSTALL_PACKAGES": (20, "Can install other applications on your device, which could be malware.", "Malware Risk"),
    "android.permission.REQUEST_INSTALL_PACKAGES": (20, "Can request to install other apps, potentially tricking users into installing malware.", "Trojan Risk"),
    "android.permission.BIND_DEVICE_ADMIN": (25, "Can gain administrative privileges, making the app very difficult to uninstall.", "Malware Risk"),
    "android.permission.SYSTEM_ALERT_WINDOW": (15, "Can draw over other apps, which can be used to create fake login screens and steal passwords.", "Phishing Risk"),
    "android.permission.QUERY_ALL_PACKAGES": (10, "Can see all other apps installed on your device, a potential privacy risk.", "Privacy Risk"),
    "android.permission.REQUEST_DELETE_PACKAGES": (15, "Can request to uninstall other apps, potentially removing security software.", "Persistence Risk"),
    "android.permission.RECEIVE_BOOT_COMPLETED": (5, "Allows the app to start itself as soon as the device finishes booting up.", "Stealth Risk")
}

def calculate_risk(analysis_results):
    reasons = []
    permission_risk = 0
    vt_risk = 0
    heuristic_risk = 0

    # --- Calculate Permission Risk ---
    apk_permissions = analysis_results.get('metadata', {}).get('permissions', [])
    dangerous_found = [p for p in apk_permissions if p in DANGEROUS_PERMISSIONS]
    if dangerous_found:
        for perm in dangerous_found:
            weight, message, risk_type = DANGEROUS_PERMISSIONS[perm]
            permission_risk += weight
            reasons.append({"level": "High Risk Permission", "risk_type": risk_type, "message": f"Requests '{perm.split('.')[-1]}': {message}"})

    # --- Calculate VirusTotal Risk ---
    vt_report = analysis_results.get('virustotal', {})
    if vt_report and not vt_report.get('error'):
        positives, total = vt_report.get('positives', 0), vt_report.get('total', 1)
        if total > 0:
            vt_risk = (positives / total) * 100
        if positives > 0:
             reasons.append({"level": "CRITICAL", "risk_type": "Malware", "message": f"Flagged by {positives}/{total} engines on VirusTotal."})

    # --- Calculate Other Heuristic Risk ---
    for warning in analysis_results.get('clone_analysis', []):
        heuristic_risk += 65 if warning['type'] == 'signature_mismatch' else 45
        reasons.append({"level": "CRITICAL", "risk_type": "Clone / Impersonation", "message": warning['message']})

    # --- Final Score Calculation ---
    total_risk_score = min(100, int(permission_risk + vt_risk + heuristic_risk))
    
    # --- Determine User Confidence Score & Level ---
    confidence_score = 100 - total_risk_score
    if confidence_score >= 81:
        confidence_level = "✅ Excellent Confidence"
    elif confidence_score >= 51:
        confidence_level = "⚠️ Fair Confidence"
    elif confidence_score >= 21:
        # This line ensures scores like 25 are labeled "Poor Confidence".
        confidence_level = "🚩 Poor Confidence" 
    elif confidence_score > 10:
        confidence_level = "❌ No Confidence - DO NOT INSTALL"
    else:
        confidence_level = "☠️ CRITICAL RISK - MALWARE LIKELY"


    if not reasons:
        reasons.append({"level": "Info", "risk_type": "None Detected", "message": "This app appears to be safe based on our analysis."})

    return confidence_score, confidence_level, total_risk_score, reasons

# ==============================================================================
# MAIN ANALYSIS PIPELINE
# ==============================================================================
def analyze_apk(file_path):
    if not os.path.exists(file_path):
        return {"error": f"File not found at: {file_path}"}
    try:
        apk_object = APK(file_path)
    except Exception as e:
        return {'error': f"Could not process APK file: {e}"}

    full_analysis = {}
    metadata = extract_metadata(file_path, apk_object)
    if 'error' in metadata: return metadata
    full_analysis['metadata'] = metadata

    full_analysis['virustotal'] = get_virustotal_report(metadata.get('file_sha256'))
    full_analysis['string_analysis'] = scan_strings(apk_object)
    full_analysis['clone_analysis'] = compare_with_known_apps(metadata)
    
    confidence_score, confidence_level, risk_score, reasons = calculate_risk(full_analysis)
    
    # AI analysis is a secondary detail
    ai_classification = {"type": "Not Available", "confidence_percent": 0}
    if MODEL and FEATURES:
        apk_permissions = metadata.get('permissions', [])
        feature_data = {feature: [1 if feature in apk_permissions else 0] for feature in FEATURES}
        df_vector = pd.DataFrame(feature_data)
        benign_prob = MODEL.predict_proba(df_vector)[0][0] * 100
        ai_classification['confidence_percent'] = int(benign_prob)
        ai_classification['type'] = "Likely Benign" if benign_prob > 50 else "Potentially Unsafe"

    final_report = {
        'confidence_score': confidence_score,
        'confidence_level': confidence_level,
        'reasons': reasons,
        'details': {
            'risk_score': risk_score,
            'ai_analysis': ai_classification,
            'metadata': metadata,
            'virustotal': full_analysis.get('virustotal'),
            'string_analysis': full_analysis.get('string_analysis'),
            'clone_analysis': full_analysis.get('clone_analysis')
        }
    }
    return final_report

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="Complete APK Analyzer with weighted scoring.")
        parser.add_argument("apk_file", help="The path to the .apk file to analyze.")
        args = parser.parse_args()
        report = analyze_apk(args.apk_file)
        print(json.dumps(report, indent=4))
    except Exception as e:
        error_report = {"confidence_score": 0, "confidence_level": "☠️ CRITICAL RISK - MALWARE LIKELY", "reasons": [{"level": "CRITICAL", "risk_type": "Analysis Error", "message": f"A critical error occurred: {str(e)}"}]}
        print(json.dumps(error_report, indent=4))