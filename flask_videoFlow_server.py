from flask import Flask, Response, jsonify, request
import cv2
import pytesseract
import threading
import time
import subprocess
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

frame_lock = threading.Lock()
latest_frame = None

def camera_reader():
    global latest_frame
    cmd = [
        "libcamera-vid",
        "--codec", "yuv420",
        "--width", "640",
        "--height", "480",
        "--framerate", "30",
        "--inline",
        "--timeout", "0",
        "--brightness", "0.25",
        "--output", "-",
        "--split", "1"
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    frame_size = 640 * 480 * 3 // 2  # YUV420: 1.5 bytes per pixel

    while True:
        raw_frame = process.stdout.read(frame_size)
        if len(raw_frame) != frame_size:
            print("[Reader] Incomplete YUV frame")
            continue
        yuv = np.frombuffer(raw_frame, dtype=np.uint8).reshape((int(480 * 1.5), 640))
        try:
            bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)
        except Exception as e:
            print("[Reader] cvtColor error:", e)
            continue
        with frame_lock:
            latest_frame = bgr
        time.sleep(0.033)

def generate_stream():
    global latest_frame
    while True:
        with frame_lock:
            if latest_frame is None:
                time.sleep(0.1)
                continue
            ret, jpeg = cv2.imencode('.jpg', latest_frame)
        if not ret:
            continue
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return "✅ Camera server is running with libcamera YUV420. Access /video_feed or POST to /capture"

@app.route('/video_feed')
def video_feed():
    return Response(generate_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/frame.jpg')
def frame():
    global latest_frame
    with frame_lock:
        if latest_frame is None:
            return "No frame available", 503
        ret, jpeg = cv2.imencode('.jpg', latest_frame)
        if not ret:
            return "JPEG encode error", 500
        return Response(jpeg.tobytes(), mimetype='image/jpeg')

@app.route('/capture', methods=['POST'])
def capture():
    global latest_frame
    with frame_lock:
        if latest_frame is None:
            return jsonify({"error": "No frame available"}), 500
        text = pytesseract.image_to_string(latest_frame)
    return jsonify({"text": text.strip()})

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


if __name__ == '__main__':
    print("[Server] Starting libcamera YUV420-based camera reader thread...")
    threading.Thread(target=camera_reader, daemon=True).start()
    print("[Server] Starting Flask server on port 5000")
    app.run(host='0.0.0.0', port=5000)
