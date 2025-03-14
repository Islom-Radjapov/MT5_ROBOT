#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
CTrade  trade;
CPositionInfo pos_info;

double First_risk_percentage = 0.1;
double Start_balance = 100000;
int random_hour;
int random_min;

//+------------------------------------------------------------------------- OnInit +
int OnInit() {
   // Define the time range (in seconds)
   int start_hour   = 8;
   int start_minute = 30;
   int end_hour     = 9;
   int end_minute   = 30;
   // Convert the range into total minutes
   int start_time_min = start_hour * 60 + start_minute;
   int end_time_min   = end_hour * 60 + end_minute;
   // Generate a random number of minutes within the range
   int random_minute = start_time_min + MathRand() % (end_time_min - start_time_min + 1);
   // Extract the randomly generated hour and minute
   random_hour = random_minute / 60;
   random_min  = random_minute % 60;
   PrintFormat("Random Time: %02d:%02d", random_hour, random_min);
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------------- OnTick +
void OnTick() {

   MqlDateTime timeStruct;
   TimeCurrent(timeStruct);
   int hour = timeStruct.hour;
   int minute = timeStruct.min;
   //Print("hour ", hour);
   //Print("minute ", minute);
   
   if (hour == random_hour && minute == random_min) {
      OpenOrder(CalculateATR(SelectPeriod()) / _Point, Find_risk());
      PrintFormat("Open Time: %02d:%02d", random_hour, random_min);
   }

}



//+--------------------------------------------------------------------- Funcktion OpenOrder +
void OpenOrder(int atr, double riskPercentage) {
   if(MathRand() % 2 == 0) {
      Print("Buy order");
      //Print(x, " is Even"); //juft
      trade.Buy(CalculateLotSize(riskPercentage, atr), _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_ASK),
      SymbolInfoDouble(_Symbol, SYMBOL_ASK) - atr * _Point,
      SymbolInfoDouble(_Symbol, SYMBOL_ASK) + atr * _Point
      );
      ExpertRemove();
   } else {
      Print("Sell order");
      //Print(x, " is Odd"); // toq
      trade.Sell(CalculateLotSize(riskPercentage, atr), _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_BID),
      SymbolInfoDouble(_Symbol, SYMBOL_BID) + atr * _Point,
      SymbolInfoDouble(_Symbol, SYMBOL_BID) - atr * _Point
      );
      ExpertRemove();
   }
}

//+--------------------------------------------------------------------- Funcktion CalculateATR +
double CalculateATR(int period) {
   double sum = 0;
   for(int i = 1; i <= period; i++) {
      double high = iHigh(Symbol(), PERIOD_CURRENT, i);
      double low  = iLow(Symbol(), PERIOD_CURRENT, i);
      double close_prev = iClose(Symbol(), PERIOD_CURRENT, i+1);

      double tr = MathMax(high - low, MathMax(MathAbs(high - close_prev), MathAbs(low - close_prev)));
      sum += tr;
   }
   Print("ATR ", sum / period);
   return sum / period;
}

//+--------------------------------------------------------------------- Funcktion SelectPeriod +
int SelectPeriod() {
   int list[] = {7,8,9,10,11,12,13,14,15,16,17,18,19};
   int size = ArraySize(list); // Ro‘yxat uzunligi
   int index = MathRand() % size; // 0 dan size-1 gacha indeks tanlash
   Print("Period ", list[index]);
   return list[index]; // Tasodifiy elementni qaytarish
}

//+--------------------------------------------------------------------- Funcktion CalculateLotSize +
double CalculateLotSize(double riskPercentage, double stopLossPips) {
   Print("Risk Percentage ", riskPercentage);
   // Get the contract size for the symbol
   double contractSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE);
   
   // Get the tick size for the symbol
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   
   // Get the tick value for the symbol
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   
   // Calculate the value of a pip
   double pipValue = (tickValue / tickSize) * SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   
   // Calculate the lot size
   double riskAmount = Start_balance * (riskPercentage / 100.0);
   double lotSize = riskAmount / (stopLossPips * pipValue);
   
   // Normalize the lot size to the allowed step
   double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   lotSize = MathFloor(lotSize / lotStep) * lotStep;
   
   // Ensure the lot size is within the allowed minimum and maximum
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   lotSize = MathMin(MathMax(lotSize, minLot), maxLot);
   Print("Lot ", lotSize);
   return lotSize;
}

//+--------------------------------------------------------------------- Funcktion CalculateProfitForPosition +
// Function to calculate profit for a position
double CalculateProfitForPosition(ulong positionID) {
   double totalProfit = 0.0;
   // Loop through all historical deals
   for (int i = 0; i < HistoryDealsTotal(); i++) {
      // Check if the deal belongs to the specified position
      if (HistoryDealGetInteger(HistoryDealGetTicket(i), DEAL_POSITION_ID) == positionID) {
         // Add the profit of the deal to the total profit
         totalProfit += HistoryDealGetDouble(HistoryDealGetTicket(i), DEAL_PROFIT);
      }
   }
   return totalProfit;
}

//+--------------------------------------------------------------------- Funcktion Find_risk +
double Find_risk() {

   
   //double lotSize = 0.0;
   double profit = 0.0;
   //datetime orderTime = 0;
   //ulong lastOrderTicket = 0;
   bool orderFound = false;
   
   HistorySelect(0, TimeCurrent());
   for (int i = HistoryOrdersTotal() - 1; i >= 0; i--) {
      ulong orderTicket = HistoryOrderGetTicket(i);
      if (HistoryOrderGetString(orderTicket, ORDER_SYMBOL) == _Symbol) {
         //lotSize = HistoryOrderGetDouble(orderTicket, ORDER_VOLUME_INITIAL);
         //orderTime = (datetime)HistoryOrderGetInteger(orderTicket, ORDER_TIME_SETUP);
         
         // Get the position ID of the order
         ulong positionID = HistoryOrderGetInteger(orderTicket, ORDER_POSITION_ID);
         
         // Calculate the profit for the position
         profit = CalculateProfitForPosition(positionID);
         
         // Store the order ticket
         //lastOrderTicket = orderTicket;
         
         // Mark that an order was found
         orderFound = true;
         
         // Exit the loop since we only need the last order
         break;
      }
   }

   // Print the results
   if (orderFound) {
      //Print("Last Order History for ", _Symbol, ":");
      //Print("Order Ticket: ", lastOrderTicket);
      //Print("Lot Size: ", lotSize);
      //Print("Profit: ", profit);
      //Print("Order Time: ", orderTime);
      if (profit > 0) {
         return First_risk_percentage;
      } else {
         if (profit < -8 && profit > -20) {
            return 0.2;
         } else if (profit < -18 && profit > -40) {
            return 0.4;
         } else if (profit < -38 && profit > -80) {
            return 0.7;
         } else if (profit < -68 && profit > -140) {
            return 1.4;
         } else if (profit < -130 && profit > -280) {
            return 2.1;
         } else if (profit < -200 && profit > -400) {
            return 4.9;
         }
      }
   } /*else {
      Print("No order history found for ", _Symbol);
      return First_risk_percentage;
   }*/
   return First_risk_percentage;
}

