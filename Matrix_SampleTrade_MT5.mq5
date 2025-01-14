#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>

CTrade  trade;
CPositionInfo pos_info;


input double Lot = 0.01;
input int Profit_increase = 2;

input bool Remove = false;
input double Risk_lot = 999;
input int Risk_order = 9;
input double Risk_profit = 3;

input int Spreed = 20;
input int MagicNumber = 1234;
input string Order_Comment = "AUTO";

int x, cnum;
bool send;
double prof;

int OnInit() {
   trade.SetExpertMagicNumber(MagicNumber);
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason) {
   Comment("");
}

int Count_buy_orders() {
   cnum = 0;
   for(x = 0; x < PositionsTotal(); x++) {
      if(pos_info.SelectByIndex(x)) {
         if (pos_info.Magic() == MagicNumber) {
            if (pos_info.PositionType() == 0) {
               cnum++;
            }
         }
      }
   }
   return(cnum);
}

int Count_sell_orders() {
   cnum = 0;
   for(x = 0; x < PositionsTotal(); x++) {
      if(pos_info.SelectByIndex(x)) {
         if (pos_info.Magic() == MagicNumber) {
            if (pos_info.PositionType() == 1) {
               cnum++;
            }
         }
      }
   }
   return(cnum);
}

void Add_order_buy(ulong last_buy_ticket) {
   if(pos_info.SelectByTicket(last_buy_ticket)) {
      if (pos_info.Volume() < Risk_lot) {
         if ( -(pos_info.Volume() * 100) > pos_info.Profit() ) {
            send = trade.Buy(NormalizeDouble(pos_info.Volume() * 1.618, 2), NULL, 0, 0, 0, Order_Comment);
            Sleep(300);
         }
      }
   }
}

void Add_order_sell(ulong last_buy_ticket) {
   if(pos_info.SelectByTicket(last_buy_ticket)) {
      if (pos_info.Volume() < Risk_lot) {
         if ( -(pos_info.Volume() * 100) > pos_info.Profit() ) {
            send = trade.Sell(NormalizeDouble(pos_info.Volume() * 1.618, 2), NULL, 0, 0, 0, Order_Comment);
            Sleep(300);
         }
      }
   }
}

void Close_all_buy() {
   for(x = PositionsTotal(); x >= 0; x--) {
      if (pos_info.SelectByIndex(x)) {
         if(pos_info.Magic() == MagicNumber) {
            if (pos_info.PositionType() == 0) {
               send = trade.PositionClose(pos_info.Ticket(), clrBlack);
            }
         }
      }
   }
}

void Close_all_sell() {
   for(x = PositionsTotal(); x >= 0; x--) {
      if (pos_info.SelectByIndex(x)) {
         if(pos_info.Magic() == MagicNumber) {
            if (pos_info.PositionType() == 1) {
               send = trade.PositionClose(pos_info.Ticket(), clrBlack);
            }
         }
      }
   }
}

double Count_profit() {
   prof = 0;
   for(x = 0; x < PositionsTotal(); x++) {
      if(pos_info.SelectByIndex(x)) {
          if(pos_info.Magic() == MagicNumber) {
            prof += pos_info.Profit();
         }
      }
   }  
   return(prof);
}

void Close_all() {
   for(x = PositionsTotal(); x >= 0; x--) {
      if (pos_info.SelectByIndex(x)) {
         if (pos_info.Magic() == MagicNumber) {
            send = trade.PositionClose(pos_info.Ticket(), clrBlack);
         }
      }
   }
}


void OnTick() {
   
   if (Remove == false && SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) < Spreed) {
      if (Count_buy_orders() == 0) {
         send = trade.Buy(Lot, NULL, 0, 0, 0, Order_Comment);
         Print("SEND BUY  ", send);
         Sleep(300);
      }
      
      if (Count_sell_orders() == 0) {
         send = trade.Sell(Lot, NULL, 0, 0, 0, Order_Comment);
         Print("SEND SELL  ", send);
         Sleep(300);
      }
   }
   
   ulong lastime[] = {0, 0};
   ulong ticket[] = {0, 0};

   for(x = 0; x < PositionsTotal(); x++) {
      if(pos_info.SelectByIndex(x)) {
         if (pos_info.Magic() == MagicNumber) {
            if (pos_info.PositionType() == 0) {
               if (lastime[0] < pos_info.TimeMsc() / 1000) {
                  lastime[0] = pos_info.TimeMsc() / 1000;
                  ticket[0] = pos_info.Ticket();
               }
            }
            if (pos_info.PositionType() == 1) {
               if (lastime[1] < pos_info.TimeMsc() / 1000) {
                  lastime[1] = pos_info.TimeMsc() / 1000;
                  ticket[1] = pos_info.Ticket();
               }
            }
         }
      }
   }
   if (SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) < Spreed) {
      Add_order_buy(ticket[0]);
      Add_order_sell(ticket[1]);
   }
   ulong lastime1[] = {0, 0};
   ulong ticket1[] = {0, 0};

   for(x = 0; x < PositionsTotal(); x++) {
      if(pos_info.SelectByIndex(x)) {
         if (pos_info.Magic() == MagicNumber) {
            if (pos_info.PositionType() == 0) {
               if (lastime1[0] < pos_info.TimeMsc() / 1000) {
                  lastime1[0] = pos_info.TimeMsc() / 1000;
                  ticket1[0] = pos_info.Ticket();
               }
            }
            if (pos_info.PositionType() == 1) {
               if (lastime1[1] < pos_info.TimeMsc() / 1000) {
                  lastime1[1] = pos_info.TimeMsc() / 1000;
                  ticket1[1] = pos_info.Ticket();
               }
            }
         }
      }
   }
   

   
   if(pos_info.SelectByTicket(ticket1[0])) {
      if ( pos_info.Volume() * Profit_increase * 100 < pos_info.Profit() ) {
         Print("CLOSE ALL BUY");
         Close_all_buy();
      }
   }
   
   if(pos_info.SelectByTicket(ticket1[1])) {
      if ( pos_info.Volume() * Profit_increase * 100 < pos_info.Profit() ) {
         Print("CLOSE ALL SELL");
         Close_all_sell();
      }
   }
   
   
   
   if (Count_buy_orders() >= Risk_order || Count_sell_orders() >= Risk_order) {
      if (Count_profit() > Risk_profit) {
         Print("CLOSE ALL");
         Close_all();
      }
   }
   
   
   if (Remove == true) {
      if (Count_profit() > Risk_profit ) {
         Print("CLOSE ALL REMOVE");
         Close_all();
         ExpertRemove();
      }
   }
   
   Comment("Working . . .");
   
}
