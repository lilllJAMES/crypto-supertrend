import time
import threading
import requests
import pandas as pd
import numpy as np
from flask import Flask, jsonify, make_response

app = Flask(__name__)

import os
# --- Configuration ---
PORT = int(os.environ.get('PORT', 8001))
SYMBOLS_LIMIT = 100      # Restored to 100 for full list
REFRESH_INTERVAL = 180   # seconds (3 min) - Increased interval to prevent API bans
TIMEFRAMES = ['15m', '1H', '4H', '1D']
TF_MAP = {'15m': '15m', '1H': '1H', '4H': '4H', '1D': '1D'} 

# Proxy Configuration
import os
PROXY_URL = os.environ.get('HTTPS_PROXY') # e.g., 'http://127.0.0.1:7890'
PROXIES = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None

if PROXY_URL:
    print(f"Using Proxy: {PROXY_URL}")

# --- In-Memory Cache ---
# Replaces Redis for this Python version
CACHE = {
    "data": {
        "coins": [],
        "lastUpdated": None
    },
    "lock": threading.Lock()
}

# --- SuperTrend Calculation ---
def calculate_supertrend(df, period=10, multiplier=3):
    """
    Calculates SuperTrend indicator.
    Returns 'UP' or 'DOWN' for the last candle.
    """
    if len(df) < period + 1:
        return 'N/A'

    high = df['high'].astype(float).values
    low = df['low'].astype(float).values
    close = df['close'].astype(float).values

    # TR Calculation
    tr1 = high - low
    tr2 = np.abs(high - np.roll(close, 1))
    tr3 = np.abs(low - np.roll(close, 1))
    tr = np.maximum(tr1, np.maximum(tr2, tr3))
    tr[0] = tr1[0] # First TR is High - Low

    # ATR Calculation (RMA/Wilder's Smoothing usually, but here we use the JS logic: alpha * tr + (1-alpha) * prev)
    # The JS implementation used: alpha = 1/period. curAtr = alpha * tr + (1-alpha) * prevAtr
    atr = np.zeros_like(tr)
    atr[0] = tr[0]
    alpha = 1.0 / period
    for i in range(1, len(tr)):
        atr[i] = alpha * tr[i] + (1 - alpha) * atr[i-1]

    # Basic Bands
    hl2 = (high + low) / 2
    basic_upper = hl2 + multiplier * atr
    basic_lower = hl2 - multiplier * atr

    # Final Bands & SuperTrend
    final_upper = np.zeros_like(basic_upper)
    final_lower = np.zeros_like(basic_lower)
    supertrend = np.zeros_like(close)
    trend = np.zeros_like(close, dtype=bool) # True = UP, False = DOWN

    # Initialize first value
    final_upper[0] = basic_upper[0]
    final_lower[0] = basic_lower[0]
    supertrend[0] = final_lower[0]
    trend[0] = True

    for i in range(1, len(close)):
        # Final Upper
        if basic_upper[i] < final_upper[i-1] or close[i-1] > final_upper[i-1]:
            final_upper[i] = basic_upper[i]
        else:
            final_upper[i] = final_upper[i-1]

        # Final Lower
        if basic_lower[i] > final_lower[i-1] or close[i-1] < final_lower[i-1]:
            final_lower[i] = basic_lower[i]
        else:
            final_lower[i] = final_lower[i-1]

        # Trend Determination
        prev_st = supertrend[i-1]
        if prev_st == final_upper[i-1] and close[i] <= final_upper[i]:
            trend[i] = False
            supertrend[i] = final_upper[i]
        elif prev_st == final_upper[i-1] and close[i] > final_upper[i]:
            trend[i] = True
            supertrend[i] = final_lower[i]
        elif prev_st == final_lower[i-1] and close[i] >= final_lower[i]:
            trend[i] = True
            supertrend[i] = final_lower[i]
        elif prev_st == final_lower[i-1] and close[i] < final_lower[i]:
            trend[i] = False
            supertrend[i] = final_upper[i]
        else:
            # Fallback (should be covered above, but just in case)
            if close[i] > final_upper[i-1]:
                trend[i] = True
            elif close[i] < final_lower[i-1]:
                trend[i] = False
            else:
                trend[i] = trend[i-1]
            
            supertrend[i] = final_lower[i] if trend[i] else final_upper[i]

    return 'UP' if trend[-1] else 'DOWN'

