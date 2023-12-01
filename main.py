from flask import Flask, render_template, Response, request, send_from_directory
import subprocess
import os
from flask_cors import CORS



app = Flask(__name__)

CORS(app)

# Directory to store segmented video files
VIDEO_DIR = "videos"

# Directory to store HLS files
HLS_DIR = "hls"

# Path to the FFmpeg executable
FFMPEG_PATH = "ffmpeg"

# Create directories if they don't exist
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(HLS_DIR, exist_ok=True)


@app.route('/')
def index():
    videos_dir = VIDEO_DIR
    video_files = [f for f in os.listdir(videos_dir)]

    return render_template('index.html', video_files=video_files)

@app.route("/upload", methods=["GET", "POST"])
def upload_video():
    if request.method == "POST":
        # Handle video upload and segment it using FFmpeg
        video_file = request.files["file"]
        video_path = os.path.join(VIDEO_DIR, video_file.filename)
        video_file.save(video_path)

        hls_path = os.path.join(HLS_DIR, f'{video_file.filename.split(".")[0]}.m3u8')
        subprocess.run(
            f'{FFMPEG_PATH} -i {video_path} -hls_time 10 -hls_list_size 0 -c:v h264 -flags +cgop -g 30 -sc_threshold 0 -f hls {hls_path}',
            shell=True
        )

        return "Video uploaded and segmented successfully"

    return render_template("upload.html")


@app.route('/video/<filename>')
def video(filename):
    video_path = os.path.join(VIDEO_DIR, filename)
    if not os.path.exists(video_path):
        return 'File not found', 404
    
    return render_template('video.html',mimetype='video/mp4', hls_path= (f'/hls/{filename.split(".")[0]}.m3u8'))


@app.route("/hls/<path:filename>")
def hls_files(filename):
    # Serve HLS files
    return send_from_directory(HLS_DIR, filename)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
