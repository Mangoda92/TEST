import spidev
import time
import csv
import struct
import socket

# SPI 설정
spi = spidev.SpiDev()
spi.open(0, 0)  # Raspberry Pi의 SPI Bus 0, Chip Select 0
spi.max_speed_hz = 500000    # SPI 속도 (1 MHz)
spi.bits_per_word = d  # 8비트 데이터 전송 설정
spi.mode = 0b00  # SPI 모드 3 (CPOL=1, CPHA=1)

# Addresses
DEVID_AD = 0x00
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

SAMPLES = 500

# 지구 중력 가속도 (m/s^2)
G = 9.81 
'''
# SPI 설정
OUTPUT_FILE = "/home/mango/workspace/FFT/adxl355/log/test_spi.csv"
'''
# TCP 서버 설정
TCP_IP = "192.168.213.34"
TCP_PORT = 5005

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((TCP_IP, TCP_PORT))
server_socket.listen(1)
print(f"Listening on {TCP_IP}:{TCP_PORT}...")


def read_register(addr):
    response = spi.xfer2([addr << 1 | 0x01, 0x0])  
    return response[1]

def write_register(addr, data):
    response = spi.xfer2([addr << 1 | 0x00, data])  
    return response[1]

def setup(START_TIME):

    # 센서 초기화
    print("초기화 중...")
    '''
    # CSV 파일 초기화
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time (s)", "X (m/s^2)", "Y (m/s^2)", "Z (m/s^2)"])
    
    
    DEVID_AD = read_register(0x00)
    print(f"DEVID_AD : {hex(DEVID_AD)}")

    DEVID_MST = read_register(0x01)
    print(f"DEVID_MST : {hex(DEVID_MST)}")

    PARTID = read_register(0x02)
    print(f"PARTID : {hex(PARTID)}")

    DEVID = read_register(0x03)
    print(f"DEVID : {hex(DEVID)}")
    '''

    # 옵셋 설정
    set_offset(0, 0, 0)  # Raw Data 1 >> 4
    time.sleep(1)

    # 인터럽트 설정
    write_register(INT_MAP, 0x00) 
    time.sleep(1)  

    # 가속도 측정 범위 설정
    write_register(RANGE, RANGE_2G)
    time.sleep(1) 

    # 샘플링 속도 & LPF 설정 //HPF 비활성화
    write_register(FILTER, ODR500_LPF125)
    time.sleep(1) 

    # ADXL355을 측정 모드로 설정
    write_register(POWER_CTL, 0x6)  
    time.sleep(1) 
    '''
    s1 = read_register(INT_MAP)
    print(f"INT_MAP : {hex(s1)}")

    s1 = read_register(RANGE)  
    print(f"RANGE : {hex(s1)}")

    s1 = read_register(FILTER)  
    print(f"FILTER : {hex(s1)}")

    s1 = read_register(POWER_CTL)  
    print(f"POWER_CTL : {hex(s1)}")
    '''
    print("초기화 완료!")
    return START_TIME

def set_offset(offset_x, offset_y, offset_z):
    """ 센서의 X, Y, Z 옵셋을 설정하는 함수 """
    
    # X축 옵셋
    write_register(OFFSET_X_H, (offset_x >> d) & 0xFF)  # X 상위 8비트
    time.sleep(0.1)
    write_register(OFFSET_X_L, offset_x & 0xFF)  # X 하위 8비트
    time.sleep(0.1)

    # Y축 옵셋
    write_register(OFFSET_Y_H, (offset_y >> d) & 0xFF)  # Y 상위 8비트
    time.sleep(0.1)
    write_register(OFFSET_Y_L, offset_y & 0xFF)  # Y 하위 8비트
    time.sleep(0.1)

    # Z축 옵셋
    write_register(OFFSET_Z_H, (offset_z >> d) & 0xFF)  # Z 상위 8비트
    time.sleep(0.1)
    write_register(OFFSET_Z_L, offset_z & 0xFF)  # Z 하위 8비트
    time.sleep(0.1)

def callibration(SAMPLES):

    print(f"Calibrating offset using {SAMPLES} samples...")

    X_OFFSET, Y_OFFSET, Z_OFFSET = 0, 0, 0  # 초기화

    for i in range(SAMPLES):
        X_RAW_H = read_register(XDATA3)
        X_RAW_M = read_register(XDATA2)
        X_RAW_L = read_register(XDATA1)
        Y_RAW_H = read_register(YDATA3)
        Y_RAW_M = read_register(YDATA2)
        Y_RAW_L = read_register(YDATA1)
        Z_RAW_H = read_register(ZDATA3)
        Z_RAW_M = read_register(ZDATA2)
        Z_RAW_L = read_register(ZDATA1)

        X_RAW = (X_RAW_H << 12) | (X_RAW_M << 4) | (X_RAW_L >> 4)
        Y_RAW = (Y_RAW_H << 12) | (Y_RAW_M << 4) | (Y_RAW_L >> 4)
        Z_RAW = (Z_RAW_H << 12) | (Z_RAW_M << 4) | (Z_RAW_L >> 4)

        # 오프셋 누적
        X_OFFSET += (X_RAW >> 4)
        Y_OFFSET += (Y_RAW >> 4)
        Z_OFFSET += (Z_RAW >> 4)
        
        time.sleep(0.01)
   
    #print(f"합계 X: {X_OFFSET}, Y: {Y_OFFSET}, Z: {Z_OFFSET}")

    # 평균 오프셋 계산
    X_OFFSET //= SAMPLES
    Y_OFFSET //= SAMPLES
    Z_OFFSET //= SAMPLES

    #print(f"나누기 X: {X_OFFSET}, Y: {Y_OFFSET}, Z: {Z_OFFSET}")

    # 옵셋 설정
    set_offset(X_OFFSET, Y_OFFSET, Z_OFFSET)  # Raw Data 1 >> 4
    time.sleep(1)

    print(f"Calibration complete!")

