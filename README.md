# SJTU_raspberryPi5UnityGPIOconnect
上海交通大學信息交互設計課程，2025春季學期，第一組樹莓派課程資料
  
  
  
## 檔案功能簡介：

### 【run_all.sh】
開啟process_recog、gpio_server.py、flask_videoFlow_server.py三個檔案（開機後自動運行）

### 【gpio_server.py】
將樹莓派接收到的GPIO訊號（四顆按鍵、Joystick、TCS34725）經過基礎處理後，創建 websocket server，讓 unity webGL 遊戲即時接收訊號狀態。

### 【flask_videoFlow_server.py】
因unity webGL不能直接存取樹莓派相機，故將樹莓派原生支持的CSI相機，透過flask server的方式傳送相機畫面給遊戲。

### 【process_recog】
接收遊戲在按下拍攝鍵後回傳的圖片資料，並切分成三張小圖，透過yolo訓練出的模型對三張小圖上的數字進行辨識，辨識完成後回傳給unity遊戲。
