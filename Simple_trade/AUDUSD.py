import MetaTrader5 as mt5
import pandas as pd
import time


def Close_profit():
    order_type = {0: 'buy', 1: 'sell'}
    positions = mt5.positions_get(symbol=SYMBOL)
    for position in positions:
        if position.profit >= 0.20:
            mt5.Close(position.symbol, ticket=position.ticket)
            print('Closed=>', order_type[position.type], 'Profit=>', position.profit)


def Close_buy(symbol, comment=None):
    positions = mt5.positions_get(symbol=symbol)
    tried = 0
    done = 0
    for pos in positions:
        # process only simple buy
        if pos.type == mt5.ORDER_TYPE_BUY:
            tried += 1
            for tries in range(10):
                info = mt5.symbol_info_tick(symbol)
                if info is None:
                    return None
                r = mt5._RawOrder(mt5.ORDER_TYPE_SELL, symbol, pos.volume, info.ask, comment, pos.ticket)
                # check results
                if r is None:
                    return None
                if r.retcode != mt5.TRADE_RETCODE_REQUOTE and r.retcode != mt5.TRADE_RETCODE_PRICE_OFF:
                    if r.retcode == mt5.TRADE_RETCODE_DONE:
                        done += 1
                    break
    print('Close all Buy')
    if done > 0:
        if done == tried:
            print(True)
        else:
            print("Partially")



def Close_sell(symbol, comment=None):
    positions = mt5.positions_get(symbol=symbol)
    tried = 0
    done = 0
    for pos in positions:
        # process only simple buy, sell
        if pos.type == mt5.ORDER_TYPE_SELL:
            tried += 1
            for tries in range(10):
                info = mt5.symbol_info_tick(symbol)
                if info is None:
                    return None
                r = mt5._RawOrder(mt5.ORDER_TYPE_BUY, symbol, pos.volume, info.ask, comment, pos.ticket)
                # check results
                if r is None:
                    return None
                if r.retcode != mt5.TRADE_RETCODE_REQUOTE and r.retcode != mt5.TRADE_RETCODE_PRICE_OFF:
                    if r.retcode == mt5.TRADE_RETCODE_DONE:
                        done += 1
                    break
    print('Close all Sell')
    if done > 0:
        if done == tried:
            print(True)
        else:
            print("Partially")


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


initialize = mt5.initialize()

if initialize:
    login = 51500183
    password = 'mkqfrkw6'
    server = 'Alpari-MT5-Demo'
    mt5.login(login=login, password=password, server=server)

    print('Connected to MetaTrader5')
    print('Login=>', mt5.account_info().login)
    print('Server=>', mt5.account_info().server)
    print('Balance=>', mt5.account_info().balance)

    SYMBOL = 'AUDUSD'
    VOLUME = 0.01
    time.sleep(5)
    mt5.Buy(symbol=SYMBOL, volume=VOLUME)
    mt5.Sell(symbol=SYMBOL, volume=VOLUME)
    time.sleep(1)

    while True:
        # 2ta order bosa va qaysi birini profiti 0.2$ dan baland bosa yopadi
        if len(mt5.positions_get(symbol=SYMBOL)) == 2:
            Close_profit()
            # time.sleep(1)

        # order 1ta bosa shu orderga qarshi order ochadi
        if len(mt5.positions_get(symbol=SYMBOL)) < 2:
            positions = mt5.positions_get(symbol=SYMBOL)
            b = 0
            s = 0
            for position in positions:
                if position.type == 0:
                    b += 1
                elif position.type == 1:
                    s += 1
            if b == len(positions):
                mt5.Sell(symbol=SYMBOL, volume=VOLUME)
            elif s == len(positions):
                mt5.Buy(symbol=SYMBOL, volume=VOLUME)
            # time.sleep(1)

        # qaysi order minusga kirsa order qoshadi
        if len(mt5.positions_get(symbol=SYMBOL)) == 2:
            for pos in mt5.positions_get(symbol=SYMBOL):
                if pos.profit < (-1.0):
                    if pos.type == 0:
                        mt5.Buy(symbol=SYMBOL, volume=0.06)
                    elif pos.type == 1:
                        mt5.Sell(symbol=SYMBOL, volume=0.06)

        elif len(mt5.positions_get(symbol=SYMBOL)) == 3:
            for pos in mt5.positions_get(symbol=SYMBOL):
                if pos.profit < (-6.0):
                    if pos.type == 0:
                        mt5.Buy(symbol=SYMBOL, volume=0.36)
                    elif pos.type == 1:
                        mt5.Sell(symbol=SYMBOL, volume=0.36)

        elif len(mt5.positions_get(symbol=SYMBOL)) == 4:
            for pos in mt5.positions_get(symbol=SYMBOL):
                if pos.profit < (-36.0):
                    if pos.type == 0:
                        mt5.Buy(symbol=SYMBOL, volume=2.16)
                    elif pos.type == 1:
                        mt5.Sell(symbol=SYMBOL, volume=2.16)

        elif len(mt5.positions_get(symbol=SYMBOL)) == 5:
            for pos in mt5.positions_get(symbol=SYMBOL):
                if pos.profit < (-216):
                    if pos.type == 0:
                        mt5.Buy(symbol=SYMBOL, volume=12.96)
                    elif pos.type == 1:
                        mt5.Sell(symbol=SYMBOL, volume=12.96)

        elif len(mt5.positions_get(symbol=SYMBOL)) == 6:
            for pos in mt5.positions_get(symbol=SYMBOL):
                if pos.profit < (-1296):
                    if pos.type == 0:
                        mt5.Buy(symbol=SYMBOL, volume=77.76)
                    elif pos.type == 1:
                        mt5.Sell(symbol=SYMBOL, volume=77.76)
        # time.sleep(1)

        # orderlar soni 2tadan kop bosa va profit kutganimzde bosa shu yonalishdagi barchasini yopadi
        if len(mt5.positions_get(symbol=SYMBOL)) > 2:
            buy_list = []
            sel_list = []
            for position in mt5.positions_get(symbol=SYMBOL):
                if position.type == 0:
                    buy_list.append(position)
                elif position.type == 1:
                    sel_list.append(position)

            if len(buy_list) < len(sel_list):
                if (sel_list[-1].volume * 2 * 10) <= sel_list[-1].profit:
                    Close_sell(symbol=SYMBOL)
            elif len(buy_list) > len(sel_list):
                if (buy_list[-1].volume * 2 * 10) <= buy_list[-1].profit:
                    Close_buy(symbol=SYMBOL)

        time.sleep(1)
else:
    print('No connection')