# --- Data Fetching Logic ---
def fetch_market_cap_rankings():
    """Fetch top coins by market cap from CoinCap API"""
    try:
        # Try CoinCap first
        url = f"https://api.coincap.io/v2/assets?limit={SYMBOLS_LIMIT}"
        # CoinCap might block proxies, try without first if PROXIES is set, but usually better with proxy if user needs it
        # Actually user has PROXY_URL, so let's use it.
        # But wait, the error was NameResolutionError, maybe proxy issue or DNS.
        # Let's add a fallback to a hardcoded list of top 20 just in case, or just return empty.
        resp = requests.get(url, timeout=10, proxies=PROXIES)
        data = resp.json()
        if 'data' not in data:
            return []
        return [item['symbol'] for item in data['data']]
    except Exception as e:
        print(f"Error fetching market cap rankings: {e}")
        # Fallback to a hardcoded list of top 20 major coins to ensure at least these are at top
        return ['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'USDC', 'ADA', 'AVAX', 'DOGE', 
                'TRX', 'LINK', 'DOT', 'MATIC', 'WBTC', 'LTC', 'DAI', 'SHIB', 'BCH', 'LEO']

def fetch_top_tickers():
    try:
        # 1. Fetch OKX Tickers
        url = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"
        resp = requests.get(url, timeout=10, proxies=PROXIES)
        data = resp.json()
        if data['code'] != '0':
            print(f"Error fetching tickers: {data}")
            return []
        
        tickers = data['data']
        # Filter USDT swaps and map by symbol
        usdt_tickers_map = {}
        for t in tickers:
            if t['instId'].endswith('-USDT-SWAP'):
                symbol = t['instId'].split('-')[0]
                usdt_tickers_map[symbol] = t

        # 2. Fetch Market Cap Rankings
        ranked_symbols = fetch_market_cap_rankings()
        
        final_tickers = []
        
        # 3. Add coins based on Market Cap Rank
        if ranked_symbols:
            print(f"Using Market Cap ranking ({len(ranked_symbols)} symbols)... First 5: {ranked_symbols[:5]}")
            for sym in ranked_symbols:
                if sym in usdt_tickers_map:
                    final_tickers.append(usdt_tickers_map[sym])
                else:
                    # Debug: Why is a ranked symbol not in map?
                    if sym in ['BTC', 'ETH', 'SOL']:
                        print(f"Warning: {sym} from ranking not found in OKX tickers map!")

        # 4. If we don't have enough (or API failed), fill with Volume-based top coins
        if len(final_tickers) < SYMBOLS_LIMIT:
            print(f"Not enough market cap coins ({len(final_tickers)}), filling with volume...")
            # Sort all available by volume
            all_sorted = sorted(usdt_tickers_map.values(), key=lambda x: float(x.get('volCcy24h', 0)), reverse=True)
            for t in all_sorted:
                if t not in final_tickers:
                    final_tickers.append(t)
                    if len(final_tickers) >= SYMBOLS_LIMIT:
                        break
        
        print(f"Final top 3 tickers: {[t['instId'] for t in final_tickers[:3]]}")

        # --- Force BTC to #1 ---
        # Because we must respect the King
        btc_found_idx = -1
        for i, t in enumerate(final_tickers):
            if t['instId'].startswith('BTC-'):
                btc_found_idx = i
                break
        
        if btc_found_idx > 0:
            print(f"Moving BTC from index {btc_found_idx} to 0")
            btc_ticker = final_tickers.pop(btc_found_idx)
            final_tickers.insert(0, btc_ticker)
        elif btc_found_idx == -1 and 'BTC' in usdt_tickers_map:
            print("Force inserting BTC at top")
            final_tickers.insert(0, usdt_tickers_map['BTC'])
            if len(final_tickers) > SYMBOLS_LIMIT:
                final_tickers.pop()
        # -----------------------

        return final_tickers[:SYMBOLS_LIMIT]
    except Exception as e:
        print(f"Exception fetching tickers (Network Error?): {e}")
        return []

