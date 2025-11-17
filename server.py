from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

SCHEDULE_FILE = "schedule.json"


# --- 初期ファイル作成 ---
if not os.path.exists(SCHEDULE_FILE):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)


# --- データ読み書き関数 ---
def load_schedule():
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_schedule(data):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# --- API: 動作確認用 ---
@app.route("/")
def index():
    return jsonify({"status": "HBS schedule API running"})


# --- API: スケジュール取得 ---
@app.route("/schedule", methods=["GET"])
def get_schedule():
    return jsonify(load_schedule())


# --- API: スケジュール投稿 ---
@app.route("/schedule", methods=["POST"])
def add_schedule():
    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not message:
        return jsonify({"error": "invalid"}), 400

    data = load_schedule()
    data.append({
        "name": name,
        "message": message,
        "time": datetime.now().strftime("%Y/%m/%d %H:%M"),
        "checked": False,
    })

    save_schedule(data)
    return jsonify({"status": "ok"})


# --- API: チェック更新 ---
@app.route("/update_check", methods=["POST"])
def update_check():
    index = int(request.form.get("index", -1))
    checked = request.form.get("checked") == "true"

    data = load_schedule()
    if 0 <= index < len(data):
        data[index]["checked"] = checked
        save_schedule(data)

    return jsonify({"status": "ok"})


# --- Main ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
