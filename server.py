from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
JST = timezone(timedelta(hours=9))
from exchangelib import Credentials, Account, DELEGATE, Configuration, FaultTolerance
import json
import os

app = Flask(__name__)
CORS(app)

SCHEDULE_FILE = "schedule.json"
if not os.path.exists(SCHEDULE_FILE):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

def load_schedule():
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_schedule(data):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    return jsonify({"status": "running"})

@app.route("/schedule", methods=["GET"])
def get_schedule():
    return jsonify(load_schedule())

@app.route("/schedule", methods=["POST"])
def add_schedule():
    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()
    recipient = request.form.get("recipient", "全員").strip()
    checked = request.form.get("checked", "false").lower() == "true"

    if not name or not message:
        return jsonify({"error": "invalid"}), 400

    data = load_schedule()
    data.append({
        "name": name,
        "recipient": recipient,
        "message": message,
        "time": datetime.now(JST).strftime("%Y/%m/%d %H:%M"),
        "checked": checked
    })

    save_schedule(data)
    return jsonify({"status": "ok"})


@app.route("/update_check", methods=["POST"])
def update_check():
    idx = int(request.form.get("index", "-1"))
    checked = request.form.get("checked", "false").lower() == "true"
    data = load_schedule()
    if 0 <= idx < len(data):
        data[idx]["checked"] = checked
        save_schedule(data)
        return jsonify({"status": "ok"})
    return jsonify({"error": "index out of range"}), 400

# --- 未読メール取得 ---
@app.route("/unread-mails", methods=["GET"])
def get_unread_mails():
    try:
        # 環境変数または直接設定
        EMAIL = os.environ.get("OUTLOOK_EMAIL", "your_email@awi.co.jp")
        PASSWORD = os.environ.get("OUTLOOK_PASSWORD", "your_password")

        creds = Credentials(username=EMAIL, password=PASSWORD)
        account = Account(
            primary_smtp_address=EMAIL,
            credentials=creds,
            autodiscover=True,
            access_type=DELEGATE
        )

        # 受信トレイの未読メールを取得（最新10件）
        unread = account.inbox.filter(is_read=False).order_by('-datetime_received')[:10]

        mails = []
        for m in unread:
            mails.append({
                "subject": m.subject,
                "sender": m.sender.name if m.sender else "",
                "received": m.datetime_received.strftime("%Y/%m/%d %H:%M")
            })

        return jsonify({"count": len(mails), "mails": mails})

    except Exception as e:
        return jsonify({"error": str(e), "count": 0, "mails": []})
    

# 管理用：一覧取得（/list）
@app.route("/list", methods=["GET"])
def list_messages():
    data = load_schedule()
    print("DEBUG /list called, data:", data)  # ログ出力
    return jsonify(data)

# 管理用：削除（index）
@app.route("/delete", methods=["POST"])
def delete_message():
    idx = int(request.form.get("index", "-1"))
    data = load_schedule()
    if 0 <= idx < len(data):
        removed = data.pop(idx)
        save_schedule(data)
        print("DEBUG delete:", idx, removed)  # ログ出力
        return jsonify({"status": "deleted", "removed": removed})
    return jsonify({"error": "index out of range"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
