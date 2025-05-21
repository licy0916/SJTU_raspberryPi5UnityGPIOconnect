import asyncio, json
import websockets
import spidev
from gpiozero import Button
import board
import busio
import adafruit_tcs34725
import datetime


# === 初始化 SPI ADC ===
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

def read_adc(channel):
    assert 0 <= channel <= 7
    r = spi.xfer2([1, (8 + channel) << 4, 0])
    val = ((r[1] & 3) << 8) + r[2]
    return val

# === 初始化 GPIO 按鈕 ===
sw_button = Button(4)
button_pins = [22, 23, 24, 25]
buttons = [Button(pin) for pin in button_pins]

# === 初始化 色彩感測器 ===
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_tcs34725.TCS34725(i2c)

# === 搖桿方向判斷 ===
def get_joystick_direction(x, y):
    left = x <= 100
    right = x >= 923
    up = y <= 100
    down = y >= 923

    if up and left:
        return "js_upleft"
    elif up and right:
        return "js_upright"
    elif down and left:
        return "js_downleft"
    elif down and right:
        return "js_downright"
    elif up:
        return "js_up"
    elif down:
        return "js_down"
    elif left:
        return "js_left"
    elif right:
        return "js_right"
    else:
        return "js_still"

async def send_data(websocket):
    print("WebSocket client connected.")
    try:
        while True:
            # 讀取四顆按鈕的狀態
            button_states = [int(b.is_pressed) for b in buttons]

            # 讀取 Joystick 類比值與方向
            x = read_adc(0)
            y = read_adc(1)
            js_dir = get_joystick_direction(x, y)

            # 讀取 Joystick 按鈕（Switch）
            js_switch = int(sw_button.is_pressed)

            # 讀取色彩感測器
            r, g, b = sensor.color_rgb_bytes

            # 打包傳送資料
            payload = {
                "buttons": button_states,
                "joystick": [x, y],
                "joystick_button": js_dir,
                "joystick_switch": js_switch,
                "color": [r, g, b]
            }

            json_payload = json.dumps(payload)
            await websocket.send(json_payload)

            print(f"{datetime.datetime.now().isoformat()} Sent:")
            print(f"  Buttons: {button_states}")
            print(f"  Joystick: x={x}, y={y}, direction={js_dir}, switch={js_switch}")
            print(f"  Color: R={r} G={g} B={b}")
            print("-" * 60)

            await asyncio.sleep(0.1)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected.")
    finally:
        spi.close()


# 啟動 WebSocket Server
async def main():
    print("WebSocket server running at ws://0.0.0.0:8765/")
    async with websockets.serve(send_data, "0.0.0.0", 8765):
        await asyncio.Future()

asyncio.run(main())
