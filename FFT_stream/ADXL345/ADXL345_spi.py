import spidev
import time
import csv
import struct

# SPI 초기화
spi = spidev.SpiDev()
spi.open(0, 0)  # SPI0, CE0 사용
spi.max_speed_hz = 5000000  # 5MHz
spi.mode = 0b11  # CPOL=1, CPHA=1 (ADXL345에 맞게 설정)



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

# CSV 파일 초기화
OUTPUT_FILE = "/home/mango/workspace/FFT/log/adxl345_spi_data_0.csv"
with open(OUTPUT_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Time (s)", "X (mg)", "Y (mg)", "Z (mg)"])

# 센서 초기화 (측정 모드 활성화)
spi.xfer2([POWER_CTL, 0x08])  # 측정 모드 활성화
spi.xfer2([DATA_FORMAT, 0x0B])  # ±16g 모드, FULL_RES
#spi.xfer2([BW_RATE, 0x0F])  # 3200Hz 샘플링 속도 설정
spi.xfer2([BW_RATE, 0x0A])  # 1600Hz 샘플링 속도 설정

# 초기 오프셋 계산 (평균 샘플링)
SAMPLES = 100
X_OFFSET = 0
Y_OFFSET = 0
Z_OFFSET = 0

print(f"Calibrating offset using {SAMPLES} samples...")
for i in range(SAMPLES):
    # X, Y, Z 데이터 읽기
    X_LSB = spi.xfer2([DATAX0 | 0x80, 0x00])  # X축 하위 바이트 (DATAX0)
    X_MSB = spi.xfer2([DATAX1 | 0x80, 0x00])  # X축 상위 바이트 (DATAX1)
    Y_LSB = spi.xfer2([DATAY0 | 0x80, 0x00])  # Y축 하위 바이트 (DATAY0)
    Y_MSB = spi.xfer2([DATAY1 | 0x80, 0x00])  # Y축 상위 바이트 (DATAY1)
    Z_LSB = spi.xfer2([DATAZ0 | 0x80, 0x00])  # Z축 하위 바이트 (DATAZ0)
    Z_MSB = spi.xfer2([DATAZ1 | 0x80, 0x00])  # Z축 상위 바이트 (DATAZ1)

    # 데이터 결합 (16비트 signed 값)
    X_RAW = (X_MSB[1] << 8) | X_LSB[1]  # X축 데이터 결합
    Y_RAW = (Y_MSB[1] << 8) | Y_LSB[1]  # Y축 데이터 결합
    Z_RAW = (Z_MSB[1] << 8) | Z_LSB[1]  # Z축 데이터 결합

    # X, Y, Z 데이터를 13비트로 축소 (상위 3비트 제거)
    X_RAW &= 0x1FFF  # 13비트로 자르기
    Y_RAW &= 0x1FFF  # 13비트로 자르기
    Z_RAW &= 0x1FFF  # 13비트로 자르기

    # 부호 있는 13비트 값으로 조정
    if X_RAW > 4095: X_RAW -= 8192  # 13비트 부호 있는 값으로 변환
    if Y_RAW > 4095: Y_RAW -= 8192  # 13비트 부호 있는 값으로 변환
    if Z_RAW > 4095: Z_RAW -= 8192  # 13비트 부호 있는 값으로 변환

    # 16비트 부호 있는 값 처리
    #if X_RAW > 32767: X_RAW -= 65536
    #if Y_RAW > 32767: Y_RAW -= 65536
    #if Z_RAW > 32767: Z_RAW -= 65536

    # 오프셋 누적
    X_OFFSET += X_RAW
    Y_OFFSET += Y_RAW
    Z_OFFSET += Z_RAW

    time.sleep(0.1)  # 100ms 대기

# 평균 오프셋 계산
X_OFFSET //= SAMPLES
Y_OFFSET //= SAMPLES
Z_OFFSET //= SAMPLES

print(f"Calibration complete: X_OFFSET={X_OFFSET}, Y_OFFSET={Y_OFFSET}, Z_OFFSET={Z_OFFSET}")

# 타임스탬프 시작
START_TIME = time.time()

# 데이터 수집 루프
while True:
    CURRENT_TIME = time.time()
    TIMESTAMP = CURRENT_TIME - START_TIME

    # X, Y, Z 데이터 읽기
    X_LSB = spi.xfer2([DATAX0 | 0x80, 0x00])  # X축 하위 바이트 (DATAX0)
    X_MSB = spi.xfer2([DATAX1 | 0x80, 0x00])  # X축 상위 바이트 (DATAX1)
    Y_LSB = spi.xfer2([DATAY0 | 0x80, 0x00])  # Y축 하위 바이트 (DATAY0)
    Y_MSB = spi.xfer2([DATAY1 | 0x80, 0x00])  # Y축 상위 바이트 (DATAY1)
    Z_LSB = spi.xfer2([DATAZ0 | 0x80, 0x00])  # Z축 하위 바이트 (DATAZ0)
    Z_MSB = spi.xfer2([DATAZ1 | 0x80, 0x00])  # Z축 상위 바이트 (DATAZ1)

    # 데이터 결합 (16비트 signed 값)
    X_RAW = (X_MSB[1] << 8) | X_LSB[1]  # X축 데이터 결합
    Y_RAW = (Y_MSB[1] << 8) | Y_LSB[1]  # Y축 데이터 결합
    Z_RAW = (Z_MSB[1] << 8) | Z_LSB[1]  # Z축 데이터 결합

    # X, Y, Z 데이터를 13비트로 축소 (상위 3비트 제거)
    X_RAW &= 0x1FFF  # 13비트로 자르기
    Y_RAW &= 0x1FFF  # 13비트로 자르기
    Z_RAW &= 0x1FFF  # 13비트로 자르기

    # 부호 있는 13비트 값으로 조정
    if X_RAW > 4095: X_RAW -= 8192  # 13비트 부호 있는 값으로 변환
    if Y_RAW > 4095: Y_RAW -= 8192  # 13비트 부호 있는 값으로 변환
    if Z_RAW > 4095: Z_RAW -= 8192  # 13비트 부호 있는 값으로 변환

    # 16비트 부호 있는 값 처리
    #if X_RAW > 32767: X_RAW -= 65536
    #if Y_RAW > 32767: Y_RAW -= 65536
    #if Z_RAW > 32767: Z_RAW -= 65536

    # 오프셋 적용
    X_RAW -= X_OFFSET
    Y_RAW -= Y_OFFSET
    Z_RAW -= Z_OFFSET

    # mg 단위로 변환 (16g 모드, 4mg/LSB)
    X_MG = X_RAW * 4
    Y_MG = Y_RAW * 4
    Z_MG = Z_RAW * 4

    # CSV 파일에 데이터 저장
    with open(OUTPUT_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([TIMESTAMP, X_MG, Y_MG, Z_MG])

    # 출력
    print(f"{TIMESTAMP:.4f} s - X: {X_MG} um/s^2, Y: {Y_MG} um/s^2, Z: {Z_MG} um/s^2")

    # 0.1초 대기 (100ms 샘플링 간격)
    time.sleep(0.0003)

# SPI 종료
spi.close()