def fetch_candles(instId, bar):
    try:
        # ... bar mapping ...
        okx_bar = bar
        if bar == '1H': okx_bar = '1H'
        if bar == '4H': okx_bar = '4H'
        if bar == '1D': okx_bar = '1D'
        
        url = f"https://www.okx.com/api/v5/market/candles?instId={instId}&bar={okx_bar}&limit=100"
        resp = requests.get(url, timeout=10, proxies=PROXIES)
        data = resp.json()
        if data['code'] != '0':
            return []
        
        # ... processing ...
        candles = data['data']
        # Convert to list of dicts for DataFrame
        formatted = []
        for c in candles: # candles are usually newest first
            formatted.append({
                'ts': int(c[0]),
                'open': float(c[1]),
                'high': float(c[2]),
                'low': float(c[3]),
                'close': float(c[4])
            })
        # Sort oldest to newest for calculation
        formatted.sort(key=lambda x: x['ts'])
        return formatted
    except Exception as e:
        print(f"Error fetching candles for {instId} {bar}: {e}")
        return []

def update_job():
    """Background job to update data"""
    while True:
        print(f"[{time.strftime('%H:%M:%S')}] Starting update job... Limit: {SYMBOLS_LIMIT}")
        start_time = time.time()
        
        tickers = fetch_top_tickers()
        print(f"Fetched {len(tickers)} tickers.")
        if not tickers:
            print("No tickers found, retrying in 10s...")
            time.sleep(10)
            continue

        results_map = {}
        
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def process_coin(ticker):
            instId = ticker['instId']
            symbol = instId.split('-')[0]
            try:
                price = float(ticker['last'])
                vol24h = float(ticker['volCcy24h'])
                open24h = float(ticker['open24h'])
                change24h = float(ticker['last']) - open24h
                changePercent = (change24h / open24h) * 100 if open24h else 0
            except:
                price = 0
                vol24h = 0
                changePercent = 0

            coin_data = {
                'symbol': symbol,
                'price': price,
                'change24h': changePercent,
                'volume24h': vol24h,
                'trends': {},
                'sparkline': []
            }

            # Fetch candles for each timeframe
            # To speed up, we can fetch these in parallel too, but maybe overkill.
            # Let's keep it simple inside the coin thread.
            for tf in TIMEFRAMES:
                candles = fetch_candles(instId, tf)
                if not candles:
                    coin_data['trends'][tf] = 'N/A'
                    continue
                
                # Use 1H candles for sparkline (last 24 points)
                if tf == '1H':
                     # Extract close prices for sparkline
                     closes = [c['close'] for c in candles]
                     # Keep last 24 points for 24h trend
                     coin_data['sparkline'] = closes[-24:]

                df = pd.DataFrame(candles)
                st = calculate_supertrend(df)
                coin_data['trends'][tf] = st
            
            return coin_data
        
        try:
            # Increased max_workers to 10 to speed up data fetching
            # 250 coins / 10 workers = 25 coins per worker (approx)
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_coin = {executor.submit(process_coin, t): t for t in tickers}
                for future in as_completed(future_to_coin):
                    try:
                        data = future.result()
                        results_map[data['symbol']] = data
                    except Exception as exc:
                        print(f"Coin processing generated an exception: {exc}")

            # Reconstruct list in original order to maintain ranking
            results = []
            for t in tickers:
                sym = t['instId'].split('-')[0]
                if sym in results_map:
                    results.append(results_map[sym])
            
            # Update Cache
            with CACHE['lock']:
                CACHE['data'] = {
                    "coins": results,
                    "lastUpdated": int(time.time() * 1000)
                }
            
            elapsed = time.time() - start_time
            print(f"[{time.strftime('%H:%M:%S')}] Update finished in {elapsed:.2f}s. Next update in {REFRESH_INTERVAL}s.")
        except Exception as e:
            print(f"CRITICAL ERROR in update_job: {e}")
            import traceback
            traceback.print_exc()

        time.sleep(REFRESH_INTERVAL)

# --- Routes ---
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    with CACHE['lock']:
        data = CACHE['data']
    response = make_response(jsonify(data))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/api/health', methods=['GET'])
def health():
    with CACHE['lock']:
        coin_count = len(CACHE['data']['coins'])
    response = make_response(jsonify({
        "status": "ok", 
        "backend": "python-flask",
        "coins_loaded": coin_count
    }))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

# Start background thread (Global scope for Gunicorn)
# Ensure it only starts once
if not any(t.name == 'BackgroundUpdater' for t in threading.enumerate()):
    t = threading.Thread(target=update_job, daemon=True, name='BackgroundUpdater')
    t.start()
    print("Background update thread started.")

if __name__ == '__main__':
    print(f"Starting Python backend on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=False)
