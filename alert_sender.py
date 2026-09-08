"""alert_sender.py — 경보 목록을 만들어 n8n Webhook 으로 POST"""
import requests

N8N_WEBHOOK_URL = "http://localhost:5678/webhook/d5188867-b93b-4842-bc1f-a136bbd5f01a"
STUDENT_NAME = "YU JIWON"

alerts = [
    {"ip": "1.2.3.114", "level": 10, "rule": "5712"},  # 거부(deny) 될 것
    {"ip": "192.168.0.10", "level": 3, "rule": "0001"},  # 허용(allow) 될 것
]

payload = {"student": STUDENT_NAME, "alerts": alerts}

try:
    res = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=5)
    print(f"[n8n] POST {N8N_WEBHOOK_URL} -> {res.status_code}")
except requests.RequestException as e:
    print(f"전송 실패: {e}")
