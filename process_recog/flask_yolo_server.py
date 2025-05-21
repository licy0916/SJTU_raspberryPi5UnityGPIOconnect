from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import cv2
import numpy as np
from datetime import datetime
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === 預設原圖尺寸（未壓縮） ===
ORIGINAL_WIDTH = 640
ORIGINAL_HEIGHT = 480

# === 三個 ROI 框 ===
ROI_BOXES = [
    (313.49, 118.6349, 205.1024, 104.4),
    (342.2763, 219.4349, 176.3161, 102.6),
    (421.4387, 318.5, 97.1538, 70.1)
]

# === 載入 YOLO 模型 ===
model = YOLO("/Volumes/TU260/unity/recognization/best.pt")  # 換成你的模型路徑

@app.route("/upload_frame", methods=["POST"])
def upload_frame():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = os.path.join(UPLOAD_FOLDER, f"frame_{timestamp}.png")
    file.save(save_path)

    # === 讀取原始圖片 ===
    img = cv2.imread(save_path)
    if img is None:
        return jsonify({"error": "Image decode failed"}), 500

    h, w = img.shape[:2]
    if h != ORIGINAL_HEIGHT or w != ORIGINAL_WIDTH:
        print(f"警告：收到的圖片尺寸是 {w}x{h}，預期是 640x480")
        img = cv2.resize(img, (ORIGINAL_WIDTH, ORIGINAL_HEIGHT))
        print("已強制將圖片縮放為 640x480")


    results = []

    # === 裁切三個 ROI 並辨識 ===
    for i, (x, y, roi_w, roi_h) in enumerate(ROI_BOXES):
        x1, y1 = int(x), int(y)
        x2, y2 = int(x + roi_w), int(y + roi_h)

        roi = img[y1:y2, x1:x2]
        if roi.size == 0:
            print(f"ROI {i} 裁切失敗，範圍為 ({x1}, {y1}) ~ ({x2}, {y2})")
            results.append(0)
            continue

        # 推論
        det = model.predict(roi, imgsz=224, conf=0.25, verbose=False)

        digits = []
        for d in det[0].boxes.data.tolist():
            cls_id, conf = int(d[5]), d[4]
            digits.append(cls_id)

        if digits:
            # 對 YOLO 預測的 class 排序（你可根據 X 座標來排序）
            results.append(int("".join(str(n) for n in sorted(digits))))
        else:
            results.append(0)

    return jsonify({
        "top": results[0],
        "mid": results[1],
        "bottom": results[2]
    })

if __name__ == "__main__":
    print("📡 Flask server running on http://127.0.0.0:5050")
    app.run(host="127.0.0.0", port=5050, debug=False)
