import requests

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
API_KEY = "CG-uU7js3FhpTcY1huVkmJnYUsf"

def get_basic_market_data(coin_id):
    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}"
    headers = {
        "x-cg-demo-api-key": API_KEY
    }
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false",
        "sparkline": "false"
    }

    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()
    data = res.json()

    market_data = data["market_data"]
    return {
        "price": market_data["current_price"]["usd"],
        "change_1h": market_data["price_change_percentage_1h_in_currency"]["usd"],
        "market_cap_rank": market_data["market_cap_rank"],
        "total_volume": market_data["total_volume"]["usd"]
    }

def get_ohlc_data(coin_id):
    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/ohlc"
    headers = {
        "x-cg-demo-api-key": API_KEY
    }
    params = {
        "vs_currency": "usd",
        "days": 14
    }

    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()
    raw = res.json()

    return [entry[4] for entry in raw]  

def calculate_rsi(closes, period=14):
    if len(closes) <= period:
        raise ValueError("Not enough data to calculate RSI")

    changes = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [max(change, 0) for change in changes]
    losses = [abs(min(change, 0)) for change in changes]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    rs = avg_gain / avg_loss if avg_loss != 0 else float("inf")
    rsi = 100 - (100 / (1 + rs))

    for i in range(period, len(changes)):
        gain = gains[i]
        loss = losses[i]
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        rs = avg_gain / avg_loss if avg_loss != 0 else float("inf")
        rsi = 100 - (100 / (1 + rs))

    return rsi

def calculate_macd(closes, short=12, long=26, signal=9):
    def ema(data, period):
        k = 2 / (period + 1)
        ema_list = [data[0]]
        for price in data[1:]:
            ema_list.append(price * k + ema_list[-1] * (1 - k))
        return ema_list

    if len(closes) < long + signal:
        raise ValueError("Not enough data to calculate MACD")

    ema_short = ema(closes, short)
    ema_long = ema(closes, long)
    macd_line = [s - l for s, l in zip(ema_short[-len(ema_long):], ema_long)]
    signal_line = ema(macd_line, signal)
    histogram = [m - s for m, s in zip(macd_line[-len(signal_line):], signal_line)]

    return histogram[-1]

def get_coin_features(coin_id):
    try:
        market = get_basic_market_data(coin_id)
        closes = get_ohlc_data(coin_id)
        rsi = round(calculate_rsi(closes), 2)
        macd_hist = round(calculate_macd(closes), 5)

        return {
            "success": True,
            "data": {
                "current_price": round(market["price"], 5),
                "price_change_1h": round(market["change_1h"], 5),
                "market_cap_rank": market["market_cap_rank"],
                "total_volume": round(market["total_volume"], 2),
                "rsi": rsi,
                "macd_histogram": macd_hist
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

