% ADXL345 가속도 데이터 FFT 분석 스크립트 (Octave)

% 데이터 로드
% 'adxl345_spi_data.csv' 파일을 로드하고, 첫 번째 줄(헤더)을 제외하고 데이터를 읽어옵니다.
data = dlmread('L:\00_share\adxl345_spi_data_0.csv', '', 1, 0); 

% 시간 및 가속도 데이터 추출
time = data(:, 1);  % 첫 번째 열: 시간 (초)
x_accel = data(:, 2);  % 두 번째 열: X축 가속도 (mg)
y_accel = data(:, 3);  % 세 번째 열: Y축 가속도 (mg)
z_accel = data(:, 4);  % 네 번째 열: Z축 가속도 (mg)

% 샘플링 주파수 계산
% 시간 차이의 평균을 구하여 샘플링 간격을 구합니다.
ts = mean(diff(time));  % 평균 샘플링 간격 (초 단위)
fs = 1 / ts;  % 샘플링 주파수 (Hz)
N = length(time);  % 데이터 길이 (샘플 수)

% 전체 FFT 플롯 생성
figure;  % 새로운 피겨(그래프) 창을 생성
hold on;  % 여러 그래프를 하나의 창에 그릴 수 있도록 설정

% 샘플링 정보 표시
% 텍스트 박스를 생성하여 샘플링 정보(평균 샘플링 간격과 샘플링 주파수)를 표시합니다.
annotation('textbox', [0.15, 0.85, 0.3, 0.1], 'String', sprintf('평균 샘플링 간격: %.6f 초\n샘플링 주파수: %.2f Hz', ts, fs), 'EdgeColor', 'none', 'FontSize', 10, 'FontWeight', 'bold');

% FFT 수행 및 개별 서브플롯 표시
function fft_analysis(signal, fs, N, axis_name, color, subplot_idx)
    % 평균값을 제거하고 FFT를 수행합니다.
    Y = fft(signal - mean(signal));  
    f = (0:N-1) * (fs / N);  % 주파수 벡터 (0부터 fs까지)
    Pyy = abs(Y/N);  % FFT 크기 (복소수 크기 계산)

    % Nyquist 주파수까지만 사용 (양의 주파수 성분만)
    f_half = f(1:floor(N/2));  % Nyquist 주파수까지만 추출
    Pyy_half = Pyy(1:floor(N/2));  % Nyquist 주파수까지만 추출

    % 각 서브플롯에 대해 FFT 그래프 그리기
    subplot(3, 1, subplot_idx);  % 3개의 서브플롯 중 subplot_idx번째 위치에 그래프 그리기
    plot(f_half, Pyy_half, 'color', color, 'LineWidth', 1.2);  % 0부터 Nyquist 주파수까지의 FFT 결과
    xlabel('Frequency (Hz)');  % X축 라벨: 주파수
    ylabel('Amplitude');  % Y축 라벨: 진폭
    title(['FFT of ', axis_name, '-axis']);  % 각 서브플롯 제목 (X, Y, Z 축별로 다르게 표시)
    grid on;  % 격자 추가
end

% X, Y, Z 축에 대해 각각 FFT 분석 수행
fft_analysis(x_accel, fs, N, 'X', 'r', 1);  % X축 가속도 데이터 (빨간색)
fft_analysis(y_accel, fs, N, 'Y', 'g', 2);  % Y축 가속도 데이터 (초록색)
fft_analysis(z_accel, fs, N, 'Z', 'b', 3);  % Z축 가속도 데이터 (파란색)

hold off;  % 그래프 그리기 완료
