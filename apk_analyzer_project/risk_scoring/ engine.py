# risk_scoring/engine.py

def calculate_risk_score(analysis_results):
    """
    Calculates a risk score based on analysis results using a rule-based engine.
    Score ranges from 0 (Safe) to 100 (Critical).
    """
    score = 0
    reasons = []

    # Rule 1: Dangerous Permissions (High Impact)
    perm_analysis = analysis_results.get('permission_analysis', {})
    if not perm_analysis.get('error'):
        dangerous_count = perm_analysis.get('count', 0)
        if dangerous_count > 3:
            score += 30
            reasons.append(f"High Risk: App requests {dangerous_count} dangerous permissions (e.g., Read SMS, Access Location).")
        elif dangerous_count > 0:
            score += 15
            reasons.append(f"Medium Risk: App requests {dangerous_count} dangerous permissions.")

    # Rule 2: Suspicious Keywords (Medium Impact)
    string_analysis = analysis_results.get('string_analysis', {})
    if not string_analysis.get('error'):
        keyword_count = sum(string_analysis.get('suspicious_keywords', {}).values())
        if keyword_count > 10:
            score += 25
            reasons.append(f"Warning: Found {keyword_count} instances of suspicious keywords (e.g., 'password', 'bank', 'login').")
        elif keyword_count > 0:
            score += 10
            reasons.append(f"Info: Found {keyword_count} instances of suspicious keywords.")

    # Rule 3: High number of URLs (Low Impact)
    if not string_analysis.get('error'):
        url_count = len(string_analysis.get('urls_found', []))
        if url_count > 50: # A very high number of embedded URLs can be suspicious
            score += 15
            reasons.append(f"Info: A large number of URLs ({url_count}) were found embedded in the app.")

    # --- Placeholder for Future ML Model Integration ---
    # You can add a call to your trained machine learning model here.
    # For example:
    # ml_prediction = your_ml_model.predict(features_from_analysis)
    # if ml_prediction == 'malware':
    #     score += 40
    #     reasons.append("AI/ML model has classified this app as potential malware.")
    
    # Cap the score at 100
    final_score = min(score, 100)
    
    if not reasons:
        reasons.append("This app appears to be safe based on our static analysis.")

    return final_score, reasons
