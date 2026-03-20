import yfinance as yf
import requests
import os
from datetime import datetime
import pytz

# 從 GitHub Secrets 讀取金鑰
LINE_ACCESS_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
LINE_USER_ID = os.environ.get('LINE_USER_ID')

WATCH_LIST = ["0050 成本79.31", "00929 成本18.32", "星宇航空 成本25.81"]

def send_line_push(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"}
    payload = {"to": LINE_USER_ID, "messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=payload)

def monitor():
    tw_tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tw_tz)
    current_hm = now.strftime("%H:%M")
    
    status_report = [f"📊 股市定時回報 ({current_hm})"]
    
    for stock_id in WATCH_LIST:
        try:
            stock = yf.Ticker(stock_id)
            info = stock.fast_info
            price = info['last_price']
            prev_close = info['previous_close']
            diff = price - prev_close
            
            if diff > 0:
                change_str = f"🔴 +{diff:.2f}"
            elif diff < 0:
                change_str = f"🟢 {diff:.2f}"
            else:
                change_str = f"⚪ 持平"
            status_report.append(f"🔹 {stock_id}: {price:.2f} ({change_str})")
        except:
            status_report.append(f"❌ {stock_id}: 讀取失敗")

    send_line_push("\n".join(status_report))

if __name__ == "__main__":
    monitor()
