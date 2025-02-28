% CSV 파일 경로
file_path = 'D:\00_share\data_log_2.csv';

% CSV 파일 읽기 (헤더 포함, 소수점 데이터 처리)
data = dlmread(file_path, ',', 1, 0); % 첫 번째 행(헤더) 무시하고 숫자 데이터만 읽기

% 데이터 열 분리
time = data(:, 1);  % 첫 번째 열 (시간)
X = data(:, 2);     % 두 번째 열 (X축 가속도)
Y = data(:, 3);     % 세 번째 열 (Y축 가속도)
Z = data(:, 4);     % 네 번째 열 (Z축 가속도)

% ★★★ 1 이상인 값은 0으로 정정 ★★★
%X(X > 1) = 0;
%Y(Y > 1) = 0;
%Z(Z > 1) = 0;
%X(X < -1) = 0;
%Y(Y < -1) = 0;
%Z(Z < -1) = 0;

% 그래프 그리기
figure;

% X축 가속도 그래프
subplot(3, 1, 1);
plot(time, X, 'r-', 'LineWidth', 2); % 빨간색 선 그래프
title('X Acceleration (m/s^2)');
xlabel('Time (s)');
ylabel('Acceleration (m/s^2)');
grid on;

% Y축 가속도 그래프
subplot(3, 1, 2);
plot(time, Y, 'g-', 'LineWidth', 2); % 초록색 선 그래프
title('Y Acceleration (m/s^2)');
xlabel('Time (s)');
ylabel('Acceleration (m/s^2)');
grid on;

% Z축 가속도 그래프
subplot(3, 1, 3);
plot(time, Z, 'b-', 'LineWidth', 2); % 파란색 선 그래프
title('Z Acceleration (m/s^2)');
xlabel('Time (s)');
ylabel('Acceleration (m/s^2)');
grid on;

% 전체 제목 추가
sgtitle('Acceleration Data in m/s^2 (Values > 1 Clamped to 0)');
