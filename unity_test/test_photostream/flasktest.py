# fake_webcam.py
from flask import Flask, Response
from flask_cors import CORS

import cv2

app = Flask(__name__)
CORS(app)
img = cv2.imread("/Users/licydoong/Desktop/unity/test_photostream/test_photo.jpg")  # 放一張測試圖

@app.route("/frame.jpg")
def frame():
    ret, jpeg = cv2.imencode('.jpg', img)
    return Response(jpeg.tobytes(), mimetype='image/jpeg')

if __name__ == "__main__":
    print("Serving on http://127.0.0.1:5000/frame.jpg")
    app.run(port=5000)
