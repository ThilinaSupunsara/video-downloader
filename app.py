from flask import Flask, render_template, request, jsonify, send_file, after_this_request
import os
from backend import get_video_data, download_media

import time
import glob

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'

def cleanup_old_files():
    """ පැයකට වඩා පැරණි files මැකීම (Cleanup Function) """
    try:
        now = time.time()
        for f in glob.glob(os.path.join(DOWNLOAD_FOLDER, "*")):
            if os.path.isfile(f):
                if os.stat(f).st_mtime < now - 3600: # 3600 seconds = 1 hour
                    os.remove(f)
                    print(f"Deleted old file: {f}")
    except Exception as e:
        print(f"Cleanup error: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-info', methods=['POST'])
def get_info():
    url = request.form.get('url')
    if not url:
        return jsonify({"status": "error", "message": "Please enter a URL"})
    return jsonify(get_video_data(url))

@app.route('/download', methods=['POST'])
def download():
    # පරණ files මකන්න
    cleanup_old_files()

    url = request.form.get('url')
    format_type = request.form.get('format')
    quality = request.form.get('quality')

    if not url:
        return render_template('index.html', error="URL is missing!")

    result = download_media(url, format_type, quality)

    if result['status'] == 'success':
        file_path = result['file_path']
        
        # User ට file එක යැවූ පසු Server එකෙන් මකා දමන්න (Clean up)
        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file: {e}")
            return response

        return send_file(file_path, as_attachment=True)
    else:
        # Error එකක් ආවොත් ලස්සනට පෙන්වන්න
        return render_template('index.html', error=result['message'])

if __name__ == '__main__':
    # Docker වල වැඩ කරන්න host='0.0.0.0' අනිවාර්යයි
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000, debug=True)