import MetaTrader5 as mt5
import pandas as pd
import time



# initialize = mt5.initialize(path=r"C:\Program Files\Alpari MT5\terminal64.exe")
# login = 51920041
# password = 'Asd_1234'
# server = 'Alpari-MT5-Demo'


initialize = mt5.initialize(path=r"C:\Program Files\Deriv MT5 Terminal\terminal64.exe")
login = 23084175
password = 'Asd_1234'
server = 'Deriv-Demo'



mt5.login(login=login, password=password, server=server)
print('Connected to MetaTrader5')
print('Login=>', mt5.account_info().login)
print('Server=>', mt5.account_info().server)
print('Balance=>', mt5.account_info().balance)



symbol = 'Step Index'

lot = 0.5
point = mt5.symbol_info(symbol).point
price = mt5.symbol_info_tick(symbol).ask
deviation = 20

request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": lot,
    "type": mt5.ORDER_TYPE_BUY,
    "price": price,
    "sl": price - 100 * point,
    "tp": price + 100 * point,
    "deviation": deviation,
    "magic": 234000,
    "comment": "python script open",
    "type_time": mt5.ORDER_TIME_GTC,
    #"type_filling": mt5.ORDER_FILLING_IOC
}

# send a trading request
result = mt5.order_send(request)


print(result)




