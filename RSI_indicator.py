import MetaTrader5 as mt5
import pandas as pd
import time

def positions_get(symbol):
    return mt5.positions_get(symbol=symbol)

def RSI(df, periods = 14, ema = True):
    """
    Returns a pd.Series with the relative strength index.
    """
    close_delta = df['close'].diff()

    # Make two series: one for lower closes and one for higher closes
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)

    if ema == True:
        # Use exponential moving average
        ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
        ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    else:
        # Use simple moving average
        ma_up = up.rolling(window=periods, adjust=False).mean()
        ma_down = down.rolling(window=periods, adjust=False).mean()

    rsi = ma_up / ma_down
    rsi = 100 - (100/(1 + rsi))
    return rsi.values[-1]

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

def trading_takeprofit(position, tick):
    if position.type == 1: # sell
        distance = abs(round(tick.bid - position.tp, 5))
        if distance <= 0.0001:
            tp = tick.bid - 0.0002
            sl = tick.ask + 0.0002
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": position.type,
                "position": position.ticket,
                "price_open": position.price_open,
                "sl": sl,
                "tp": tp,
                "magic": position.magic,
                "comment": "python script open",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
                "ENUM_ORDER_STATE": mt5.ORDER_FILLING_RETURN,
            }

            result = mt5.order_send(request)
            print("Profit")
            return result


    elif position.type == 0: # buy
        distance = abs(round(position.tp - tick.ask, 5))
        if distance <= 0.0001:
            tp = tick.ask + 0.0002
            sl = tick.bid - 0.0002
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": position.type,
                "position": position.ticket,
                "price_open": position.price_open,
                "sl": sl,
                "tp": tp,
                "magic": position.magic,
                "comment": "python script open",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
                "ENUM_ORDER_STATE": mt5.ORDER_FILLING_RETURN,
            }

            result = mt5.order_send(request)
            print("Profit")
            return result


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
        VOLUME = 0.1
        df = get_df(SYMBOL, TIMEFRAME, 0, 24)
        atr = ATR(df)

        if not position:
            rsi = RSI(df)

            if rsi < 20:
                market_order(symbol=SYMBOL, volume=VOLUME, order_type="buy", deviation=DEVIATION, magic=MAGIC,
                             stoploss=tick.bid - atr, takeprofit=tick.ask + atr)
            elif rsi > 80:
                market_order(symbol=SYMBOL, volume=VOLUME, order_type="sell", deviation=DEVIATION, magic=MAGIC,
                             stoploss=tick.ask + atr, takeprofit=tick.bid - atr)
        else:
            position = position[0]
            if position.type == 1 : # sell
                if position.bid <= tick.bid + 0.001:
                    VOLUME += VOLUME + 0.0002
                    market_order(symbol=SYMBOL, volume=VOLUME, order_type="sell", deviation=DEVIATION, magic=MAGIC, takeprofit=tick.bid - atr)
            elif position.type == 0: # buy
                if position.ask <= tick.ask + 0.001:
                    VOLUME += VOLUME + 0.0002
                    market_order(symbol=SYMBOL, volume=VOLUME, order_type="buy", deviation=DEVIATION, magic=MAGIC, takeprofit=tick.bid + atr)
            else:
                trading_takeprofit(position=position, tick=tick)
        


        time.sleep(1)

else:
    print('No connection')

