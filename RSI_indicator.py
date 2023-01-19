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
    df = pd.DataFrame(bars)
    df = df[['time', 'open', 'high', 'low', 'close']]
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def ATR(df):
    atr_period = 14  # defining the atr period to 14

    # calculating the range of each candle
    df['range'] = df['high'] - df['low']

    # calculating the average value of ranges
    df['atr_14'] = df['range'].rolling(atr_period).mean()

    return df['atr_14'].values[-1]


def trading_takeprofit(position, tick):
    position = position[0]
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
            return result



initialize = mt5.initialize()
if initialize:
    login = 51466985
    password = 'N4ry9n7vi'
    server = 'Alpari-MT5-Demo'

    mt5.login(login=login, password=password, server=server)
    print('Connected to MetaTrader5')
    print('Login=>' , mt5.account_info().login)
    print('Balance=>', mt5.account_info().balance)
    print('Server=>', mt5.account_info().server)

    SYMBOL = "EURUSD_i"
    # lot = 0.01
    # TIMEFRAME = mt5.TIMEFRAME_M1
    VOLUME = 0.1  # Trade Volume
    DEVIATION = 20  # Deviation for Order Slippage
    MAGIC = 10
    # strategy loop
    while True:
        # strategy logic
        # if no positions are open
        position = positions_get(SYMBOL)
        tick = mt5.symbol_info_tick(SYMBOL)
        if not position:
            df = get_df(SYMBOL, mt5.TIMEFRAME_M20, 0, 24)
            rsi = RSI(df)
            atr = ATR(df)
            if rsi < 30:
                market_order(symbol=SYMBOL, volume=VOLUME, order_type="buy", deviation=DEVIATION, magic=MAGIC,
                             stoploss=tick.bid - atr, takeprofit=tick.ask + atr)
                print(atr)
            elif rsi > 70:
                market_order(symbol=SYMBOL, volume=VOLUME, order_type="sell", deviation=DEVIATION, magic=MAGIC,
                             stoploss=tick.ask + atr, takeprofit=tick.bid - atr)
                print(atr)
        else:
            answer_takeprofit = trading_takeprofit(position=position, tick=tick)  # 'Request executed'  or  'Invalid stops'  or  'Request rejected'
            if answer_takeprofit:
                print(answer_takeprofit[7])

        time.sleep(1)

else:
    print('No connection')

