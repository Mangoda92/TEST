pkg load instrument-control

% TCP 클라이언트 설정
TCP_IP = "192.168.75.19";
TCP_PORT = 5005;
tcp_client = tcpip(TCP_IP, TCP_PORT);

% TCP 연결 시작
fopen(tcp_client);
disp("Listening for data...");

while true
    try
        % 4개의 float (16바이트) 데이터를 읽음
        raw_data = fread(tcp_client, 4, "single");  % ★ 4개의 float을 읽어야 함

        % 데이터가 제대로 수신되었는지 확인
        if length(raw_data) == 4
            time_value = raw_data(1);
            x = raw_data(2);
            y = raw_data(3);
            z = raw_data(4);

            % 수신한 데이터 출력
            fprintf("Time: %.4f s, X: %.4f mg, Y: %.4f mg, Z: %.4f mg\n", time_value, x, y, z);
        else
            warning("Received data length is incorrect. Expected 4 values, got %d values.", length(raw_data));
        end
    catch
        disp("Error or connection lost. Reconnecting...");
        fclose(tcp_client);
        pause(1);
        fopen(tcp_client);
    end

    pause(0.001);
end

% TCP 연결 종료
fclose(tcp_client);
