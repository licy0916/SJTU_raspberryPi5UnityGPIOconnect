#!/bin/bash

TERMINAL=lxterminal  # ✅ 若不是 Pi OS 可改 gnome-terminal 或 x-terminal-emulator

# Camera Server（5000）
$TERMINAL -e "bash -c 'source /home/user/myenv/bin/activate && cd /home/user/Desktop/unity && python3 flask_camera_server.py; exec bash'" &

# YOLO Server（5050）
$TERMINAL -e "bash -c 'source /home/user/myenv/bin/activate && cd /home/user/Desktop/unity && python3 flask_yolo_server.py; exec bash'" &

# 其他你未來要加的服務（先預留）
#$TERMINAL -e "bash -c 'source /home/user/myenv/bin/activate && cd /home/user/Desktop/unity && python3 other_server.py; exec bash'" &
#給權限chmod +x /home/user/Desktop/unity/run_all_servers.sh


echo \"🚀 所有伺服器已啟動，請確認終端機視窗。已啟用虛擬環境 myenv\"
