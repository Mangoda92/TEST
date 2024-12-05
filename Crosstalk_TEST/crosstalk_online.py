import numpy as np

# 주어진 파라미터
epsilon_r = 4.2  # 상대 유전율
L = 50e-3        # 선로 길이 (m)
S = 635e-6       # 선로 간 거리 (m)
H = 200e-6       # 유전체 두께 (m)
TR = 0.1e-9      # 트랜지션 시간 (초)
V = 1.0          # 입력 전압 (V)

# TRT 계산
TRT = 1.017 * np.sqrt(epsilon_r ** (0.475 + 0.67)) * L * 2

# S/H 비율 계산
S_H_ratio = S / H

# TRT/TR 계산
TRT_TR_ratio = TRT / TR

# 계산 조건 확인 (TRT_TR_ratio가 1 이하인지 확인)
if TRT_TR_ratio <= 1:
    # TRT/TR이 1 이하일 경우 계산
    CTdB = 20 * np.log10(1 / (1 + S_H_ratio**2) * TRT_TR_ratio)
    V_crosstalk = V * (1 / (1 + S_H_ratio**2)) * TRT_TR_ratio
else:
    # TRT/TR이 1 초과일 경우 계산
    CTdB = 20 * np.log10(1 / (1 + S_H_ratio**2))
    V_crosstalk = V * (1 / (1 + S_H_ratio**2))

# 결과 출력
print(f"TRT = {TRT:.5e} s")
print(f"TRT/TR ratio = {TRT_TR_ratio:.5f}")
print(f"V_crosstalk = {V_crosstalk:.5f} V")
print(f"CTdB = {CTdB:.2f} dB")