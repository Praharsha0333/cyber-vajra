import os
import subprocess
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# Initialize the Flask app
app = Flask(__name__)

# Configure a folder to temporarily store uploaded APKs
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/analyze_apk', methods=['POST'])
def analyze_apk_endpoint():
    """
    This is the API endpoint that the Flutter app will call.
    It receives an APK file, saves it, runs your analysis script,
    and returns the JSON report.
    """
    # 1. Check if a file was sent in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    # 2. Save the uploaded file securely
    if file and file.filename.endswith('.apk'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # 3. Call your standalone analysis script as a command-line tool
            # This runs: python run_analysis.py /path/to/the/file.apk
            result = subprocess.run(
                ['python', 'run_analysis.py', filepath],
                capture_output=True,
                text=True,
                check=True  # This will raise an error if the script fails
            )
            
            # The output from your script is in result.stdout
            analysis_json = json.loads(result.stdout)
            
            # 4. Return the JSON report to the Flutter app
            return jsonify(analysis_json)

        except subprocess.CalledProcessError as e:
            # If your script has an error, return that error
            return jsonify({
                'error': 'Analysis script failed.',
                'details': e.stderr
            }), 500
        except json.JSONDecodeError:
            # If the script output isn't valid JSON
            return jsonify({
                'error': 'Failed to decode analysis script output.',
                'raw_output': result.stdout
            }), 500
        finally:
            # 5. Clean up by deleting the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
    else:
        return jsonify({'error': 'Invalid file type, please upload an APK'}), 400

if __name__ == '__main__':
    # This server script runs without any command-line arguments.
    app.run(host='0.0.0.0', port=5001, debug=True)
