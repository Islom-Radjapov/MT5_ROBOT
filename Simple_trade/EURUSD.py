import MetaTrader5 as mt5
import time



def Close_profit():
    order_type = {0: 'buy', 1: 'sell'}
    for position in mt5.positions_get(symbol=SYMBOL):
        if position.profit >= 0.20:
            mt5.Close(position.symbol, ticket=position.ticket)
            print('Closed=>', order_type[position.type], 'Profit=>', position.profit)


def Close_buy(symbol, comment=None):
    positions = mt5.positions_get(symbol=symbol)
    print('Closed all Buy')
    for pos in positions:
        # process only simple buy
        if pos.type == mt5.ORDER_TYPE_BUY:
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
            print('Profit=>', pos.profit)



def Close_sell(symbol, comment=None):
    positions = mt5.positions_get(symbol=symbol)
    print('Closed all Sell')
    tried = 0
    done = 0
    for pos in positions:
        # process only simple buy, sell
        if pos.type == mt5.ORDER_TYPE_SELL:
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
        print('Profit=>', pos.profit)


def get_volume(volum):
    if volum == 12.96:
        return 77.76
    elif volum == 2.16:
        return 12.96
    elif volum == 0.36:
        return 2.16
    elif volum == 0.06:
        return 0.36
    elif volum == 0.01:
        return 0.06


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
            list_sell.append(pos)
        else:
            list_buy.append(pos)
    return list_buy, list_sell


def add_order(positions):

    if len(positions) == 2:
        for pos in mt5.positions_get(symbol=SYMBOL):
            if pos.profit < (-1.0):
                if pos.type == 0:
                    mt5.Buy(symbol=SYMBOL, volume=0.06)
                    print('Open=> BUY volume', 0.06)
                else:
                    mt5.Sell(symbol=SYMBOL, volume=0.06)
                    print('Open=> SELL volume', 0.06)

    elif len(positions) == 3:
        for pos in mt5.positions_get(symbol=SYMBOL):
            if pos.profit < (-6.0):
                if pos.type == 0:
                    mt5.Buy(symbol=SYMBOL, volume=0.36)
                    print('Open=> BUY volume', 0.36)
                else:
                    mt5.Sell(symbol=SYMBOL, volume=0.36)
                    print('Open=> SELL volume', 0.36)

    elif len(positions) == 4:
        for pos in mt5.positions_get(symbol=SYMBOL):
            if pos.profit < (-36.0):
                if pos.type == 0:
                    mt5.Buy(symbol=SYMBOL, volume=2.16)
                    print('Open=> BUY volume', 2.16)
                else:
                    mt5.Sell(symbol=SYMBOL, volume=2.16)
                    print('Open=> SELL volume', 2.16)

    elif len(positions) == 5:
        for pos in mt5.positions_get(symbol=SYMBOL):
            if pos.profit < (-216):
                if pos.type == 0:
                    mt5.Buy(symbol=SYMBOL, volume=12.96)
                    print('Open=> BUY volume', 12.96)
                else:
                    mt5.Sell(symbol=SYMBOL, volume=12.96)
                    print('Open=> SELL volume', 12.96)

    elif len(positions) == 6:
        for pos in mt5.positions_get(symbol=SYMBOL):
            if pos.profit < (-1296):
                if pos.type == 0:
                    mt5.Buy(symbol=SYMBOL, volume=77.76)
                    print('Open=> BUY volume', 77.76)
                else:
                    mt5.Sell(symbol=SYMBOL, volume=77.76)
                    print('Open=> SELL volume', VOLUME)



initialize = mt5.initialize()

if initialize:
    login = 51502266
    password = 'ylmgh3sd'
    server = 'Alpari-MT5-Demo'
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
            print('Open=> BUY volume', VOLUME)
        if sell == 0:
            mt5.Sell(symbol=SYMBOL, volume=VOLUME)
            print('Open=> SELL volume', VOLUME)
        time.sleep(0.5)

        # 2ta order bosa va qaysi birini profiti 0.2$ dan baland bosa yopadi
        buy, sell = Count_order(positions=mt5.positions_get(symbol=SYMBOL))
        if buy == 1 and sell == 1:
            Close_profit()
        time.sleep(0.5)

        # qaysi order minusga kirsa order qoshadi
        positions = mt5.positions_get(symbol=SYMBOL)
        if len(positions) >= 2:
            add_order(positions)
        time.sleep(0.5)



        """" orderlar soni 3tadan kop bosa va profit kutganimzde bosa shu yonalishdagi barchasini yopadi
                                            yoki qaysi positsiya 1ta bosa va profit 0.2$ balan bosa yopadi  """
        if len(mt5.positions_get(symbol=SYMBOL)) >= 3:
            buy_list, sell_list = Count_position()

            if len(buy_list) > len(sell_list):
                if (buy_list[-1].volume * 2 * 10) <= buy_list[-1].profit:
                    Close_buy(symbol=SYMBOL)
                else:
                    if len(sell_list) == 1 and sell_list[0].profit >= 0.2:
                        mt5.Close(symbol=SYMBOL, ticket=sell_list[0].ticket)
                        print('Closed=> SEL profit=>', sell_list[0].profit)

            elif len(buy_list) < len(sell_list):
                if (sell_list[-1].volume * 2 * 10) <= sell_list[-1].profit:
                    Close_sell(symbol=SYMBOL)
                else:
                    if len(buy_list) == 1 and buy_list[0].profit >= 0.2:
                        mt5.Close(symbol=SYMBOL, ticket=buy_list[0].ticket)
                        print('Closed=> BUY profit=>', buy_list[0].profit)
        time.sleep(0.5)

else:
    print('No connection')