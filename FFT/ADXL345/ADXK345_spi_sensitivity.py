import spidev
import time
import csv
import struct

# ADXL345 레지스터 주소
DEVICE_ID = 0x00
OFSX = 0x1E
OFSY = 0x1F
OFSZ = 0x20
POWER_CTL = 0x2D  # Power control register
DATA_FORMAT = 0x31
BW_RATE = 0x2C  # 샘플링 속도 설정 레지스터
DATAX0 = 0x32  # X축 데이터 하위 바이트 레지스터 주소
DATAX1 = 0x33  # X축 데이터 상위 바이트 레지스터 주소
DATAY0 = 0x34  # Y축 데이터 하위 바이트 레지스터 주소
DATAY1 = 0x35  # Y축 데이터 상위 바이트 레지스터 주소
DATAZ0 = 0x36  # Z축 데이터 하위 바이트 레지스터 주소
DATAZ1 = 0x37  # Z축 데이터 상위 바이트 레지스터 주소

G = 9.81  # 지구 중력 가속도 (m/s^2)

# SPI 설정
spi = spidev.SpiDev()
spi.open(0, 0)  # SPI 버스 0, 장치 0 (CE0)
spi.max_speed_hz = 500000  # SPI 속도 설정 (500kHz)
spi.mode = 0b11  # SPI 모드 3 (CPOL=1, CPHA=1)

OUTPUT_FILE = "/home/mango/workspace/FFT_stream/test/data_log_1.csv"

def setup(START_TIME):
    # 센서 초기화
    print("초기화 중...")

    # CSV 파일 초기화
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time (s)", "X (m/s^2)", "Y (m/s^2)", "Z (m/s^2)"])

    # OFFSET 설정
    spi.xfer2([OFSX, 10])  # X축 보정 1
    time.sleep(0.1)
    spi.xfer2([OFSY, 75])  # Y축 보정 75
    time.sleep(0.1)
    spi.xfer2([OFSZ, -3])  # Z축 보정 -5
    time.sleep(0.1)
    
    # ±2g 모드 설정 (Data Format register)
    spi.xfer2([DATA_FORMAT, 0x00])  # ±2g (0x00) 설정
    time.sleep(0.1)
    
    # 샘플링 속도 설정 (800Hz)
    spi.xfer2([BW_RATE, 0x0D])  # 800Hz
    time.sleep(0.1)

    # ADXL345을 측정 모드로 설정
    spi.xfer2([POWER_CTL, 0x08])  # 측정 모드 활성화
    time.sleep(0.1)

    print("초기화 완료!")

    return START_TIME

def read_acceleration(START_TIME):
    CURRENT_TIME = time.time()
    TIMESTAMP = CURRENT_TIME - START_TIME

    # 각 축의 LSB와 MSB 값을 개별적으로 읽음
    X_LSB = spi.xfer2([DATAX0 | 0x80, 0x00])
    X_MSB = spi.xfer2([DATAX1 | 0x80, 0x00])
    Y_LSB = spi.xfer2([DATAY0 | 0x80, 0x00])
    Y_MSB = spi.xfer2([DATAY1 | 0x80, 0x00])
    Z_LSB = spi.xfer2([DATAZ0 | 0x80, 0x00])
    Z_MSB = spi.xfer2([DATAZ1 | 0x80, 0x00])

    # LSB와 MSB 결합
    X_RAW = (X_MSB[1] << 8) | X_LSB[1]
    Y_RAW = (Y_MSB[1] << 8) | Y_LSB[1]
    Z_RAW = (Z_MSB[1] << 8) | Z_LSB[1]

    # 하위 6비트 제거 및 정수 변환
    X_RAW = X_RAW >> 6
    Y_RAW = Y_RAW >> 6
    Z_RAW = Z_RAW >> 6

    print(f"Raw Data 1 - X: {X_RAW}, Y: {Y_RAW}, Z: {Z_RAW}")

    # 2의 보수 변환 (10비트 음수 처리)
    if X_RAW & (1 << 9):  
        X_RAW -= 1024
    if Y_RAW & (1 << 9):  
        Y_RAW -= 1024
    if Z_RAW & (1 << 9):  
        Z_RAW -= 1024

    print(f"Raw Data 2 - X: {X_RAW}, Y: {Y_RAW}, Z: {Z_RAW}")

    # ±2g 모드에서 g 단위 변환
    g_X = X_RAW / 256
    g_Y = Y_RAW / 256
    g_Z = Z_RAW / 256

    print(f"{TIMESTAMP:.4f} s - X: {g_X:.4f} g, Y: {g_Y:.4f} g, Z: {g_Z:.4f} g")

    # ±2g 모드에서 m/s^2 단위 변환
    g_X1 = g_X * G #* 9
    g_Y1 = g_Y* G #* 9
    g_Z1 = g_Z * G #* 9

    # CSV 파일에 데이터 저장
    with open(OUTPUT_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([TIMESTAMP, g_X1, g_Y1, g_Z1])

    # 결과 출력
    print(f"{TIMESTAMP:.4f} s - X: {g_X1:.4f} m/s^2, Y: {g_Y1:.4f} m/s^2, Z: {g_Z1:.4f} m/s^2")

    return g_X, g_Y, g_Z

def main():
    # 타임스탬프 시작
    START_TIME = time.time()

    setup(START_TIME)  # 센서 초기화 함수 호출

    while True:
        read_acceleration(START_TIME)  # 가속도 측정
        time.sleep(0.001)

if __name__ == "__main__":
    main()
