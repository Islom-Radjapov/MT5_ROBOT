//+------------------------------------------------------------------+
//|                                                    BILLION_9.mq5 |
//|                                  Copyright 2024, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+




#property copyright "BILLION Trading Club"
#property link      "https://t.me/+998331583333"
#property version   "1.0"
#property description "Billion Intelligent Robot's  \nTel: +998331583333 \n\n\n\n\n\n\n\t\t\t\t\t\tDeveloper  IslomRadjapov   Tel: +998977099197";
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
#include <Trade/Trade.mqh>
CTrade  trade;



input double Lot = 0.2;
input int TakeProfit = 1500;

int OnInit() {

   return(INIT_SUCCEEDED);

}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
//---

}
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+

int x;
double lastbar, bar, ask, bid;

void OnTick() {

   bar = iBars(_Symbol,PERIOD_M1);
   if (lastbar != bar) {
   
      lastbar = bar;
      ask =  SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      bid =  SymbolInfoDouble(_Symbol, SYMBOL_BID);
      
      trade.Buy(Lot, _Symbol, ask, 0, bid + TakeProfit * _Point);

   }

}
//+------------------------------------------------------------------+