import numpy as np
import matplotlib.pyplot as plt

# 파라미터
L = 2                    # 선로 길이 (m;2m)
tr = 100e-12              # 라이징 타임 (100ps)
str = tr * 0.1
v_step = 1.0             # 입력 스텝 전압 (V)

CL = 2.051e-12  # C11 : 2.051pF
CM = 0.239e-12  # C12 : 0.239pF
LL = 9.869e-9   # L11 : 9.869nH
LM = 2.103e-9   # L12 : 2.103nH

#CL = 1.5941281e-11  # C11 
#CM = 6.568844e-13   # C12 
#LL = 1.01237982e-7  # L11 
#LM = 1.71586305e-8  # L12 

# 지연 시간
TD = L * (np.sqrt(LL * CL))

# NEXT 계산
NEXT = (v_step / 4) * ((LM / LL) + (CM / CL))  # NEXT 최대 전위

# FEXT 계산
FEXT = - ((v_step / 2) * TD / tr) * ((LM / LL) - (CM / CL))  # FEXT 최소 전위

# 예제 값 (실제 계산값이 예제값과 일치해야 함)
print(f"Calculated CL(C11): {CL} V")
print(f"Calculated CM(C12): {CM} V")
print(f"Calculated LL(L11): {LL} V")
print(f"Calculated LM(L12): {LM} V")
print(f"Calculated NEXT: {NEXT} V")
print(f"Calculated FEXT: {FEXT} V")
print(f"Calculated TD: {TD} s")

# 시간 축 생성 
time = np.linspace(0, 10 * tr, 1000) 

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

# FEXT 신호 
fext_signal = np.zeros_like(time)
fext_signal[time > TD] = np.where(
    time[time > TD] <= TD + str,  # 빠르게 증가하는 부분
    FEXT * ((time[time > TD] - TD) / str),  # 선형적으로 증가
    np.where(time[time > TD] <= TD + tr, 
             FEXT,  # 유지하는 부분 (tr 동안 유지)
             np.where(time[time > TD] <= TD + tr + str,
                      FEXT - FEXT * ((time[time > TD] - (TD + tr)) / str),  # 빠르게 감소하는 부분
                      0)  # tr 후 0으로 감소
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