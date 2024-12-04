import numpy as np
import matplotlib.pyplot as plt

# 주어진 파라미터
w1, w2 = 335e-6, 335e-6     # Line 1과 Line 2의 폭 (m)
t1, t2 = 40e-6, 40e-6       # Line 1과 Line 2의 두께 (40 μm)
we = w1 + t1
h = 200e-6                  # 유전체 두께 (m)
#d = 635e-6                  # 두 선로 간 거리 (m)
d = 100e-6                    # 두 선로 간 거리 (m)
L = 50e-3                   # 선로 길이 (m)
er = 4.2                    # 상대 유전율 (FR4)
tan_delta = 0.02            # 손실 탄젠트
tr = 0.1e-9                 # Rising time (s)
str = tr * 0.1
v_step = 1.0                # 입력 스텝 전압 (V)
Z0 = 50.0
#Z0 = np.sqrt(L11/C11)         # 선로 특성 임피던스
f = 20e9                     # 주파수 (20 GHz)

# 고유 상수
c0 = 3e8                    # 빛의 속도 (m/s)
e0 = 8.854e-12              # 진공 유전율 (F/m)

# 계산용 상수
c = c0 / np.sqrt(er)        # 유전체 내 신호 전달 속도
dV_dt = v_step / tr         # 입력 신호의 변화율 (V/s)

# 유전체 손실 정수 계산
alpha_d = (np.pi * f * np.sqrt(er) * tan_delta) / c0

# 정전 용량 계산

## C11 (단위 길이당 정전 용량)                                 
C11 = e0 * er * (1 + 1 / np.sqrt(1 + 12 * (h / we))) * we / h   # Wheeler 1 PCB TOP
#C11 = e0 * er * (1 + 1 / np.sqrt(1 + 12 * (h / we))) * we / h   # Wheeler 1 PCB TOP
#C11 = e0 * er * (w1 + t1) / h                                  # 일반 PCB TOP   
#C11 = e0 * er * we / (h * np.sqrt(1 + 12 * (h / we)))          # Wheeler 2 PCB TOP
#C11 = e0 * er * (w1 + 2 * t1) / h                              # 

## C12 (단위 길이당 결합 정전 용량
C12 = e0 * er * (w1 + t1) / d                                   

## L11 (단위 길이당 인덕턴스
L11 = Z0**2 * C11                  

## L12 (단위 길이당 결합 인덕턴스
L12 = L11 * (h / d)                 

# 지연 시간
TD = L * (np.sqrt(L11 * C11))
#TD = 0.28e-9  # TD를 0.28ns로 지정

# NEXT 계산 (수정된 수식 사용)
NEXT = (v_step / 4) * ((L12 / L11) + (C12 / C11))  # NEXT 최대 전위

# FEXT 계산 (수정된 수식 사용)
FEXT = - ((v_step / 2) * TD / tr) * ((L12 / L11) - (C12 / C11))  # FEXT 최소 전위

# 예제 값 (실제 계산값이 예제값과 일치해야 함)
print(f"Calculated C11: {C11:.4e} F/m")
print(f"Calculated C12: {C12:.4e} F/m")
print(f"Calculated L11: {L11:.4e} F/m")
print(f"Calculated L12: {L12:.4e} F/m")
print(f"Calculated NEXT: {NEXT:.4e} V")
print(f"Calculated FEXT: {FEXT:.4e} V")
print(f"Calculated TD: {TD:.4e} s")
print(f"Calculated c: {c:.4e} s")

# 시간 축 생성 (시간을 2배 더 확장)
time = np.linspace(0, 12 * tr, 1000)  # 라이징 타임 후 5배까지

# 입력 신호
input_signal = np.where(time <= tr, v_step * (time / tr), v_step)

# NEXT 신호
next_signal = np.zeros_like(time)
next_signal[time <= 2 * TD] = np.where(
    time[time <= 2 * TD] <= tr,
    NEXT * (time[time <= 2 * TD] / tr),
    NEXT
)
next_signal[(time > 2 * TD) & (time <= 2 * TD + tr)] = NEXT * (
    1 - (time[(time > 2 * TD) & (time <= 2 * TD + tr)] - 2 * TD) / tr
)

# FEXT 신호 (tr 시간 후에 0으로 감소하도록 수정)
fext_signal = np.zeros_like(time)
fext_signal[time > TD] = np.where(
    time[time > TD] <= TD + str,  # 빠르게 증가하는 부분
    FEXT * ((time[time > TD] - TD) / str),  # 선형적으로 증가
    np.where(time[time > TD] <= TD + tr, 
             FEXT,  # 유지하는 부분 (tr 동안 유지)
             np.where(time[time > TD] <= TD + tr + str,
                      FEXT - FEXT * ((time[time > TD] - (TD + tr)) / str),  # 빠르게 감소하는 부분
                      0)  # 그 후 0으로 감소
    )
)

# 그래프 그리기
plt.figure(figsize=(10, 5))
plt.plot(time * 1e9, input_signal, label=": Input Signal", color="red")
plt.plot(time * 1e9, next_signal, label=": NEXT (Near-End Crosstalk)", color="blue")
plt.plot(time * 1e9, fext_signal, label=": FEXT (Far-End Crosstalk)", color="green")

# 그래프 설정
plt.title("Crosstalk Analysis in Time Domain")
plt.xlabel("Time [ns]")
plt.ylabel("Voltage [V]")
plt.legend()
plt.grid()
plt.show()

