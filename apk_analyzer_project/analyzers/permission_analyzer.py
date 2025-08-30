# analyzers/permission_analyzer.py

# A set of permissions often considered dangerous or high-risk
DANGEROUS_PERMISSIONS = {
    "android.permission.READ_SMS",
    "android.permission.SEND_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS",
    "android.permission.READ_CALL_LOG",
    "android.permission.WRITE_CALL_LOG",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.RECORD_AUDIO",
    "android.permission.CAMERA",
    "android.permission.INSTALL_PACKAGES",
    "android.permission.SYSTEM_ALERT_WINDOW",
    "android.permission.BIND_DEVICE_ADMIN"
}

def analyze_permissions(permissions_list):
    """
    Analyzes the list of permissions and flags dangerous ones.
    """
    if not isinstance(permissions_list, list):
        return {
            'error': 'Invalid input: permissions_list must be a list.'
        }
        
    found_dangerous = []
    for perm in permissions_list:
        if perm in DANGEROUS_PERMISSIONS:
            found_dangerous.append(perm)
            
    return {
        'dangerous_permissions_found': found_dangerous,
        'count': len(found_dangerous)
    }
