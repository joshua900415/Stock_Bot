import yfinance as yf
import requests
import os
import json
from datetime import datetime
import pytz

LINE_ACCESS_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
LINE_USER_ID = os.environ.get('LINE_USER_ID')

# 設定監控標的：有成本的寫數字，沒成本的寫 None
WATCH_CONFIG = {
    "0050.TW": 78.31,
    "00929.TW": 18.35,
    "2646.TW": 25.00,
    "BTC-USD": None  # 比特幣不設成本，僅看現價
}

def send_line_push(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"}
    payload = {"to": LINE_USER_ID, "messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=payload)

def monitor():
    tw_tz = pytz.timezone('Asia/Taipei')
    now_str = datetime.now(tw_tz).strftime("%H:%M")
    
    # 讀取上一次儲存的價格
    history_file = "price_history.json"
    last_prices = {}
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                last_prices = json.load(f)
        except:
            last_prices = {}

    status_report = [f"📊 股市/加密幣回報 ({now_str})"]
    current_prices_to_save = {}

    for stock_id, cost in WATCH_CONFIG.items():
        try:
            stock = yf.Ticker(stock_id)
            price = stock.fast_info['last_price']
            current_prices_to_save[stock_id] = price
            
            # --- 第一部分：成本損益 ---
            if cost is not None:
                total_profit_pct = ((price - cost) / cost) * 100
                total_icon = "💰" if total_profit_pct >= 0 else "📉"
                header_str = f"{total_icon} {stock_id} (成本:{cost})"
                detail_str = f"   現價:{price:.2f} (總:{total_profit_pct:+.2f}%)"
            else:
                # 沒成本的標的（如比特幣）
                header_str = f"₿ {stock_id} (即時報價)"
                # 比特幣通常數字很大，我們加上千分位逗號方便看
                detail_str = f"   現價: ${price:,.2f}"

            # --- 第二部分：較上次回報的波動 ---
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

            status_report.append(header_str)
            status_report.append(detail_str)
            status_report.append(f"   {wave_str}")
            status_report.append("-" * 15)
        except:
            status_report.append(f"❌ {stock_id}: 讀取失敗")

    # 儲存目前價格
    with open(history_file, "w") as f:
        json.dump(current_prices_to_save, f)

    send_line_push("\n".join(status_report))

if __name__ == "__main__":
    monitor()
