# analyzers/apk_metadata_extractor.py
from androguard.core.bytecodes.apk import APK
import hashlib

def extract_metadata(filepath):
    """
    Extracts key metadata from an APK file.
    """
    try:
        # Androguard APK object
        apk = APK(filepath)

        # Calculate file hashes
        with open(filepath, 'rb') as f:
            file_bytes = f.read()
            md5_hash = hashlib.md5(file_bytes).hexdigest()
            sha256_hash = hashlib.sha256(file_bytes).hexdigest()

        metadata = {
            'file_path': filepath,
            'app_name': apk.get_app_name(),
            'package_name': apk.get_package(),
            'version_code': apk.get_androidversion_code(),
            'version_name': apk.get_androidversion_name(),
            'permissions': apk.get_permissions(),
            'hashes': {
                'md5': md5_hash,
                'sha256': sha256_hash
            }
        }
        return metadata
    except Exception as e:
        # Return an error dictionary if analysis fails
        return {'error': f"Could not extract metadata: {e}"}
