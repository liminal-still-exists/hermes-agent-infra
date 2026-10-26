import http.server
from http.server import ThreadingHTTPServer
import json
from urllib.parse import parse_qs
import hmac, hashlib, urllib.request
import ctypes

# 설정 파일 로드
_CONFIG_PATH = r"C:\Scripts\config\remote_control.json"
with open(_CONFIG_PATH, "r", encoding="utf-8") as _f:
    _config = json.load(_f)

class PowerControlHandler(http.server.SimpleHTTPRequestHandler):
    _shutting_down = False

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_content = '''
                <html>
                    <head>
                        <title>Power Control</title>
                        <meta charset="UTF-8">
                    </head>
                    <body>
                        <h2>전원 컨트롤</h2>
                            <button onclick="handlePowerSubmit()">절전 모드</button>
                            <p id="status">컴퓨터 상태: 켜짐</p>
                        <br>
                        <h2>모니터 컨트롤</h2>
                        <button onclick="handleMonitorOff()">모니터 끄기</button>
                        <script>
                            let monitorDebounce = false;
                            let powerDebounce = false;
                            function handleMonitorOff() {
                                if (monitorDebounce) return;
                                monitorDebounce = true;
                                fetch('/monitor-off', {
                                    method: 'POST',
                                });
                                setTimeout(function() { monitorDebounce = false; }, 5000);
                            }

                            function handlePowerSubmit() {
                                document.getElementById('status').innerText = '컴퓨터 상태: 절전 모드 진입 중';
                                if (powerDebounce) return;
                                powerDebounce = true;
                                setTimeout(function() { powerDebounce = false; }, 5000);

                                // 타임아웃 설정
                                const timeout = new Promise((_, reject) => {
                                    setTimeout(() => {
                                        reject(new Error('Request timed out'));
                                    }, 3000);
                                });

                                // fetch 요청
                                const fetchRequest = fetch('/shutdown', {
                                    method: 'POST',
                                    body: new URLSearchParams({ power_button: '알림' }),
                                    headers: {
                                        'Content-Type': 'application/x-www-form-urlencoded',
                                    },
                                }).then(async response => {
                                    const data = await response.json();
                                    return data;
                                });
                                // Promise.race를 사용하여 타임아웃과 fetch 경합
                                Promise.race([timeout, fetchRequest])
                                    .then(data => {
                                        document.getElementById('status').innerText = data.message;
                                    })
                                    .catch(error => {
                                        console.error('Error:', error);
                                        document.getElementById('status').innerText = '컴퓨터 상태: 응답 없음';
                                    });
                            }
                        </script>
                    </body>
                </html>
            '''
            self.wfile.write(html_content.encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/monitor-off':
            try:
                secret = _config["webhook_secret"].encode()
                body = b'{"action": "monitor-off"}'
                sig = hmac.new(secret, body, hashlib.sha256).hexdigest()
                req = urllib.request.Request(
                    _config["webhook_url"],
                    data=body,
                    headers={
                        "Content-Type": "application/json",
                        "X-Hub-Signature-256": f"sha256={sig}",
                    },
                )
                with urllib.request.urlopen(req, timeout=10):
                    pass
            except Exception as e:
                print(f"Webhook 호출 실패: {e}")
            finally:
                self.send_response(200)
                self.end_headers()
        elif self.path == '/shutdown':
            if PowerControlHandler._shutting_down:
                self.send_response(429)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": "중복 클릭 방지"}).encode())
                return

            PowerControlHandler._shutting_down = True
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)

            if 'power_button' in params:
                # 응답 먼저 보내고 종료
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"message": "절전 모드 진입 완료"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                self.wfile.flush()
                PowerControlHandler._shutting_down = False
                # subprocess.run(["rundll32.exe", "powrprof.dll","SetSuspendState", "0, 1, 0"])
                ctypes.windll.powrprof.SetSuspendState(0, 0, 0)
        else:
            super().do_POST()

# 사용할 포트 번호 (설정 파일)
port = _config["port"]

# 웹서버 시작
with ThreadingHTTPServer(("", port), PowerControlHandler) as httpd:
    print("웹서버 시작. 포트", port)
    httpd.serve_forever()