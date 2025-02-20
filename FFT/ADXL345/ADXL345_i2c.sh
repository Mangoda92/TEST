#!/bin/bash

# I2C 주소 및 레지스터 정의 (ADXL345 기본 주소: 0x53)
ADDRESS=0x53
POWER_CTL=0x2D
DATA_FORMAT=0x31
BW_RATE=0x2C
DATAX0=0x32
DATAX1=0x33
DATAY0=0x34
DATAY1=0x35
DATAZ0=0x36
DATAZ1=0x37

# CSV 파일 초기화
OUTPUT_FILE="/home/mango/workspace/FFT/adxl345_data.csv"
echo "Time (s),X (mg),Y (mg),Z (mg)" > $OUTPUT_FILE

# 센서 초기화 (측정 모드 활성화)
i2cset -y 1 $ADDRESS $POWER_CTL 0x08  # 측정 모드 활성화
i2cset -y 1 $ADDRESS $DATA_FORMAT 0x0B # ±16g 모드, FULL_RES
i2cset -y 1 $ADDRESS $BW_RATE 0x0A     # 100Hz 샘플링 속도 설정

# 초기 오프셋 계산 (평균 샘플링)
SAMPLES=100
X_OFFSET=0
Y_OFFSET=0
Z_OFFSET=0

echo "Calibrating offset using $SAMPLES samples..."
for ((i=0; i<$SAMPLES; i++)); do
    X_L=$(i2cget -y 1 $ADDRESS $DATAX0)
    X_H=$(i2cget -y 1 $ADDRESS $DATAX1)
    Y_L=$(i2cget -y 1 $ADDRESS $DATAY0)
    Y_H=$(i2cget -y 1 $ADDRESS $DATAY1)
    Z_L=$(i2cget -y 1 $ADDRESS $DATAZ0)
    Z_H=$(i2cget -y 1 $ADDRESS $DATAZ1)

    X_RAW=$(( ($(printf "%d" $X_H) << 8) | $(printf "%d" $X_L) ))
    Y_RAW=$(( ($(printf "%d" $Y_H) << 8) | $(printf "%d" $Y_L) ))
    Z_RAW=$(( ($(printf "%d" $Z_H) << 8) | $(printf "%d" $Z_L) ))

    if [ $X_RAW -gt 32767 ]; then X_RAW=$((X_RAW - 65536)); fi
    if [ $Y_RAW -gt 32767 ]; then Y_RAW=$((Y_RAW - 65536)); fi
    if [ $Z_RAW -gt 32767 ]; then Z_RAW=$((Z_RAW - 65536)); fi

    X_OFFSET=$((X_OFFSET + X_RAW))
    Y_OFFSET=$((Y_OFFSET + Y_RAW))
    Z_OFFSET=$((Z_OFFSET + Z_RAW))

    sleep 0.1  # 5ms 대기
done

X_OFFSET=$((X_OFFSET / SAMPLES))
Y_OFFSET=$((Y_OFFSET / SAMPLES))
Z_OFFSET=$((Z_OFFSET / SAMPLES))

echo "Calibration complete: X_OFFSET=$X_OFFSET, Y_OFFSET=$Y_OFFSET, Z_OFFSET=$Z_OFFSET"

# 타임스탬프 시작
START_TIME=$(date +%s.%N)  # 초.나노초 단위

# 데이터 수집 루프
while true
do
    CURRENT_TIME=$(date +%s.%N)
    TIMESTAMP=$(echo "$CURRENT_TIME - $START_TIME" | bc)

    X_L=$(i2cget -y 1 $ADDRESS $DATAX0)
    X_H=$(i2cget -y 1 $ADDRESS $DATAX1)
    Y_L=$(i2cget -y 1 $ADDRESS $DATAY0)
    Y_H=$(i2cget -y 1 $ADDRESS $DATAY1)
    Z_L=$(i2cget -y 1 $ADDRESS $DATAZ0)
    Z_H=$(i2cget -y 1 $ADDRESS $DATAZ1)

    X_RAW=$(( ($(printf "%d" $X_H) << 8) | $(printf "%d" $X_L) ))1
    Y_RAW=$(( ($(printf "%d" $Y_H) << 8) | $(printf "%d" $Y_L) ))
    Z_RAW=$(( ($(printf "%d" $Z_H) << 8) | $(printf "%d" $Z_L) ))

    if [ $X_RAW -gt 32767 ]; then X_RAW=$((X_RAW - 65536)); fi
    if [ $Y_RAW -gt 32767 ]; then Y_RAW=$((Y_RAW - 65536)); fi
    if [ $Z_RAW -gt 32767 ]; then Z_RAW=$((Z_RAW - 65536)); fi

    # 오프셋 적용
    X_RAW=$((X_RAW - X_OFFSET))
    Y_RAW=$((Y_RAW - Y_OFFSET))
    Z_RAW=$((Z_RAW - Z_OFFSET))

    # mg 단위로 변환 (16g 모드, 4mg/LSB)
    X_MG=$(echo "$X_RAW * 4" | bc)
    Y_MG=$(echo "$Y_RAW * 4" | bc)
    Z_MG=$(echo "$Z_RAW * 4" | bc)

    # CSV 파일에 데이터 저장
    echo "$TIMESTAMP,$X_MG,$Y_MG,$Z_MG" >> $OUTPUT_FILE

    # 출력
    echo "$TIMESTAMP s - X: $X_MG mg, Y: $Y_MG mg, Z: $Z_MG mg"

    # 0.01초 대기 (10ms 샘플링 간격)
    sleep 0.1
done
