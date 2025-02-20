fs = 5000; % 샘플링 주파수 (1kHz 신호를 충분히 표현할 수 있도록 높임)
f_vib_1 = 1000; % 1kHz 진동 주파수
f_vib_2 = 500;  % 500Hz 진동 주파수
f_vib_3 = 100;  % 100Hz 진동 주파수
T = 0.1; % 100ms 동안 데이터 생성
t = (0:1/fs:T)'; % 시간 벡터

% 변위 신호 (μm 단위)
x_displacement = 1.0 * sin(2 * pi * f_vib_1 * t) + 1.0 * sin(2 * pi * f_vib_2 * t); % X축 변위 (1μm @ 1kHz + 1μm @ 500Hz)
y_displacement = 1.0 * sin(2 * pi * f_vib_2 * t) + 1.0 * sin(2 * pi * f_vib_3 * t); % Y축 변위 (1μm @ 500Hz + 1μm @ 100Hz)
z_displacement = 1.0 * sin(2 * pi * f_vib_3 * t) + 1.0 * sin(2 * pi * f_vib_1 * t); % Z축 변위 (1μm @ 100Hz + 1μm @ 1kHz)

% 변위를 두 번 미분하여 가속도 계산 (단위: μm/s²)
x_accel = - (2 * pi * f_vib_1)^2 * 1.0 * sin(2 * pi * f_vib_1 * t) ...
          - (2 * pi * f_vib_2)^2 * 1.0 * sin(2 * pi * f_vib_2 * t);

y_accel = - (2 * pi * f_vib_2)^2 * 1.0 * sin(2 * pi * f_vib_2 * t) ...
          - (2 * pi * f_vib_3)^2 * 1.0 * sin(2 * pi * f_vib_3 * t);

z_accel = - (2 * pi * f_vib_3)^2 * 1.0 * sin(2 * pi * f_vib_3 * t) ...
          - (2 * pi * f_vib_1)^2 * 1.0 * sin(2 * pi * f_vib_1 * t);

% 데이터 저장 (지정한 경로)
data = [t, x_accel, y_accel, z_accel];
csvwrite('L:/00_share/vibration_1kHz.csv', data);  % 경로 지정
