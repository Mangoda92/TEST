import spidev
import time
import socket
import struct  # 바이너리 변환을 위한 모듈

# SPI 초기화
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 5000000  # 5MHz
spi.mode = 0b11  # CPOL=1, CPHA=1

# ADXL345 레지스터 주소
POWER_CTL = 0x2D
DATA_FORMAT = 0x31
BW_RATE = 0x2C
DATAX0 = 0x32
DATAX1 = 0x33
DATAY0 = 0x34
DATAY1 = 0x35
DATAZ0 = 0x36
DATAZ1 = 0x37

# 센서 초기화
spi.xfer2([POWER_CTL, 0x08])  # 측정 모드 활성화
spi.xfer2([DATA_FORMAT, 0x0B])  # ±16g 모드, FULL_RES
spi.xfer2([BW_RATE, 0x0A])  # 1600Hz 샘플링 속도 설정

# TCP 서버 설정
TCP_IP = "192.168.75.19"
TCP_PORT = 5005
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((TCP_IP, TCP_PORT))
server_socket.listen(1)
print(f"Listening on {TCP_IP}:{TCP_PORT}...")

conn, addr = server_socket.accept()
print(f"Connection from: {addr}")

# 오프셋 보정
SAMPLES = 100
X_OFFSET, Y_OFFSET, Z_OFFSET = 0, 0, 0

print(f"Calibrating offset using {SAMPLES} samples...")
for _ in range(SAMPLES):
    X_LSB = spi.xfer2([DATAX0 | 0x80, 0x00])
    X_MSB = spi.xfer2([DATAX1 | 0x80, 0x00])
    Y_LSB = spi.xfer2([DATAY0 | 0x80, 0x00])
    Y_MSB = spi.xfer2([DATAY1 | 0x80, 0x00])
    Z_LSB = spi.xfer2([DATAZ0 | 0x80, 0x00])
    Z_MSB = spi.xfer2([DATAZ1 | 0x80, 0x00])

    X_RAW = (X_MSB[1] << 8) | X_LSB[1]
    Y_RAW = (Y_MSB[1] << 8) | Y_LSB[1]
    Z_RAW = (Z_MSB[1] << 8) | Z_LSB[1]

    if X_RAW > 4095: X_RAW -= 8192
    if Y_RAW > 4095: Y_RAW -= 8192
    if Z_RAW > 4095: Z_RAW -= 8192

    X_OFFSET += X_RAW
    Y_OFFSET += Y_RAW
    Z_OFFSET += Z_RAW

    time.sleep(0.001)

X_OFFSET //= SAMPLES
Y_OFFSET //= SAMPLES
Z_OFFSET //= SAMPLES

print(f"Calibration complete: X_OFFSET={X_OFFSET}, Y_OFFSET={Y_OFFSET}, Z_OFFSET={Z_OFFSET}")

START_TIME = time.time()
fs = 1  # 1Hz 샘플링

while True:
    try:
        CURRENT_TIME = time.time()
        TIMESTAMP = CURRENT_TIME - START_TIME

        X_LSB = spi.xfer2([DATAX0 | 0x80, 0x00])
        X_MSB = spi.xfer2([DATAX1 | 0x80, 0x00])
        Y_LSB = spi.xfer2([DATAY0 | 0x80, 0x00])
        Y_MSB = spi.xfer2([DATAY1 | 0x80, 0x00])
        Z_LSB = spi.xfer2([DATAZ0 | 0x80, 0x00])
        Z_MSB = spi.xfer2([DATAZ1 | 0x80, 0x00])

        X_RAW = (X_MSB[1] << 8) | X_LSB[1]
        Y_RAW = (Y_MSB[1] << 8) | Y_LSB[1]
        Z_RAW = (Z_MSB[1] << 8) | Z_LSB[1]

        if X_RAW > 4095: X_RAW -= 8192
        if Y_RAW > 4095: Y_RAW -= 8192
        if Z_RAW > 4095: Z_RAW -= 8192

        X_RAW -= X_OFFSET
        Y_RAW -= Y_OFFSET
        Z_RAW -= Z_OFFSET

        X_MG = X_RAW * 4
        Y_MG = Y_RAW * 4
        Z_MG = Z_RAW * 4

        # 바이너리 변환 및 전송 (float 4개 = 16 bytes)
        binary_data = struct.pack('<ffff', TIMESTAMP, X_MG, Y_MG, Z_MG)
        conn.send(binary_data)

        print(f"Time: {TIMESTAMP:.4f} s - X: {X_MG} mg, Y: {Y_MG} mg, Z: {Z_MG} mg")

        time.sleep(1 / fs)

    except BrokenPipeError:
        print("Client disconnected. Waiting for new connection...")
        conn.close()
        conn, addr = server_socket.accept()
        print(f"New connection from: {addr}")

conn.close()
spi.close()
