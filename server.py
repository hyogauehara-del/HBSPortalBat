# server.py
import http.server
import socketserver
import json
from urllib.parse import parse_qs
from datetime import datetime
import os

PORT = 8000  # Render 上では PORT は環境変数で上書きされます
SCHEDULE_FILE = "schedule.json"

# schedule.json がなければ作成
if not os.path.exists(SCHEDULE_FILE):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

class Handler(http.server.SimpleHTTPRequestHandler):
    # POST リクエスト処理
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        data = parse_qs(body)

        # 投稿処理
        if self.path == "/schedule":
            name = data.get("name", [""])[0].strip()
            message = data.get("message", [""])[0].strip()

            if name and message:
                with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
                    schedules = json.load(f)

                now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

                # 直前と同じ投稿を1秒以内に追加しない
                if not schedules or not (
                    schedules[-1]["name"] == name and schedules[-1]["message"] == message
                ):
                    schedules.append({"name": name, "message": message, "time": now, "checked": False})
                    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
                        json.dump(schedules, f, ensure_ascii=False, indent=2)

            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")  # ← CORS 許可
            self.end_headers()
        
        # チェックボックス更新
        elif self.path == "/update_check":
            index = int(data.get("index", ["-1"])[0])
            checked = data.get("checked", ["false"])[0].lower() == "true"

            with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
                schedules = json.load(f)

            if 0 <= index < len(schedules):
                schedules[index]["checked"] = checked
                with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
                    json.dump(schedules, f, ensure_ascii=False, indent=2)

            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")  # ← CORS 許可
            self.end_headers()

        else:
            self.send_error(404, "Not Found")

    # GET リクエスト処理
    def do_GET(self):
        if self.path.startswith("/schedule"):
            if os.path.exists(SCHEDULE_FILE):
                with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
                    schedules = json.load(f)
            else:
                schedules = []
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")  # ← CORS 許可
            self.end_headers()
            self.wfile.write(json.dumps(schedules, ensure_ascii=False).encode("utf-8"))
        else:
            super().do_GET()

# Render では PORT は環境変数で指定される
port = int(os.environ.get("PORT", PORT))
with socketserver.TCPServer(("", port), Handler) as httpd:
    print(f"Serving at port {port}")
    httpd.serve_forever()
