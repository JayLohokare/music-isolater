import os
import uuid
import threading
import subprocess
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Config
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
SEPARATED_FOLDER = os.path.join(os.path.dirname(__file__), 'separated')
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg', 'm4a', 'mp4', 'mov', 'avi', 'mkv'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SEPARATED_FOLDER, exist_ok=True)

# In-memory task tracker
# Format: { task_id: {"status": "processing"|"done"|"error", "files": [], "error": ""} }
TASKS = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_audio(task_id, file_path):
    print(f"[{task_id}] Starting demucs processing for {file_path}")
    TASKS[task_id]['status'] = 'processing'
    
    # Extract audio from video files using ffmpeg to prevent demucs crash
    ext = file_path.rsplit('.', 1)[1].lower()
    if ext in ['mp4', 'mov', 'avi', 'mkv']:
        print(f"[{task_id}] Extracting audio from video format: {ext}")
        audio_path = file_path.rsplit('.', 1)[0] + '.wav'
        try:
            subprocess.run(["ffmpeg", "-y", "-i", file_path, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", audio_path], check=True, capture_output=True)
            file_path = audio_path
            print(f"[{task_id}] Successfully converted video to {audio_path}")
        except subprocess.CalledProcessError as e:
            print(f"[{task_id}] FFmpeg extraction error.")
            TASKS[task_id]['status'] = 'error'
            TASKS[task_id]['error'] = "Failed to extract audio from the uploaded video file."
            return

    # htdemucs separates into 4 stems: vocals, drums, bass, other
    # Faster to process and download than the 6 stem model, perfect for a web app demo
    model = "htdemucs"
    
    command = [
        "demucs",
        "-n", model,
        "-o", SEPARATED_FOLDER,
        file_path
    ]
    
    try:
        subprocess.run(command, check=True)
        # Find the output folder
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_dir = os.path.join(SEPARATED_FOLDER, model, base_name)
        
        if os.path.exists(output_dir):
            files = [f for f in os.listdir(output_dir) if f.endswith('.wav')]
            TASKS[task_id]['files'] = files
            TASKS[task_id]['output_dir'] = output_dir
            TASKS[task_id]['status'] = 'done'
            print(f"[{task_id}] Finished processing")
        else:
            TASKS[task_id]['status'] = 'error'
            TASKS[task_id]['error'] = 'Output directory not found after processing.'
            
    except subprocess.CalledProcessError as e:
        print(f"[{task_id}] Error running demucs: {e}")
        TASKS[task_id]['status'] = 'error'
        TASKS[task_id]['error'] = str(e)
    except Exception as e:
        print(f"[{task_id}] Unexpected error: {e}")
        TASKS[task_id]['status'] = 'error'
        TASKS[task_id]['error'] = str(e)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())[:8]
        safe_filename = f"{unique_id}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        file.save(file_path)
        
        task_id = unique_id
        TASKS[task_id] = {'status': 'queued', 'files': [], 'filename': filename}
        
        # Start a background thread to process the audio
        thread = threading.Thread(target=process_audio, args=(task_id, file_path))
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Upload successful. Processing started.'})
    
    return jsonify({'error': 'Invalid file type. Supported types: mp3, wav, flac, ogg, m4a, mp4, mov, avi, mkv'}), 400

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    task = TASKS.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
        
    return jsonify({
        'status': task['status'],
        'files': task.get('files', []),
        'error': task.get('error', '')
    })

@app.route('/download/<task_id>/<filename>')
def download_file(task_id, filename):
    task = TASKS.get(task_id)
    if not task or task['status'] != 'done':
        return "Not available", 404
        
    return send_from_directory(task['output_dir'], filename, as_attachment=True)

@app.route('/listen/<task_id>/<filename>')
def listen_file(task_id, filename):
    task = TASKS.get(task_id)
    if not task or task['status'] != 'done':
        return "Not available", 404
        
    return send_from_directory(task['output_dir'], filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
