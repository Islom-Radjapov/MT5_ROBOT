import MetaTrader5 as mt5
from time import sleep

initialize = mt5.initialize()

if initialize:

    SYMBOL = 'EURUSD'

    try:
        while True:
            result = mt5.Close(symbol=SYMBOL)
            sleep(0.00333)
            print("result=>", result)
            print("Stop While and Close all positon")

    except:
        mt5.Close(symbol=SYMBOL)
        print("CODE ERROR")
else:
    print('No connection')