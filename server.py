from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)  # 全サイトからのアクセスを許可（必要なら特定ドメインに絞ってください）

SCHEDULE_FILE = "schedule.json"

# 初期化
if not os.path.exists(SCHEDULE_FILE):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

@app.route("/schedule", methods=["GET"])
def get_schedule():
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/schedule", methods=["POST"])
def post_schedule():
    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()
    checked = request.form.get("checked", "false").lower() == "true"

    if not name or not message:
        return jsonify({"error": "invalid"}), 400

    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        schedules = json.load(f)

    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    schedules.append({"name": name, "message": message, "time": now, "checked": checked})

    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(schedules, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "ok"}), 200

@app.route("/check", methods=["POST"])
def update_check():
    # クライアントは index（行番号）を送る想定
    try:
        idx = int(request.form.get("index", -1))
    except:
        return jsonify({"error": "invalid index"}), 400
    flag = request.form.get("checked", "false").lower() == "true"

    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        schedules = json.load(f)

    if 0 <= idx < len(schedules):
        schedules[idx]["checked"] = flag
        with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
            json.dump(schedules, f, ensure_ascii=False, indent=2)
        return jsonify({"status": "ok"})
    return jsonify({"error": "index out of range"}), 400

@app.route("/")
def root():
    return "HBS schedule API running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
