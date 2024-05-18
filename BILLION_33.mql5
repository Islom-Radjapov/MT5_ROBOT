#property copyright "BILLION Trading Club"
#property link      "https://t.me/+998331583333"
#property version   "33.0"
#property description "Billion Intelligent Robot's  \nTel: +998331583333 \n\n\n\n\n\n\n\t\t\t\t\t\tDeveloper  IslomRadjapov   Tel: +998977099197";

#include <Trade/Trade.mqh>
CTrade  trade;
CPositionInfo pos_info;


input double Lot = 1;

int x, buys = 0, sells = 0, buystop = 0, sellstop = 0;
ulong ticke;
double ask, bid;

void OnTick() {
   
   // Count buy, sell, ..stop orders
   buys = 0;
   sells = 0;
   buystop = 0;
   sellstop = 0;
   
   for (x = 0; x < PositionsTotal(); x++) {
      if ( pos_info.SelectByIndex(x) ) {
         if (pos_info.PositionType() == 0) {
            buys++;
         }
         else if (pos_info.PositionType() == 1) {
            sells++;
         }  
      }
   }
   
   for (x = 0; x < OrdersTotal(); x++) {
      if ( (ticke = OrderGetTicket(x) ) > 0) {
         if (OrderGetInteger(ORDER_TYPE) == 4) {
            buystop++;
         }
         else if (OrderGetInteger(ORDER_TYPE) == 5) {
            sellstop++;
         }  
      }
   }
   
   ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);

   
   if (buys == 0 && buystop == 0) {
      trade.BuyStop(Lot, ask, _Symbol, bid, 0);
   }
   
   if (sells == 0 && sellstop == 0) {
      trade.SellStop(Lot, bid, _Symbol, ask, 0);
   }
   
   for (x = 0; x < PositionsTotal(); x++) {
      if ( pos_info.SelectByIndex(x) ) {
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
   
   for (x = 0; x < OrdersTotal(); x++) {
      if ( (ticke = OrderGetTicket(x) ) > 0) {
         if (OrderGetInteger(ORDER_TYPE) == 4) {
            if (OrderGetDouble(ORDER_PRICE_OPEN) > ask ) {
               trade.OrderModify(ticke, ask, bid, 0, ORDER_TIME_DAY, ORDER_TIME_DAY);
            }
         }
         else if (OrderGetInteger(ORDER_TYPE) == 5) {
            if (OrderGetDouble(ORDER_PRICE_OPEN) < bid ) {
               trade.OrderModify(ticke, bid, ask, 0, ORDER_TIME_DAY, ORDER_TIME_DAY);
            }
         }  
      }
   }
   
   

   Comment("Working . . .");

}
