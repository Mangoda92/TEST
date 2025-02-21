pkg load instrument-control

% TCP 클라이언트 설정
TCP_IP = "192.168.75.19";  % 연결할 장비의 IP 주소
TCP_PORT = 5005;  % 장비와 통신할 포트 번호
tcp_client = tcpip(TCP_IP, TCP_PORT);  % TCP 연결을 설정

% TCP 연결 시작
fopen(tcp_client);  % TCP 연결을 열고 시작
disp("Listening for data...");  % 데이터를 받기 시작했다고 출력

% 실시간 데이터를 저장할 배열 초기화
time_data = [];  % 시간 데이터를 저장할 배열
x_accel_data = [];  % X축 가속도 데이터를 저장할 배열
y_accel_data = [];  % Y축 가속도 데이터를 저장할 배열
z_accel_data = [];  % Z축 가속도 데이터를 저장할 배열

% FFT 관련 파라미터
fs = 1;  % 샘플링 주파수, 초기 값으로 설정 (추후 계산됨)
N = 0;  % 데이터 개수, 초기 값으로 설정
ts = 0;  % 평균 샘플링 간격, 초기 값으로 설정

% 실시간 그래프를 위한 설정
figure;  % 새로운 figure(창)를 열어 그래프를 그릴 준비
subplot(3,1,1);  % X축 가속도 그래프를 위한 서브플롯
h1 = plot(nan, nan, 'r');  % X축 FFT 그래프 (초기값은 빈 데이터)
xlabel('Frequency (Hz)');  % X축 레이블: 주파수
ylabel('Amplitude');  % Y축 레이블: 진폭
title('FFT of X-axis');  % 제목: X축 FFT
grid on;  % 격자 표시

subplot(3,1,2);  % Y축 가속도 그래프를 위한 서브플롯
h2 = plot(nan, nan, 'g');  % Y축 FFT 그래프 (초기값은 빈 데이터)
xlabel('Frequency (Hz)');
ylabel('Amplitude');
title('FFT of Y-axis');
grid on;

subplot(3,1,3);  % Z축 가속도 그래프를 위한 서브플롯
h3 = plot(nan, nan, 'b');  % Z축 FFT 그래프 (초기값은 빈 데이터)
xlabel('Frequency (Hz)');
ylabel('Amplitude');
title('FFT of Z-axis');
grid on;

% 최대 250개의 데이터만 유지하도록 설정
MAX_DATA_POINTS = 300;  % 데이터를 최대 250개만 저장

% 실시간 데이터 수집 및 FFT 업데이트 루프
while true
    try
        % 4개의 float (16바이트) 데이터를 읽음
        raw_data = fread(tcp_client, 4, "single");  % 데이터를 4개씩 읽어옴 (float 형식)

        % 데이터가 제대로 수신되었는지 확인
        if length(raw_data) == 4  % 데이터를 4개 읽은 경우만 처리
            % 데이터를 배열에 저장 (실시간 데이터 저장)
            time_data = [time_data; raw_data(1)];  % 시간 데이터 저장
            x_accel_data = [x_accel_data; raw_data(2)];  % X축 가속도 데이터 저장
            y_accel_data = [y_accel_data; raw_data(3)];  % Y축 가속도 데이터 저장
            z_accel_data = [z_accel_data; raw_data(4)];  % Z축 가속도 데이터 저장

            % 최대 데이터 포인트를 유지하도록 데이터 잘라내기
            if length(time_data) > MAX_DATA_POINTS
                % 250개를 초과하면 가장 오래된 데이터를 제거하고 최신 데이터만 남긴다
                time_data = time_data(end-MAX_DATA_POINTS+1:end);
                x_accel_data = x_accel_data(end-MAX_DATA_POINTS+1:end);
                y_accel_data = y_accel_data(end-MAX_DATA_POINTS+1:end);
                z_accel_data = z_accel_data(end-MAX_DATA_POINTS+1:end);
            end

            % 샘플링 주파수와 시간 차이 계산
            if length(time_data) > 1
                ts = mean(diff(time_data));  % 시간 차이의 평균을 계산하여 샘플링 간격 계산
                fs = 1 / ts;  % 샘플링 주파수를 계산 (1/샘플링 간격)
            end
            N = length(time_data);  % 데이터 길이 (샘플 개수)

            % 실시간 FFT 계산 및 그래프 갱신
            % X, Y, Z축에 대해 각각 FFT 분석 수행 (주석처리된 부분)
            fft_analysis(x_accel_data, fs, N, 'X', 'r', 1, h1);
            fft_analysis(y_accel_data, fs, N, 'Y', 'g', 2, h2);
            fft_analysis(z_accel_data, fs, N, 'Z', 'b', 3, h3);

            % 데이터 출력 (디버깅용으로 출력)
            %fprintf("Time: %.4f s, X: %.4f mg, Y: %.4f mg, Z: %.4f mg\n", raw_data(1), raw_data(2), raw_data(3), raw_data(4));
        else
            warning("Received data length is incorrect. Expected 4 values, got %d values.", length(raw_data));  % 데이터 길이가 4개가 아닐 경우 경고
        end
    catch
        disp("Error or connection lost. Reconnecting...");  % 연결 오류 발생 시 재연결 메시지
        fclose(tcp_client);  % 기존 연결 종료
        pause(1);  % 잠시 대기 후
        fopen(tcp_client);  % 다시 연결 시도
    end
    
    pause(0.0001);  % 1ms 대기 (실시간 처리 시간 간격)
end

% TCP 연결 종료
fclose(tcp_client);  % 연결 종료

% 실시간 FFT 분석 함수 (그래프 갱신)
function fft_analysis(signal, fs, N, axis_name, color, subplot_idx, plot_handle)
    % 평균값을 제거하고 FFT를 수행합니다.
    Y = fft(signal - mean(signal));  % FFT 계산 (평균 제거 후)
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
