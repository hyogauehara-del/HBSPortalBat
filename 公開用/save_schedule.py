# save_schedule.py
import json
import cgi
import os
from datetime import datetime

print("Content-Type: application/json")
print("Access-Control-Allow-Origin: *")
print()

form = cgi.FieldStorage()
name = form.getvalue("name")
message = form.getvalue("message")

file_path = "schedule.json"

# 既存データを読み込み
if os.path.exists(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = []

# 新しい投稿を追加
data.append({
    "name": name,
    "message": message,
    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
})

# 保存
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(json.dumps({"status": "ok"}))
