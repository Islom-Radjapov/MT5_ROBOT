#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
CTrade  trade;
CPositionInfo pos_info;

double First_risk_percentage = 0.05;
double Start_balance = 25000;
input int Spreed = 11;
int start_hour   = 5; // 8  Toshkent soati 10dan
//int start_minute = 30;
int end_hour     = 18; // 21  Toshkent soati 21gacha
//int end_minute   = 30;

string commentt;
int MagicNumber = 383;
int random_hour;
int random_min;

//+------------------------------------------------------------------------- OnInit +
int OnInit() {

   trade.SetExpertMagicNumber(MagicNumber);
   /*// Convert the range into total minutes
   int start_time_min = start_hour * 60 + start_minute;
   int end_time_min   = end_hour * 60 + end_minute;
   // Generate a random number of minutes within the range
   int random_minute = start_time_min + MathRand() % (end_time_min - start_time_min + 1);
   // Extract the randomly generated hour and minute
   random_hour = random_minute / 60;
   random_min  = random_minute % 60;
   PrintFormat("Random Time: %02d:%02d", random_hour, random_min);*/
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------------- OnTick +
void OnTick() {
   
   MqlDateTime timeStruct;
   TimeCurrent(timeStruct);
   int hour = timeStruct.hour;
   //int minute = timeStruct.min;
   
   if (hour >= start_hour && hour <= end_hour) {
      if (Find_Symbol(_Symbol) && SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) < Spreed) {
         int period = SelectPeriod();
         double atr = CalculateATR(period);
         double riskPercentage = Find_risk();
         double lot = CalculateLotSize(riskPercentage, atr / _Point);
         
         if(MathRand() % 2 == 0) {
            //Print(x, " is Even"); //juft
            trade.Buy(lot, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_ASK),
            SymbolInfoDouble(_Symbol, SYMBOL_ASK) - atr,
            SymbolInfoDouble(_Symbol, SYMBOL_ASK) + atr, commentt
            );
            PrintFormat("Open Time: %02d:%02d", random_hour, random_min );
            Print("BUY order => ", _Symbol);
            Print("Risk Percent => ", riskPercentage);
            Print("LOT => ", lot);
            Print("ATR => ", atr);
            Print("comment => ", commentt);
            //ExpertRemove();
         } else {
            //Print(x, " is Odd"); // toq
            trade.Sell(lot, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_BID),
            SymbolInfoDouble(_Symbol, SYMBOL_BID) + atr,
            SymbolInfoDouble(_Symbol, SYMBOL_BID) - atr, commentt
            );
            PrintFormat("Open Time: %02d:%02d", random_hour, random_min );
            Print("SELL order => ", _Symbol);
            Print("Risk Percent => ", riskPercentage);
            Print("LOT => ", lot);
            Print("ATR => ", atr);
            Print("comment => ", commentt);
            //ExpertRemove();
         }
      }
   }
}


//+--------------------------------------------------------------------- Funcktion Find_Symbol +
bool Find_Symbol(string sym) {

   for(int x = 0; x < PositionsTotal(); x++) {
      if(pos_info.SelectByIndex(x)) {
         if (pos_info.Symbol() == sym) {
            if (pos_info.Magic() == MagicNumber) {
               return false;
            }
         }
      }
   }
   return true;
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
   return sum / period;
}

//+--------------------------------------------------------------------- Funcktion SelectPeriod +
int SelectPeriod() {
   int list[] = {7,8,9,10,11,12,13,14};//,15,16,17,18,19};
   int size = ArraySize(list); // Ro‘yxat uzunligi
   int index = MathRand() % size; // 0 dan size-1 gacha indeks tanlash
   return list[index]; // Tasodifiy elementni qaytarish
}

//+--------------------------------------------------------------------- Funcktion CalculateLotSize +
double CalculateLotSize(double riskPercentage, double stopLossPips) {
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

   double profit = 0.0;
   bool orderFound = false;
   string orderComment;
   ulong positionID = 0;
   ulong orderTicket = 0;
   HistorySelect(0, TimeCurrent());
   for (int i = HistoryOrdersTotal() - 1; i >= 0; i--) {
      ulong orderTicket = HistoryOrderGetTicket(i);
      if (HistoryOrderGetString(orderTicket, ORDER_SYMBOL) == _Symbol) {
         if (HistoryOrderGetInteger(orderTicket, ORDER_MAGIC) == MagicNumber) {
            positionID = HistoryOrderGetInteger(orderTicket, ORDER_POSITION_ID);
            profit = CalculateProfitForPosition(positionID);
            orderComment = HistoryOrderGetString(positionID, ORDER_COMMENT);
            orderFound = true;
            break;
         }
      }
   }


   if (orderFound) {
      if (profit < 0 && orderComment == "67383") { // 2
         commentt = "18394";
         return 0.05;
      } else if (profit < 0 && orderComment == "18394") { // 3
         commentt = "62782";
         return 0.1;
      } else if (profit < 0 && orderComment == "62782") { // 4
         commentt = "41657";
         return 0.2;
      } else if (profit < 0 && orderComment == "41657") { // 5
         commentt = "17120";
         return 0.4;
      } else if (profit < 0 && orderComment == "17120") { // 6
         commentt = "55769";
         return 0.8;
      } else if (profit < 0 && orderComment == "55769") { // 7
         commentt = "9507";
         return 1.6;
      } else if (profit < 0 && orderComment == "9507") { // 8
         commentt = "52180";
         return 3.2;
      } else if (profit < 0 && orderComment == "52180") { // 9
         commentt = "54492";
         return 6.4;
      }
   }
   
   commentt = "67383";
   return First_risk_percentage;
}



