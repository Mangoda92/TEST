pkg load instrument-control

% TCP 클라이언트 설정
TCP_IP = "192.168.75.19";  
TCP_PORT = 5005;  
tcp_client = tcpip(TCP_IP, TCP_PORT);

% TCP 연결 시작
fopen(tcp_client);
disp("Listening for data...");

% 실시간 데이터를 저장할 배열 초기화
time_data = [];
x_accel_data = [];
y_accel_data = [];
z_accel_data = [];

% FFT 관련 파라미터
fs = 1;  % 샘플링 주파수, 추후 계산될 값
N = 0;  % 데이터 개수
ts = 0;  % 평균 샘플링 간격

% 실시간 그래프를 위한 설정
figure;
subplot(3,1,1);  % X축 가속도 그래프
h1 = plot(nan, nan, 'r');
xlabel('Frequency (Hz)');
ylabel('Amplitude');
title('FFT of X-axis');
grid on;

subplot(3,1,2);  % Y축 가속도 그래프
h2 = plot(nan, nan, 'g');
xlabel('Frequency (Hz)');
ylabel('Amplitude');
title('FFT of Y-axis');
grid on;

subplot(3,1,3);  % Z축 가속도 그래프
h3 = plot(nan, nan, 'b');
xlabel('Frequency (Hz)');
ylabel('Amplitude');
title('FFT of Z-axis');
grid on;

% 실시간 데이터 수집 및 FFT 업데이트 루프
while true
    try
        % 4개의 float (16바이트) 데이터를 읽음
        raw_data = fread(tcp_client, 4, "single");

        % 데이터가 제대로 수신되었는지 확인
        if length(raw_data) == 4
            % 데이터를 배열에 저장
            time_data = [time_data; raw_data(1)];
            x_accel_data = [x_accel_data; raw_data(2)];
            y_accel_data = [y_accel_data; raw_data(3)];
            z_accel_data = [z_accel_data; raw_data(4)];

            % 샘플링 주파수와 시간 차이 계산
            if length(time_data) > 1
                ts = mean(diff(time_data));  % 평균 샘플링 간격
                fs = 1 / ts;  % 샘플링 주파수
            end
            N = length(time_data);  % 데이터 길이

            % 실시간 FFT 계산 및 그래프 갱신
            % X, Y, Z축에 대해 각각 FFT 분석 수행
            fft_analysis(x_accel_data, fs, N, 'X', 'r', 1, h1);
            fft_analysis(y_accel_data, fs, N, 'Y', 'g', 2, h2);
            fft_analysis(z_accel_data, fs, N, 'Z', 'b', 3, h3);

            % 데이터 출력
            fprintf("Time: %.4f s, X: %.4f mg, Y: %.4f mg, Z: %.4f mg\n", raw_data(1), raw_data(2), raw_data(3), raw_data(4));
        else
            warning("Received data length is incorrect. Expected 4 values, got %d values.", length(raw_data));
        end
    catch
        disp("Error or connection lost. Reconnecting...");
        fclose(tcp_client);
        pause(1);
        fopen(tcp_client);
    end
    
    pause(0.001);  % 1ms 대기 (실시간 처리 시간 간격)
end

% TCP 연결 종료
fclose(tcp_client);

% 실시간 FFT 분석 함수 (그래프 갱신)
function fft_analysis(signal, fs, N, axis_name, color, subplot_idx, plot_handle)
    % 평균값을 제거하고 FFT를 수행합니다.
    Y = fft(signal - mean(signal));  
    f = (0:N-1) * (fs / N);  % 주파수 벡터 (0부터 fs까지)
    Pyy = abs(Y / N);  % FFT 크기 (복소수 크기 계산)

    % Nyquist 주파수까지만 사용 (양의 주파수 성분만)
    f_half = f(1:floor(N / 2));  % Nyquist 주파수까지만 추출
    Pyy_half = Pyy(1:floor(N / 2));  % Nyquist 주파수까지만 추출

    % 각 서브플롯에 대해 FFT 그래프 그리기
    subplot(3, 1, subplot_idx);  % 3개의 서브플롯 중 subplot_idx번째 위치에 그래프 그리기
    set(plot_handle, 'YData', Pyy_half, 'XData', f_half);  % 기존 그래프 데이터 갱신
    title(['FFT of ', axis_name, '-axis']);  % 각 서브플롯 제목 (X, Y, Z 축별로 다르게 표시)
end
