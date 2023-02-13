import MetaTrader5 as mt5
import time



def Close_profit():
    order_type = {0: 'BUY', 1: 'SELL'}
    for position in mt5.positions_get(symbol=SYMBOL):
        if position.profit >= 0.20:
            mt5.Close(position.symbol, ticket=position.ticket)
            time.sleep(0.00333)
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
    time.sleep(0.00333)



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
    time.sleep(0.00333)



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
        if buy_list[-1].profit <= -1:
            mt5.Buy(symbol=SYMBOL, volume=0.06)
            time.sleep(0.00333)
            print('Open=> BUY volume', 0.06)
    elif lengh == 2:
        if buy_list[-1].profit <= -6:
            mt5.Buy(symbol=SYMBOL, volume=0.36)
            time.sleep(0.00333)
            print('Open=> BUY volume', 0.36)
    elif lengh == 3:
        if buy_list[-1].profit <= -36:
            mt5.Buy(symbol=SYMBOL, volume=2.16)
            time.sleep(0.00333)
            print('Open=> BUY volume', 2.16)
    elif lengh == 4:
        if buy_list[-1].profit <= -216:
            mt5.Buy(symbol=SYMBOL, volume=12.96)
            time.sleep(0.00333)
            print('Open=> BUY volume', 12.96)
    elif lengh == 5:
        if buy_list[-1].profit <= -1296:
            mt5.Buy(symbol=SYMBOL, volume=77.76)
            time.sleep(0.00333)
            print('Open=> BUY volume', 77.76)



def add_order_sell(sell_list):
    lengh = len(sell_list)
    if lengh == 1:
        if sell_list[-1].profit <= -1:
            mt5.Sell(symbol=SYMBOL, volume=0.06)
            time.sleep(0.00333)
            print('Open=> SELL volume', 0.06)
    elif lengh == 2:
        if sell_list[-1].profit <= -6:
            mt5.Sell(symbol=SYMBOL, volume=0.36)
            time.sleep(0.00333)
            print('Open=> SELL volume', 0.36)
    elif lengh == 3:
        if sell_list[-1].profit <= -36:
            mt5.Sell(symbol=SYMBOL, volume=2.16)
            time.sleep(0.00333)
            print('Open=> SELL volume', 2.16)
    elif lengh == 4:
        if sell_list[-1].profit <= -216:
            mt5.Sell(symbol=SYMBOL, volume=12.96)
            time.sleep(0.00333)
            print('Open=> SELL volume', 12.96)
    elif lengh == 5:
        if sell_list[-1].profit <= -1296:
            mt5.Sell(symbol=SYMBOL, volume=77.76)
            time.sleep(0.00333)
            print('Open=> SELL volume', 77.76)




initialize = mt5.initialize()

if initialize:
    login = 51508814
    password = '1dnxwlpf'
    server = 'Alpari-MT5-Demo'
    # investor parol: 'anznie3n'
    mt5.login(login=login, password=password, server=server)

    print('Connected to MetaTrader5')
    print('Login=>', mt5.account_info().login)
    print('Server=>', mt5.account_info().server)
    print('Balance=>', mt5.account_info().balance)

    SYMBOL = 'EURUSD'
    VOLUME = 0.01
    time.sleep(5)


    while True:

        # qaysi positsiyada order yo bosa shu positsiyada order ochadi
        buy, sell = Count_order(positions=mt5.positions_get(symbol=SYMBOL))
        if buy == 0:
            mt5.Buy(symbol=SYMBOL, volume=VOLUME)
            time.sleep(0.00333)
            print('Open=> BUY volume', VOLUME)
        if sell == 0:
            mt5.Sell(symbol=SYMBOL, volume=VOLUME)
            time.sleep(0.00333)
            print('Open=> SELL volume', VOLUME)


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