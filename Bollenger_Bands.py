import MetaTrader5 as mt5
import pandas as pd
import time


TIMEFRAME = mt5.TIMEFRAME_M1
VOLUME = 0.1     # Trade Volume
DEVIATION = 20   # Deviation for Order Slippage
MAGIC = 10
SMA_PERIOD = 20  # SMA Period for Bollinger Band
STANDARD_DEVIATIONS = 2  # Number of Deviations for calculation of Bollinger Bands
TP_SD = 2        # Number of Deviations for Take Profit
SL_SD = 3        # Number of Deviations for Stop Loss
# function to send a market order

def positions_get(symbol):
    return mt5.positions_get(symbol=symbol)

def market_order(symbol, volume, order_type, deviation, magic, stoploss, takeprofit):
    tick = mt5.symbol_info_tick(symbol)

    order_dict = {'buy': 0, 'sell': 1}
    price_dict = {'buy': tick.ask, 'sell': tick.bid}

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_dict[order_type],
        "price": price_dict[order_type],
        "deviation": deviation,
        "magic": magic,
        "sl": stoploss,
        'tp': takeprofit,
        "comment": "python market order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    order_result = mt5.order_send(request)
    print(order_result)

    return order_result


def get_signal(symbol):
    bars = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 1, SMA_PERIOD)

    # converting to datafrane
    df = pd.DataFrame(bars)
    # a simple moving average

    sma = df['close'].mean()

    #standard deviation
    sd = df['close'].std()
    # print(df.close)

    #lower band
    lower_band  = sma - STANDARD_DEVIATIONS * sd
    #upper band
    upper_band = sma + STANDARD_DEVIATIONS * sd

    #last close.price
    last_close_price = df.iloc[-1]['close']

    # print(last_close_price, upper_band)

    # finding signal
    if last_close_price < lower_band:
        return 'buy', sd
    elif last_close_price > upper_band:
        return 'sell', sd
    else:
        return [None, None]

def start_robot(symbol):
    position = positions_get(symbol)

    if not position:
        signal, standard_deviation = get_signal(symbol)

        tick = mt5.symbol_info_tick(symbol)

        if signal == 'buy':
            market_order(symbol, VOLUME, 'buy', DEVIATION, MAGIC, tick.bid - SL_SD * standard_deviation, tick.bid + TP_SD * standard_deviation)

        elif signal == 'sell':
            market_order(symbol, VOLUME, 'sell', DEVIATION, MAGIC, tick.bid + SL_SD * standard_deviation, tick.bid - TP_SD * standard_deviation)



initialize = mt5.initialize()

login = 51465031
password = 'ma5M7GU8W'
server = 'Alpari-MT5-Demo'

mt5.login(login=login, password=password, server=server)

if initialize:
    print('Connected to MetaTrader5')
    print('Login=>' , mt5.account_info().login)
    print('Balance=>', mt5.account_info().balance)
    print('Server=>', mt5.account_info().server)

# strategy loop
while True:
    # strategy logic
    # if no positions are open

    start_robot("EURUSD_i")
    # start_robot("XAUUSD_i")

    # check for signal every 1 second
    time.sleep(1)
