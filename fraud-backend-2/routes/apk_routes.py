# routes/apk_routes.py
from flask import Blueprint, request, jsonify
from services.apk_checker import scan_apk
import os

apk_bp = Blueprint("apk_routes", __name__)

UPLOAD_DIR = "uploaded_apks"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@apk_bp.route("/check_apk", methods=["POST"])
def check_apk():
    if "apk_file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["apk_file"]
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(file_path)

    result = scan_apk(file_path)
    return jsonify(result)
