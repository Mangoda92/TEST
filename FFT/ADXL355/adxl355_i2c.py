import smbus
import time
import csv
import struct

# Addresses
Status = 0x04
XDATA3 = 0x08
XDATA2 = 0x09
XDATA1 = 0x0A
YDATA3 = 0x0B
YDATA2 = 0x0C
YDATA1 = 0x0D
ZDATA3 = 0x0E
ZDATA2 = 0x0F
ZDATA1 = 0x10
INT_MAP = 0x2A
RANGE = 0x2C
POWER_CTL = 0x2D
FILTER = 0x28

# Data Range
RANGE_2G = 0x1
RANGE_4G = 0x2
RANGE_8G = 0x3

# offset
OFFSET_X_H = 0x1E
OFFSET_X_L = 0x1F
OFFSET_Y_H = 0x20
OFFSET_Y_L = 0x21
OFFSET_Z_H = 0x22
OFFSET_Z_L = 0x23

# sampling & LPF
## 100 kHz: 최대 ODR 200 Hz
## 400 kHz: 최대 ODR 800 Hz
## 1 MHz: 최대 ODR 1.6 kHz
## 3.4 MHz: 최대 ODR 5.6 kHz
LOWPASS_FILTER_MASK = 0x0F
ODR4000_LPF1000 = 0b0000
ODR2000_LPF500 = 0b0001
ODR1000_LPF250 = 0b0010
ODR500_LPF125 = 0b0011
ODR250_LPF62_5 = 0b0100
ODR125_LPF31_25 = 0b0101
ODR61_5_LPF15_625 = 0b0110
ODR31_25_LPF7_813 = 0b0111
ODR15_625_LPF3_906 = 0b1000
ODR7_813_LPF1_953 = 0b1001
ODR3_906_LPF0_977 = 0b1010

# Values
READ_BIT = 0x01
WRITE_BIT = 0x00
DUMMY_BYTE = 0xAA
MEASURE_MODE = 0x06  # Only accelerometer

# 지구 중력 가속도 (m/s^2)
G = 9.81 

# I2C 설정
bus = smbus.SMBus(1)  # Raspberry Pi의 I2C bus 1 사용
DEVICE_ADDR = 0x53  # ADXL345 기본 I2C 주소

OUTPUT_FILE = "/home/mango/workspace/FFT/adxl355/log/test.csv"

def setup(START_TIME):
    # 센서 초기화
    print("초기화 중...")

    # CSV 파일 초기화
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time (s)", "X (m/s^2)", "Y (m/s^2)", "Z (m/s^2)"])

    # 옵셋 설정
    bus.write_byte_data(DEVICE_ADDR, POWER_CTL, 0x1)  # 측정 모드 활성화
    time.sleep(0.5)

    set_offset(65448, 50137, 5407)  # Raw Data 1 >> 4
    time.sleep(0.5)
    a1 = bus.read_byte_data(DEVICE_ADDR, OFFSET_X_H)
    #print(f"OFFSET_X_H : {hex(a1)}")
    a1 = bus.read_byte_data(DEVICE_ADDR, OFFSET_X_L)
    #print(f"OFFSET_X_L : {hex(a1)}")
    a1 = bus.read_byte_data(DEVICE_ADDR, OFFSET_Y_H)
    #print(f"OFFSET_Y_H : {hex(a1)}")
    a1 = bus.read_byte_data(DEVICE_ADDR, OFFSET_Y_L)
    #print(f"OFFSET_Y_L : {hex(a1)}")
    a1 = bus.read_byte_data(DEVICE_ADDR, OFFSET_Z_H)
    #print(f"OFFSET_Z_H : {hex(a1)}")
    a1 = bus.read_byte_data(DEVICE_ADDR, OFFSET_Z_L)
    #print(f"OFFSET_Z_L : {hex(a1)}")

    # 인터럽트트 설정
    bus.write_byte_data(DEVICE_ADDR, INT_MAP, 0x0)  # ±2g 설정
    time.sleep(0.5)
    a1 = bus.read_byte_data(DEVICE_ADDR, INT_MAP)
    print(f"INT_MAP : {hex(a1)}")

    # 가속도 측정 범위 설정
    bus.write_byte_data(DEVICE_ADDR, RANGE, RANGE_2G)  # ±2g 설정
    time.sleep(0.5)
    a1 = bus.read_byte_data(DEVICE_ADDR, RANGE)
    print(f"RANGE : {hex(a1)}")

    # 샘플링 속도 & LPF 설정 //HPF 비활성화
    bus.write_byte_data(DEVICE_ADDR, FILTER, ODR125_LPF31_25)  # ODR : 1000Hz, LPF : 250Hz
    time.sleep(0.5)
    a1 = bus.read_byte_data(DEVICE_ADDR, FILTER)
    print(f"FILTER : {bin(a1)}")

    # ADXL345을 측정 모드로 설정
    bus.write_byte_data(DEVICE_ADDR, POWER_CTL, 0x6)  # 측정 모드 활성화
    time.sleep(0.5)
    a1 = bus.read_byte_data(DEVICE_ADDR, POWER_CTL)
    print(f"POWER_CTL : {hex(a1)}")

    print("초기화 완료!")

    return START_TIME

