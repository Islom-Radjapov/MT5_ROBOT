//+------------------------------------------------------------------+
//|                                              TralingStoploss.mq5 |
//|                                  Copyright 2026, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
//---
   
//---
   return(INIT_SUCCEEDED);
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

#include <Trade/Trade.mqh>
CTrade  trade;
CPositionInfo pos_info;


int x;
ulong ticke;
double ask, bid;

void OnTick() {

   ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   
   for (x = 0; x < PositionsTotal(); x++) {
      if ( pos_info.SelectByIndex(x) ) {
         if ( pos_info.StopLoss() != 0) {
            if (pos_info.PositionType() == 0) {
               if ( pos_info.StopLoss() < bid) {
                  trade.PositionModify(PositionGetTicket(x), bid, 0);
               }
            }
            else if (pos_info.PositionType() == 1) {
               if ( pos_info.StopLoss() > ask) {
                  trade.PositionModify(PositionGetTicket(x), ask, 0);
               }
            }
         }
      }
   }
   
}
