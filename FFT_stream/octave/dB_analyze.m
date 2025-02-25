pkg load instrument-control

% 55dB 이하 : 인채로 느끼지 못함
% 60dB±5 : 약간 느낌
% 70dB±5 : 크게 느낌
% 80dB±5 : 창문, 미닫이가 흔들림
% 90dB±5 : 기물이 넘어지고 물이 넘침
% 100dB±5 : 집의 벽이나 비석이 넘어짐
% 105~110dB : 가옥파괴 30%이하
% 110dB 이상 : 가옥파괴 30%이상, 단층, 산사태 발생

% TCP 클라이언트 설정
TCP_IP = "192.168.213.35";  
TCP_PORT = 5005;  
tcp_client = tcpip(TCP_IP, TCP_PORT);

% TCP 연결 시작
fopen(tcp_client);
disp("Listening for data...");

% 기준 가속도 a0 (10^-5 m/s²)
a0 = 1e-5;

% 실시간 데이터 수집 루프
while true
    try
        % 4개의 float (16바이트) 데이터를 읽음
        raw_data = fread(tcp_client, 4, "single");

        % 데이터가 제대로 수신되었는지 확인
        if length(raw_data) == 4
            % mg → m/s² 변환 (1 mg = 9.81e-3 m/s²)
            x_accel_mps2 = raw_data(2) * 9.81e-3;
            y_accel_mps2 = raw_data(3) * 9.81e-3;
            z_accel_mps2 = raw_data(4) * 9.81e-3;

            % 진동가속도레벨 (dB) 변환
            x_dB = 20 * log10(abs(x_accel_mps2) / a0);
            y_dB = 20 * log10(abs(y_accel_mps2) / a0);
            z_dB = 20 * log10(abs(z_accel_mps2) / a0);

            % 데이터 출력
            fprintf("Time: %.4f s, X: %.2f dB, Y: %.2f dB, Z: %.2f dB\n", raw_data(1), x_dB, y_dB, z_dB);
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