def set_offset(offset_x, offset_y, offset_z):
    """ 센서의 X, Y, Z 옵셋을 설정하는 함수 """
    
    # X축 옵셋
    bus.write_byte_data(DEVICE_ADDR, OFFSET_X_H, (offset_x >> 8) & 0xFF)  # X 상위 8비트
    time.sleep(0.1)
    bus.write_byte_data(DEVICE_ADDR, OFFSET_X_L, offset_x & 0xFF)  # X 하위 8비트
    time.sleep(0.1)

    # Y축 옵셋
    bus.write_byte_data(DEVICE_ADDR, OFFSET_Y_H, (offset_y >> 8) & 0xFF)  # Y 상위 8비트
    time.sleep(0.1)
    bus.write_byte_data(DEVICE_ADDR, OFFSET_Y_L, offset_y & 0xFF)  # Y 하위 8비트
    time.sleep(0.1)

    # Z축 옵셋
    bus.write_byte_data(DEVICE_ADDR, OFFSET_Z_H, (offset_z >> 8) & 0xFF)  # Z 상위 8비트
    time.sleep(0.1)
    bus.write_byte_data(DEVICE_ADDR, OFFSET_Z_L, offset_z & 0xFF)  # Z 하위 8비트
    time.sleep(0.1)

def read_acceleration(START_TIME):
    CURRENT_TIME = time.time()
    TIMESTAMP = CURRENT_TIME - START_TIME

    # 각 축의 RAW 값을 개별적으로 읽음

    X_RAW_H = bus.read_byte_data(DEVICE_ADDR, XDATA3) 
    X_RAW_M = bus.read_byte_data(DEVICE_ADDR, XDATA2)
    X_RAW_L = bus.read_byte_data(DEVICE_ADDR, XDATA1)
    Y_RAW_H = bus.read_byte_data(DEVICE_ADDR, YDATA3)
    Y_RAW_M = bus.read_byte_data(DEVICE_ADDR, YDATA2)
    Y_RAW_L = bus.read_byte_data(DEVICE_ADDR, YDATA1)
    Z_RAW_H = bus.read_byte_data(DEVICE_ADDR, ZDATA3)
    Z_RAW_M = bus.read_byte_data(DEVICE_ADDR, ZDATA2)
    Z_RAW_L = bus.read_byte_data(DEVICE_ADDR, ZDATA1)
    
    '''
    print(f"Raw X - H: {X_RAW_H}, M: {X_RAW_M}, L: {X_RAW_L}")
    print(f"Raw Y - H: {Y_RAW_H}, M: {Y_RAW_M}, L: {Y_RAW_L}")
    print(f"Raw Z - H: {Z_RAW_H}, M: {Z_RAW_M}, L: {Z_RAW_L}")
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - -")
    '''

    # RAW 결합
    X_RAW  = (X_RAW_H << 12) | (X_RAW_M << 4) | (X_RAW_L >> 4)
    Y_RAW  = (Y_RAW_H << 12) | (Y_RAW_M << 4) | (Y_RAW_L >> 4)
    Z_RAW  = (Z_RAW_H << 12) | (Z_RAW_M << 4) | (Z_RAW_L >> 4)

    print(f"Raw Data 1 - X: {X_RAW}, Y: {Y_RAW}, Z: {Z_RAW}")

    # 2의 보수 변환 (20비트 음수 처리)
    if X_RAW & (1 << 19):
        X_RAW -= (1 << 20)
    if Y_RAW & (1 << 19):
        Y_RAW -= (1 << 20)
    if Z_RAW & (1 << 19):
        Z_RAW -= (1 << 20)

    print(f"Raw Data 2 - X: {X_RAW}, Y: {Y_RAW}, Z: {Z_RAW}")

    # ±2g 모드에서 g 단위 변환
    g_X = X_RAW / 256000
    g_Y = Y_RAW / 256000
    g_Z = Z_RAW / 256000

    print(f"{TIMESTAMP:.4f} s - X: {g_X:.6f} g, Y: {g_Y:.6f} g, Z: {g_Z:.6f} g")

    #test = bus.read_byte_data(DEVICE_ADDR, Status)

    # 출력: 16진수로 표시
    #print(f"Status : {hex(test)}")

    # ±2g 모드에서 m/s^2 단위 변환
    g_X1 = g_X * G #* 9
    g_Y1 = g_Y* G #* 9
    g_Z1 = g_Z * G #* 9


    # CSV 파일에 데이터 저장
    with open(OUTPUT_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([TIMESTAMP, g_X1, g_Y1, g_Z1])

    # 결과 출력
    print(f"{TIMESTAMP:.4f} s - X: {g_X1:.6f} m/s^2, Y: {g_Y1:.6f} m/s^2, Z: {g_Z1:.6f} m/s^2")

    return g_X, g_Y, g_Z

def main():
    # 타임스탬프 시작
    START_TIME = time.time()

    setup(START_TIME)  # 센서 초기화 함수 호출

    while True:
        read_acceleration(START_TIME)  # 가속도 측정
        time.sleep(0.008)

if __name__ == "__main__":
    main()
