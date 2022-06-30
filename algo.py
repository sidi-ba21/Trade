import statistics

def SMA(data, period):
    return statistics.mean(data[len(data) - period:])

# Calculate the EMA for the given data and period
def EMA(data, period):
    ema = float(0)
    # Calculate the EMA for the given period
    for i in range(0, period):
        ema += data[i]
    ema = ema / period
    # Calculate the EMA for the next period
    for i in range(period, len(data)):
        ema = (data[i] - ema) * 2 / (period + 1) + ema
    return ema

def BollingerBands(data, sma,period):
    std = statistics.pstdev(data[-period:])
    upper_bb = sma + (2 * std)
    lower_bb = sma - (2 * std)
    return upper_bb, lower_bb

def BB_strategy(data, upper_bb, lower_bb):
    if data[-1] > lower_bb:
        return "Buy"
    elif data[-1] < upper_bb:
        return "Sell"
    else:
        return "no signal"

def RSI(data, period):
    up = 0
    down = 0
    # Calculate the up and down values for the past 14 days
    for i in range(0, period):
        if data[i] > data[i + 1]:
            up += data[i] - data[i + 1]
        else:
            down += data[i + 1] - data[i]
    # Calculate the RSI value for the past 14 days
    rs = up / down
    rsi = 100 - (100 / (1 + rs))
    return rsi

def MACD(data):
    ema_12 = EMA(data[len(data) - (12 + 1):], 12)
    ema_26 = EMA(data[len(data) - (16 + 1):], 16)
    macd = ema_12 - ema_26
    return macd