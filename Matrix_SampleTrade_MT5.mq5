#include <Trade/Trade.mqh>
CTrade  trade;
CPositionInfo pos_info;

input double Lot = 0.01;
input int Risk_order = 9;
input double Risk_lot = 0.89;
input double Risk_profit = 3;

input bool Remove = false;
input int MagicNumber = 1234;

int send, x = 0;

int OnInit() {
   trade.SetExpertMagicNumber(MagicNumber);
   return(INIT_SUCCEEDED);
}
  
void OnDeinit(const int reason) {
   Comment("");
}


int Count_buy_orders() {
   int res = 0;
   for(x = 0; x < PositionsTotal(); x++) {
      if(pos_info.SelectByIndex(x)) {
         if (PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
            if (PositionGetInteger(POSITION_TYPE) == 0) {
               res++;
            }
         }
      }
   }  
   return(res);
}

int Count_sell_orders() {
   int res = 0;
   for(x = 0; x < PositionsTotal(); x++) {
      if(pos_info.SelectByIndex(x)) {
         if (PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
            if (PositionGetInteger(POSITION_TYPE) == 1) {
               res++;
            }
         }
      }
   }  
   return(res);
}


void Add_order_buy(ulong last_buy_ticket) {
   if(pos_info.SelectByTicket(last_buy_ticket)) {
      if (PositionGetDouble(POSITION_VOLUME) < Risk_lot) {
         if ( -(PositionGetDouble(POSITION_VOLUME) * 100) > PositionGetDouble(POSITION_PROFIT) ) {
            send = trade.Buy(NormalizeDouble(PositionGetDouble(POSITION_VOLUME) * 1.618, 2));
            Sleep(500);
         }
      }
   }
}

void Add_order_sell(ulong last_buy_ticket) {
   if(pos_info.SelectByTicket(last_buy_ticket)) {
      if (PositionGetDouble(POSITION_VOLUME) < Risk_lot) {
         if ( -(PositionGetDouble(POSITION_VOLUME) * 100) > PositionGetDouble(POSITION_PROFIT) ) {
            send = trade.Sell(NormalizeDouble(PositionGetDouble(POSITION_VOLUME) * 1.618, 2));
            Sleep(500);
         }
      }
   }
}

void Close_all_buy() {
   for(x = PositionsTotal() - 1; x >= 0; x--) {
      if(PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
         if (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) {
            trade.PositionClose(PositionGetTicket(x), clrBlack);
         }
           
      }
   }
}

void Close_all_sell() {
   for(x = PositionsTotal() - 1; x >= 0; x--) {
      if(PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
         if (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL) {
            trade.PositionClose(PositionGetTicket(x), clrBlack);
         }
      }
   }
}

void Close_all() {
   for(x = PositionsTotal() - 1; x >= 0; x--) {
      if(PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
         trade.PositionClose(PositionGetTicket(x), clrBlack);
      }
   }
}

double Count_profit() {
   double prof = 0;
   for(x = 0; x < PositionsTotal(); x++) {
      if(pos_info.SelectByIndex(x)) {
         if (PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
            prof += PositionGetDouble(POSITION_PROFIT);
         }
      }
   }  
   return(prof);
}

void OnTick() {
   
   if (Remove == false) {
      if (Count_buy_orders() == 0) {
         send = trade.Buy(Lot);
         Sleep(500);
      }
      
      if (Count_sell_orders() == 0) {
         send = trade.Sell(Lot);
         Sleep(500);
      }
   }
   
   ulong lastime[] = {0, 0};
   ulong ticket[] = {0, 0};

    for(x = 0; x < PositionsTotal(); x++) {
      if(pos_info.SelectByIndex(x)) {
         if (PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
            if (PositionGetInteger(POSITION_TYPE) == 0) {
               if (lastime[0] < PositionGetInteger(POSITION_TIME_MSC) / 1000) {
                  lastime[0] = PositionGetInteger(POSITION_TIME_MSC) / 1000;
                  ticket[0] = PositionGetTicket(x);
               }
            }
            if (PositionGetInteger(POSITION_TYPE) == 1) {
               if (lastime[1] < PositionGetInteger(POSITION_TIME_MSC) / 1000) {
                  lastime[1] = PositionGetInteger(POSITION_TIME_MSC) / 1000;
                  ticket[1] = PositionGetTicket(x);
               }
            }
         }
      }
   }
   
   Add_order_buy(ticket[0]);
   Add_order_sell(ticket[1]);
   
   
   ulong lastime1[] = {0, 0};
   ulong ticket1[] = {0, 0};

    for(x = 0; x < PositionsTotal(); x++) {
      if(pos_info.SelectByIndex(x)) {
         if (PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
            if (PositionGetInteger(POSITION_TYPE) == 0) {
               if (lastime1[0] < PositionGetInteger(POSITION_TIME_MSC) / 1000) {
                  lastime1[0] = PositionGetInteger(POSITION_TIME_MSC) / 1000;
                  ticket1[0] = PositionGetTicket(x);
               }
            }
            if (PositionGetInteger(POSITION_TYPE) == 1) {
               if (lastime1[1] < PositionGetInteger(POSITION_TIME_MSC) / 1000) {
                  lastime1[1] = PositionGetInteger(POSITION_TIME_MSC) / 1000;
                  ticket1[1] = PositionGetTicket(x);
               }
            }
         }
      }
   }
   

   
   if(pos_info.SelectByTicket(ticket1[0])) {
      if ( PositionGetDouble(POSITION_VOLUME) * 2 * 100 < PositionGetDouble(POSITION_PROFIT) ) {
         Print("CLOSE ALL BUY");
         while (true) {
            Close_all_buy();
            if (Count_buy_orders() == 0) {
               break;
            }
         }
      }
   }
   
   if(pos_info.SelectByTicket(ticket1[1])) {
      if ( PositionGetDouble(POSITION_VOLUME) * 2 * 100 < PositionGetDouble(POSITION_PROFIT) ) {
         Print("CLOSE ALL SELL");
         while (true) {
            Close_all_sell();
            if (Count_buy_orders() == 0) {
               break;
            }
         }
      }
   }
   
   
   
   if (Count_buy_orders() >= Risk_order || Count_sell_orders() >= Risk_order) {
      if (Count_profit() > Risk_profit) {
         Print("CLOSE ALL");
         while (true) {
            Close_all();
            if (Count_buy_orders() == 0) {
               break;
            }
         }
      }
   }
   
   
   if (Remove == true) {
      if (Count_profit() > Risk_profit ) {
         while (true) {
            Close_all();
            if (Count_buy_orders() == 0) {
               break;
            }
         }
         ExpertRemove();
      }
   }
   
   Comment("Working . . ."); 

}
