//+------------------------------------------------------------------+
//|                                                    BILLION_9.mq5 |
//|                                  Copyright 2024, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
int Login = 251370743;
//datetime date = D'2024.12.31 23:59';



#property copyright "BILLION Trading Club"
#property link      "https://t.me/+998331583333"
#property version   "9.0"
#property description "Billion Intelligent Robot's  \nTel: +998331583333 \n\n\n\n\n\n\n\t\t\t\t\t\tDeveloper  IslomRadjapov   Tel: +998977099197";
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
#include <Trade/Trade.mqh>
CTrade  trade;



input double Lot = 0.2;
input int TakeProfit = 500;

int OnInit() {

   if ( AccountInfoInteger(ACCOUNT_LOGIN) == Login) { //&& TimeCurrent() < date) {
      return(INIT_SUCCEEDED);
   }
   else {
      Alert("Account not authorized, Contact EA author to validate account");
      ExpertRemove();
      return(INIT_FAILED);
   }

}
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
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
      trade.Sell(Lot, _Symbol, bid, 0, ask - TakeProfit * _Point);

   }
   

}
//+------------------------------------------------------------------+
