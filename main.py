import yfinance as yf
import requests
import os
import json
from datetime import datetime
import pytz

LINE_ACCESS_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
LINE_USER_ID = os.environ.get('LINE_USER_ID')

# 設定監控標的與成本 (請依需求修改成本)
WATCH_CONFIG = {
    "0050.TW": 78.31,
    "00929.TW": 18.32,
    "2646.TW": 25.81
}

def send_line_push(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"}
    payload = {"to": LINE_USER_ID, "messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=payload)

def monitor():
    tw_tz = pytz.timezone('Asia/Taipei')
    now_str = datetime.now(tw_tz).strftime("%H:%M")
    
    # 讀取上一次儲存的價格 (如果有)
    history_file = "price_history.json"
    last_prices = {}
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            last_prices = json.load(f)

    status_report = [f"📊 股市波動回報 ({now_str})"]
    current_prices_to_save = {}

    for stock_id, cost in WATCH_CONFIG.items():
        try:
            stock = yf.Ticker(stock_id)
            price = stock.fast_info['last_price']
            current_prices_to_save[stock_id] = price
            
            # 1. 計算與成本的總損益
            total_profit_pct = ((price - cost) / cost) * 100
            total_icon = "💰" if total_profit_pct >= 0 else "📉"
            
            # 2. 計算與「上次回報」的波動幅
            if stock_id in last_prices:
                diff_pct = ((price - last_prices[stock_id]) / last_prices[stock_id]) * 100
                if diff_pct > 0:
                    wave_str = f"📈 較上次 +{diff_pct:.2f}%"
                elif diff_pct < 0:
                    wave_str = f"📉 較上次 {diff_pct:.2f}%"
                else:
                    wave_str = "➡️ 持平"
            else:
                wave_str = "🆕 今日首報"

            status_report.append(f"{total_icon} {stock_id} (成本:{cost})")
            status_report.append(f"   現價:{price:.2f} (總:{total_profit_pct:+.2f}%)")
            status_report.append(f"   {wave_str}")
            status_report.append("-" * 15)
        except:
            status_report.append(f"❌ {stock_id}: 讀取失敗")

    # 儲存目前的價格供下次使用
    with open(history_file, "w") as f:
        json.dump(current_prices_to_save, f)

    send_line_push("\n".join(status_report))

if __name__ == "__main__":
    monitor()
