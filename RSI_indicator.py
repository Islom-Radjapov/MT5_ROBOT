import MetaTrader5 as mt5
import pandas as pd
import time

def positions_get(symbol):
    return mt5.positions_get(symbol=symbol)

def RSI(df):

    # to calculate RSI, we first need to calculate the exponential weighted aveage gain and loss during the period
    df['gain'] = (df['close'] - df['open']).apply(lambda x: x if x > 0 else 0)
    df['loss'] = (df['close'] - df['open']).apply(lambda x: -x if x < 0 else 0)

    # here we use the same formula to calculate Exponential Moving Average
    df['ema_gain'] = df['gain'].ewm(span=PERIOD, min_periods=PERIOD).mean()
    df['ema_loss'] = df['loss'].ewm(span=PERIOD, min_periods=PERIOD).mean()

    # the Relative Strength is the ratio between the exponential avg gain divided by the exponential avg loss
    df['rs'] = df['ema_gain'] / df['ema_loss']

    # the RSI is calculated based on the Relative Strength using the following formula
    df['rsi_14'] = 100 - (100 / (df['rs'] + 1))

    return df['rsi_14'].values[-1]

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
    order_result = mt5.order_send(request)[10]
    order_type = {0: 'buy', 1: 'sell'}
    print("ORDER=>", order_type[order_result.type], "price=>", round(order_result.price, 5),
          "stoploss=>", round(order_result.sl, 5), "takeprofit=>", round(order_result.tp, 5))
    return order_result

def get_df(symbol, timeframe, start_pos, num_bars):
    bars = mt5.copy_rates_from_pos(symbol, timeframe, start_pos, num_bars)
    df = pd.DataFrame(bars)[['time', 'open', 'high', 'low', 'close']]
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def ATR(df):
    # calculating the range of each candle
    df['range'] = df['high'] - df['low']

    # calculating the average value of ranges
    df['atr_14'] = df['range'].rolling(PERIOD).mean()

    return df['atr_14'].values[-1]


initialize = mt5.initialize()

if initialize:
    login = 51466985
    password = 'N4ry9n7vi'
    server = 'Alpari-MT5-Demo'

    mt5.login(login=login, password=password, server=server)

    print('Connected to MetaTrader5')
    print('Login=>' , mt5.account_info().login)
    print('Server=>', mt5.account_info().server)
    print('Balance=>', mt5.account_info().balance)

    SYMBOL = "EURUSD_i"
    TIMEFRAME = mt5.TIMEFRAME_M1
    VOLUME = 0.1
    DEVIATION = 20
    MAGIC = 10
    PERIOD = 14     # setting the RSI and ATR Period


    while True:

        position = positions_get(SYMBOL)
        tick = mt5.symbol_info_tick(SYMBOL)

        if not position:
            df = get_df(SYMBOL, TIMEFRAME, 0, 24)
            rsi = RSI(df)
            atr = 2 * ATR(df)

            if rsi < 30:
                market_order(symbol=SYMBOL, volume=VOLUME, order_type="buy", deviation=DEVIATION, magic=MAGIC,
                             stoploss=tick.bid - atr, takeprofit=tick.ask + atr)
            elif rsi > 70:
                market_order(symbol=SYMBOL, volume=VOLUME, order_type="sell", deviation=DEVIATION, magic=MAGIC,
                             stoploss=tick.ask + atr, takeprofit=tick.bid - atr)

        time.sleep(1)

else:
    print('No connection')

