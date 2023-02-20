import MetaTrader5 as mt5
import time
order_type = {0: 'BUY', 1: 'SELL'}


def Close_profit():
    for position in mt5.positions_get(symbol=SYMBOL):
        if position.profit >= 0.20:
            mt5.Close(position.symbol, ticket=position.ticket)
            # time.sleep(0.00333)
            print(order_type[position.type], 'Profit=>', position.profit)



def Close_buy(symbol, comment=None):
    positions = mt5.positions_get(symbol=symbol)
    for pos in positions:
        if pos.type == 0:
            for tries in range(10):
                info = mt5.symbol_info_tick(symbol)
                if info is None:
                    return None
                r = mt5._RawOrder(mt5.ORDER_TYPE_SELL, symbol, pos.volume, info.ask, comment, pos.ticket)
                # check results
                if r is None:
                    return None
                if r.retcode != mt5.TRADE_RETCODE_REQUOTE and r.retcode != mt5.TRADE_RETCODE_PRICE_OFF:
                    break
            print('BUY Profit=>', pos.profit)



def Close_sell(symbol, comment=None):
    positions = mt5.positions_get(symbol=symbol)
    for pos in positions:
        if pos.type == 1:
            for tries in range(10):
                info = mt5.symbol_info_tick(symbol)
                if info is None:
                    return None
                r = mt5._RawOrder(mt5.ORDER_TYPE_BUY, symbol, pos.volume, info.ask, comment, pos.ticket)
                # check results
                if r is None:
                    return None
                if r.retcode != mt5.TRADE_RETCODE_REQUOTE and r.retcode != mt5.TRADE_RETCODE_PRICE_OFF:
                    break
        print('SELL Profit=>', pos.profit)



def Count_order(positions):
    num_buy = 0
    num_sell = 0
    for pos in positions:
        if pos.type == 0:
            num_buy += 1
        else:
            num_sell += 1
    return num_buy, num_sell



def Count_position():
    list_buy = []
    list_sell = []
    for pos in mt5.positions_get(symbol=SYMBOL):
        if pos.type == 0:
            list_buy.append(pos)
        elif pos.type == 1:
            list_sell.append(pos)
    return list_buy, list_sell



def add_order_buy(buy_list):
    lengh = len(buy_list)
    if lengh == 1:
        if buy_list[-1].profit <= -3:
            BUY1 = mt5.Buy(symbol=SYMBOL, volume=0.02)
            print(f'Open=> {order_type[BUY1[-1].type]} volume', BUY1[-1].volume)
    elif lengh == 2:
        if buy_list[-1].profit <= -6:
            BUY1 = mt5.Buy(symbol=SYMBOL, volume=0.03)
            print(f'Open=> {order_type[BUY1[-1].type]} volume', BUY1[-1].volume)
    elif lengh == 3:
        if buy_list[-1].profit <= -9:
            BUY1 = mt5.Buy(symbol=SYMBOL, volume=0.09)
            print(f'Open=> {order_type[BUY1[-1].type]} volume', BUY1[-1].volume)
    elif lengh == 4:
        if buy_list[-1].profit <= -27:
            BUY1 = mt5.Buy(symbol=SYMBOL, volume=0.23)
            print(f'Open=> {order_type[BUY1[-1].type]} volume', BUY1[-1].volume)
    elif lengh == 5:
        if buy_list[-1].profit <= -69:
            BUY1 = mt5.Buy(symbol=SYMBOL, volume=0.47)
            print(f'Open=> {order_type[BUY1[-1].type]} volume', BUY1[-1].volume)



def add_order_sell(sell_list):
    lengh = len(sell_list)
    if lengh == 1:
        if sell_list[-1].profit <= -3:
            SELL1 = mt5.Sell(symbol=SYMBOL, volume=0.02)
            print(f'Open=> {order_type[SELL1[-1].type]} volume', SELL1[-1].volume)
    elif lengh == 2:
        if sell_list[-1].profit <= -6:
            SELL1 = mt5.Sell(symbol=SYMBOL, volume=0.03)
            print(f'Open=> {order_type[SELL1[-1].type]} volume', SELL1[-1].volume)
    elif lengh == 3:
        if sell_list[-1].profit <= -9:
            SELL1 = mt5.Sell(symbol=SYMBOL, volume=0.09)
            print(f'Open=> {order_type[SELL1[-1].type]} volume', SELL1[-1].volume)
    elif lengh == 4:
        if sell_list[-1].profit <= -27:
            SELL1 = mt5.Sell(symbol=SYMBOL, volume=0.23)
            print(f'Open=> {order_type[SELL1[-1].type]} volume', SELL1[-1].volume)
    elif lengh == 5:
        if sell_list[-1].profit <= -69:
            SELL1 = mt5.Sell(symbol=SYMBOL, volume=0.47)
            print(f'Open=> {order_type[SELL1[-1].type]} volume', SELL1[-1].volume)




initialize = mt5.initialize()

if initialize:
    login = 51513413
    password = 's8ramreh'
    server = 'Alpari-MT5-Demo'
    # investor parol: 'anznie3n'
    mt5.login(login=login, password=password, server=server)

    print('Connected to MetaTrader5')
    print('Login=>', mt5.account_info().login)
    print('Server=>', mt5.account_info().server)
    print('Balance=>', mt5.account_info().balance)

    SYMBOL = 'EURUSD'

    order_type = {0: 'BUY', 1: 'SELL'}
    while True:

        # qaysi positsiyada order yo bosa shu positsiyada order ochadi
        buy, sell = Count_order(positions=mt5.positions_get(symbol=SYMBOL))
        if buy == 0:
            BUY = mt5.Buy(symbol=SYMBOL, volume=0.01)
            print(f'Open=> {order_type[BUY[-1].type]} volume', BUY[-1].volume)
        if sell == 0:
            SELL = mt5.Sell(symbol=SYMBOL, volume=0.01)
            print(f'Open=> {order_type[SELL[-1].type]} volume', SELL[-1].volume)


        # qaysi order minusga kirsa shu pozitsiyaga order qoshadi
        buy_list, sell_list = Count_position()
        add_order_buy(buy_list=buy_list)
        add_order_sell(sell_list=sell_list)


        buy_list, sell_list = Count_position()
        # buy orderla kutganimizde foyda keltirsa barchasini yopadi
        if buy_list:
            if buy_list[-1].volume * 2 * 10 <= buy_list[-1].profit:
                Close_buy(symbol=SYMBOL)
        # sel orderla kutganimizde foyda keltirsa barchasini yopadi
        if sell_list:
            if sell_list[-1].volume * 2 * 10 <= sell_list[-1].profit:
                Close_sell(symbol=SYMBOL)

else:
    print('No connection')