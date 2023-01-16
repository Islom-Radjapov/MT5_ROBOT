import MetaTrader5 as mt5
import pandas as pd
import time

def positions_get(symbol):
    return mt5.positions_get(symbol=symbol)

def RSI(df):
    # setting the RSI Period
    rsi_period = 14

    # to calculate RSI, we first need to calculate the exponential weighted aveage gain and loss during the period
    df['gain'] = (df['close'] - df['open']).apply(lambda x: x if x > 0 else 0)
    df['loss'] = (df['close'] - df['open']).apply(lambda x: -x if x < 0 else 0)

    # here we use the same formula to calculate Exponential Moving Average
    df['ema_gain'] = df['gain'].ewm(span=rsi_period, min_periods=rsi_period).mean()
    df['ema_loss'] = df['loss'].ewm(span=rsi_period, min_periods=rsi_period).mean()

    # the Relative Strength is the ratio between the exponential avg gain divided by the exponential avg loss
    df['rs'] = df['ema_gain'] / df['ema_loss']

    # the RSI is calculated based on the Relative Strength using the following formula
    df['rsi_14'] = 100 - (100 / (df['rs'] + 1))

    return df['rsi_14']
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

initialize = mt5.initialize()

login = 51466985
password = 'N4ry9n7vi'
server = 'Alpari-MT5-Demo'

mt5.login(login=login, password=password, server=server)

# symbol = 'EURUSD_i'
# timeframe = mt5.TIMEFRAME_D1
# start_pos = 0
# num_bars = 1000

def get_df(symbol, timeframe, start_pos, num_bars):
    bars = mt5.copy_rates_from_pos(symbol, timeframe, start_pos, num_bars)
    df = pd.DataFrame(bars)
    df = df[['time', 'open', 'high', 'low', 'close']]
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

if initialize:
    print('Connected to MetaTrader5')
    print('Login=>' , mt5.account_info().login)
    print('Balance=>', mt5.account_info().balance)
    print('Server=>', mt5.account_info().server)

    symbol = "EURUSD_i"
    # lot = 0.01
    # strategy loop
    while True:
        # strategy logic
        # if no positions are open
        position = positions_get(symbol)
        if not position:
            df = get_df(symbol, mt5.TIMEFRAME_M15, 0, 1000)
            rsi = RSI(df)
            if rsi < 20:
                market_order(symbol, 0.01, "buy", 20, 10, stoploss, takeprofit)
            elif rsi > 80:
                market_order(symbol, 0.01, "sell", 20, 10, stoploss, takeprofit)


        # check for signal every 1 second
        time.sleep(1)
else:
    print('No connection')