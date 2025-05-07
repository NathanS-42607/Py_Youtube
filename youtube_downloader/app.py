from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO, emit
import threading
import os
import yt_dlp
from youtube_downloader import progress_hook

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

class DownloadThread(threading.Thread):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.progress = 0
        self.status = "idle"
        self.error = None
        self.video_path = None

    def run(self):
        try:
            self.status = "downloading"
            # Get the downloads directory path relative to app.py
            downloads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'downloads')
            os.makedirs(downloads_dir, exist_ok=True)
            
            # Create yt-dlp options
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'retries': 10,
                'fragment_retries': 10,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
                
            # Get the most recently modified file in the downloads directory
            files = os.listdir(downloads_dir)
            if files:
                self.video_path = os.path.join('static', 'downloads', max(files, key=lambda x: os.path.getmtime(os.path.join(downloads_dir, x))))
            self.status = "completed"
        except Exception as e:
            self.status = "error"
            self.error = str(e)
        finally:
            socketio.emit('download_status', {
                'status': self.status,
                'error': self.error,
                'video_path': self.video_path
            })

@app.route('/')
def index():
    downloads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'downloads')
    os.makedirs(downloads_dir, exist_ok=True)
    
    # Get list of downloaded videos
    videos = []
    if os.path.exists(downloads_dir):
        for file in os.listdir(downloads_dir):
            if file.lower().endswith(('.mp4', '.webm')):
                # Store relative path for template and absolute path for download
                video_path = os.path.join('static', 'downloads', file)
                absolute_path = os.path.join(downloads_dir, file)
                file_size = os.path.getsize(absolute_path)
                videos.append({
                    'name': file,
                    'path': video_path,
                    'size': f"{file_size / (1024*1024):.2f} MB",
                    'absolute_path': absolute_path
                })
    
    return render_template('index.html', videos=videos)



@app.route('/download/<path:filename>')
def download_video(filename):
    try:
        # Get the absolute path from the filename
        downloads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'downloads')
        absolute_path = os.path.join(downloads_dir, filename)
        
        if not os.path.exists(absolute_path):
            return "File not found", 404
            
        return send_file(absolute_path, as_attachment=True)
    except Exception as e:
        return f"Error downloading video: {str(e)}"

@socketio.on('start_download')
def handle_start_download(data):
    url = data.get('url')
    if not url:
        emit('download_status', {'status': 'error', 'error': 'No URL provided'})
        return

    # Start download in a separate thread
    download_thread = DownloadThread(url)
    download_thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True)
