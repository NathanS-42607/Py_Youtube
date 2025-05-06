from flask import Flask, render_template, request, jsonify
import subprocess
import os
from pathlib import Path

app = Flask(__name__)

# Default download directory
DOWNLOAD_DIR = str(Path.home() / "Downloads")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download_video', methods=['POST'])
def download_video():
    try:
        video_url = request.form.get('video_url')
        if not video_url:
            return jsonify({'error': 'No video URL provided'}), 400

        # Create download directory if it doesn't exist
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

        # Run the youtube_downloader script
        result = subprocess.run(['python3', 'youtube_downloader.py', video_url, DOWNLOAD_DIR],
                              capture_output=True,
                              text=True)

        return jsonify({
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
