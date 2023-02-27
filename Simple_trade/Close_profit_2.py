import MetaTrader5 as mt5
from time import sleep

initialize = mt5.initialize()

if initialize:

    SYMBOL = 'EURUSD'

    try:
        while True:
            profit = 0
            for pos in mt5.positions_get(symbol=SYMBOL):
                profit += pos.profit

            if profit >= 2:
                mt5.Close(symbol=SYMBOL)
                sleep(0.00333)
                print("Stop robot close all positions")
                break
        result = mt5.Close(symbol=SYMBOL)
        print("result=>", result)
        print("Stop While and Close all positon")

    except:
        mt5.Close(symbol=SYMBOL)
        print("CODE ERROR")
else:
    print('No connection')