def read_acceleration(START_TIME):
    CURRENT_TIME = time.time()
    TIMESTAMP = CURRENT_TIME - START_TIME

    # 각 축의 RAW 값을 개별적으로 읽음
    X_RAW_H = read_register(XDATA3)
    X_RAW_M = read_register(XDATA2)
    X_RAW_L = read_register(XDATA1)
    Y_RAW_H = read_register(YDATA3)
    Y_RAW_M = read_register(YDATA2)
    Y_RAW_L = read_register(YDATA1)
    Z_RAW_H = read_register(ZDATA3)
    Z_RAW_M = read_register(ZDATA2)
    Z_RAW_L = read_register(ZDATA1)
    '''
    print(f"Raw X - H: {X_RAW_H}, M: {X_RAW_M}, L: {X_RAW_L}")
    print(f"Raw Y - H: {Y_RAW_H}, M: {Y_RAW_M}, L: {Y_RAW_L}")
    print(f"Raw Z - H: {Z_RAW_H}, M: {Z_RAW_M}, L: {Z_RAW_L}")
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - -")
    '''
    # RAW 결합
    X_RAW = (X_RAW_H << 12) | (X_RAW_M << 4) | (X_RAW_L >> 4)
    Y_RAW = (Y_RAW_H << 12) | (Y_RAW_M << 4) | (Y_RAW_L >> 4)
    Z_RAW = (Z_RAW_H << 12) | (Z_RAW_M << 4) | (Z_RAW_L >> 4)

    #print(f"Raw Data 1 - X: {X_RAW}, Y: {Y_RAW}, Z: {Z_RAW}")

    # 2의 보수 변환 (20비트 음수 처리)
    if X_RAW & (1 << 19):
        X_RAW -= (1 << 20)
    if Y_RAW & (1 << 19):
        Y_RAW -= (1 << 20)
    if Z_RAW & (1 << 19):
        Z_RAW -= (1 << 20)

    #print(f"Raw Data 2 - X: {X_RAW}, Y: {Y_RAW}, Z: {Z_RAW}")

    # ±2g 모드에서 g 단위 변환
    g_X = X_RAW / 256000
    g_Y = Y_RAW / 256000
    g_Z = Z_RAW / 256000

    #print(f"{TIMESTAMP:.4f} s - X: {g_X:.6f} g, Y: {g_Y:.6f} g, Z: {g_Z:.6f} g")

    # ±2g 모드에서 m/s^2 단위 변환
    g_X1 = g_X * G
    g_Y1 = g_Y * G
    g_Z1 = g_Z * G
    '''
    # CSV 파일에 데이터 저장
    with open(OUTPUT_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([TIMESTAMP, g_X1, g_Y1, g_Z1])
    '''
    # 결과 출력
    #print(f"{TIMESTAMP:.4f} s - X: {g_X1:.6f} m/s^2, Y: {g_Y1:.6f} m/s^2, Z: {g_Z1:.6f} m/s^2")

    return TIMESTAMP, g_X, g_Y, g_Z

def main():

    global conn, addr

    conn, addr = server_socket.accept()
    print(f"Connection from: {addr}")
    
    # 타임스탬프 시작
    START_TIME = time.time()

    setup(START_TIME)  # 센서 초기화 함수 호출

    callibration(SAMPLES)

    while True:

        try:
            TIMESTAMP, g_X, g_Y, g_Z = read_acceleration(START_TIME)

            # 바이너리 변환 및 전송 (정수 4개 = 16 bytes)
            binary_data = struct.pack('<ffff', float(TIMESTAMP), float(g_X), float(g_Y), float(g_Z))
            conn.send(binary_data)

            print(f"Sent: {TIMESTAMP}, X: {g_X}, Y: {g_Y}, Z: {g_Z}")

            time.sleep(0.002)  # 500Hz 샘플링

        except BrokenPipeError:
            print("Client disconnected. Waiting for new connection...")
            conn.close()
            conn, addr = server_socket.accept()
            print(f"New connection from: {addr}")
        

if __name__ == "__main__":
    main()
