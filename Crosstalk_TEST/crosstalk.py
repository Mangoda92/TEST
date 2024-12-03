import numpy as np
import matplotlib.pyplot as plt

# 주어진 파라미터
w1, w2 = 335e-6, 335e-6  # Line 1과 Line 2의 폭 (m)
t1, t2 = 40e-6, 40e-6    # Line 1과 Line 2의 두께 (40 μm)
h = 200e-6               # 유전체 두께 (m)
d = 635e-6               # 두 선로 간 거리 (m)
L = 2                    # 선로 길이 (m;2m)
er = 4.2                 # 상대 유전율 (FR4)
tan_delta = 0.02         # 손실 탄젠트
tr = 100e-12              # 라이징 타임 (100ps)
str = tr * 0.1
v_step = 1.0             # 입력 스텝 전압 (V)


# 고유 상수
c0 = 3e8                 # 빛의 속도 (m/s)
e0 = 8.854e-12           # 진공 유전율 (F/m)

# 계산용 상수
c = c0 / np.sqrt(er)     # 유전체 내 신호 전달 속도
dV_dt = v_step / tr      # 입력 신호의 변화율 (V/s)

CL = 2.051e-12  # C11 : 2.051pF
CM = 0.239e-12  # C12 : 0.239pF
LL = 9.869e-9   # L11 : 9.869nH
LM = 2.103e-9   # L12 : 2.103nH


# 지연 시간
TD = L * (np.sqrt(LL * CL))
#TD = 0.28e-9  # TD를 0.28ns로 지정

# NEXT 계산 (수정된 수식 사용)
NEXT = (v_step / 4) * ((LM / LL) + (CM / CL))  # NEXT 최대 전위

# FEXT 계산 (수정된 수식 사용)
FEXT = - ((v_step / 2) * TD / tr) * ((LM / LL) - (CM / CL))  # FEXT 최소 전위

# 예제 값 (실제 계산값이 예제값과 일치해야 함)
print(f"Calculated CL(C11): {CL} V")
print(f"Calculated CM(C12): {CM} V")
print(f"Calculated LL(L11): {LL} V")
print(f"Calculated LM(L12): {LM} V")
print(f"Calculated NEXT: {NEXT} V")
print(f"Calculated FEXT: {FEXT} V")
print(f"Calculated TD: {TD} s")

# 시간 축 생성 (시간을 2배 더 확장)
time = np.linspace(0, 10 * tr, 1000)  # 라이징 타임 후 5배까지

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