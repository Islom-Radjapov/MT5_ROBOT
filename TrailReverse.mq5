//+------------------------------------------------------------------+
//|                                                 TrailReverse.mq5 |
//|                                                                  |
//|  Videodagi robot qoidalari (uning 1805 ta savdosidan aniqlangan):|
//|   1. Ochiq order yo'q: narxdan "Masofa" yuqorida BUY STOP va     |
//|      "Masofa" pastda SELL STOP turadi. Narx yaqinlashsa, ular    |
//|      ham ketidan suriladi (BUY STOP pastga, SELL STOP tepaga).   |
//|   2. Stop order ishga tushadi: yangi orderning SL i kirish       |
//|      narxidan "Masofa" uzoqlikda bo'ladi.                        |
//|   3. BUY ochiq: SL = Bid - Masofa. Narx har pointda ko'tarilsa,  |
//|      SL ham ko'tariladi. SELL STOP aynan SL turgan joyda turadi. |
//|   4. SELL ochiq: SL = Ask + Masofa. Narx tushgan sari SL ham     |
//|      tushadi. BUY STOP aynan SL turgan joyda turadi.             |
//|   5. SL urilsa, o'sha joydagi teskari stop order ishga tushadi.  |
//|      Doim 1 ta ochiq order + 1 ta stop order bo'lib turadi.      |
//|                                                                  |
//|  Masofa va qadam NARX BIRLIGIDA (oltinda dollar): 0.30 = 30 cent |
//|  (0.10 lotda bitta zarar = 3$). Faqat HEDGING hisoblar uchun.    |
//+------------------------------------------------------------------+
#property version     "3.00"
#property description "Doim 1 ta ochiq order + 1 ta teskari stop order. SL va stop order narx ketidan suriladi."
#property description "Masofa va qadam narx birligida (oltinda dollar). Faqat HEDGING hisoblar uchun."

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\OrderInfo.mqh>

#define SLIPPAGE_POINTS 30   // bozor orderi uchun ruxsat etilgan sirpanish (punkt)

enum ENUM_START_MODE
  {
   START_BOTH_STOPS = 0,  // Ikki tomonga stop order (videodagidek)
   START_BUY        = 1   // Darhol BUY ochish
  };

//==================================================================== Sozlamalar
input group "=== Asosiy sozlamalar ==="
input double          InpLot       = 0.10;             // Lot
input double          InpDistance  = 0.30;             // Masofa ($): SL va stop order narxdan shuncha uzoqda
input double          InpStep      = 0.01;             // Surish qadami ($): 0.01 = har bir pointda
input ENUM_START_MODE InpStartMode = START_BOTH_STOPS; // Boshlash usuli

input group "=== Ish vaqti (server vaqti) ==="
input bool   InpUseTime    = false;   // Ish vaqtini cheklash
input string InpStartTime  = "05:00"; // Boshlanish vaqti
input string InpEndTime    = "19:00"; // Tugash vaqti
input bool   InpCloseAtEnd = false;   // Vaqt tugaganda ochiq orderni yopish

input group "=== Boshqa ==="
input long   InpMagic      = 2611;    // Magic raqam (robot o'z orderlarini taniydi)

//==================================================================== Global
CTrade               trade;
CPositionInfo        posInfo;
COrderInfo           ordInfo;

double               g_lot        = 0.0;            // broker qoidasiga moslangan lot
int                  g_startMin   = 0;              // boshlanish (kun boshidan daqiqa)
int                  g_endMin     = 0;              // tugash (kun boshidan daqiqa)
datetime             g_pauseUntil = 0;              // xatodan keyin qisqa pauza
ENUM_ORDER_TYPE_TIME g_timeType   = ORDER_TIME_GTC; // stop order muddati

//+------------------------------------------------------------------+
int OnInit()
  {
   if((ENUM_ACCOUNT_MARGIN_MODE)AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
     {
      Alert("TrailReverse: bu robot faqat HEDGING hisobda ishlaydi.");
      return(INIT_FAILED);
     }
   if(InpLot <= 0 || InpDistance <= 0 || InpStep < 0)
     {
      Alert("TrailReverse: Lot va Masofa 0 dan katta, Surish qadami 0 yoki undan katta bo'lishi kerak.");
      return(INIT_PARAMETERS_INCORRECT);
     }
   g_startMin = ParseTime(InpStartTime);
   g_endMin   = ParseTime(InpEndTime);
   if(g_startMin < 0 || g_endMin < 0)
     {
      Alert("TrailReverse: vaqt SS:DD ko'rinishida bo'lishi kerak, masalan 05:00.");
      return(INIT_PARAMETERS_INCORRECT);
     }

   g_lot = NormalizeLot(InpLot);
   double spread = SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID);
   PrintFormat("TrailReverse: %s | digits=%d | point=%g | stops level=%d | spred=%s | lot=%.2f | masofa=%s | qadam=%s",
               _Symbol, _Digits, _Point, (int)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL),
               DoubleToString(spread, _Digits), g_lot, DoubleToString(Distance(), _Digits),
               DoubleToString(InpStep, _Digits));
   if(spread > 0 && Distance() <= spread)
      Print("TrailReverse: OGOHLANTIRISH - Masofa spreddan katta bo'lishi kerak, aks holda stop orderlar qo'yilmaydi.");

   //--- broker GTC orderlarga ruxsat bermasa, kunlik order ishlatiladi
   long expModes = SymbolInfoInteger(_Symbol, SYMBOL_EXPIRATION_MODE);
   g_timeType = ((expModes & SYMBOL_EXPIRATION_GTC) != 0) ? ORDER_TIME_GTC : ORDER_TIME_DAY;

   trade.SetExpertMagicNumber((ulong)InpMagic);
   trade.SetDeviationInPoints(SLIPPAGE_POINTS);
   trade.SetTypeFillingBySymbol(_Symbol);
   trade.LogLevel(LOG_LEVEL_ERRORS);
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   //--- robot grafikdan olib tashlansa, stop orderlar o'chiriladi (ochiq order SL bilan qoladi)
   if(reason == REASON_REMOVE)
      DeleteOrders(-1);
   Comment("");
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   if(TimeCurrent() < g_pauseUntil)
      return;

   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) || !MQLInfoInteger(MQL_TRADE_ALLOWED))
     {
      Comment("TrailReverse: Algo Trading o'chirilgan.");
      return;
     }

   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick) || tick.bid <= 0 || tick.ask <= 0)
      return;

   //--- bir vaqtda faqat bitta ochiq order: eng yangisi qoladi, eskisi yopiladi
   bool  closedOld = false;
   ulong pos       = SyncPositions(closedOld);
   if(closedOld)
      return;

   bool timeOk = InTradingTime();

   if(pos == 0)
     {
      if(!timeOk)
         DeleteOrders(-1);                         // ish vaqtidan tashqarida kirish yo'q
      else if(InpStartMode == START_BUY && !HasOrders())
         OpenFirstBuy(tick);                       // "Darhol BUY" rejimida birinchi kirish
      else
        {
         //--- ochiq order yo'q: ikki tomonda stop order (videodagi "Video Buy/Sell Stop")
         ManageFlatStop(ORDER_TYPE_BUY_STOP, tick);
         ManageFlatStop(ORDER_TYPE_SELL_STOP, tick);
        }
     }
   else if(posInfo.SelectByTicket(pos))
     {
      bool isBuy = (posInfo.PositionType() == POSITION_TYPE_BUY);

      if(!timeOk && InpCloseAtEnd)
        {
         DeleteOrders(-1);
         if(!trade.PositionClose(pos))
            Fail("Vaqt tugadi, orderni yopish");
        }
      else
        {
         double sl = TrailPosition(pos, tick);                 // SL narx ketidan suriladi
         DeleteOrders(isBuy ? ORDER_TYPE_BUY_STOP : ORDER_TYPE_SELL_STOP);
         if(timeOk && sl > 0)                                   // teskari order SL joyida ("Dynamic")
            ManageReverseOrder(isBuy ? ORDER_TYPE_SELL_STOP : ORDER_TYPE_BUY_STOP, sl, tick);
         else
            DeleteOrders(-1);
        }
     }

   ShowStatus(timeOk, pos);
  }

//==================================================================== Ochiq order
//--- "Darhol BUY" rejimi: SL kirish narxidan "Masofa" pastda
void OpenFirstBuy(const MqlTick &tick)
  {
   double sl = NormPrice(tick.ask - Distance());
   if(!trade.Buy(g_lot, _Symbol, 0.0, sl, 0.0, "TrailReverse"))
      Fail("BUY ochish");
  }

//--- Robotning eng yangi ochiq orderini qaytaradi, qolganlarini yopadi
ulong SyncPositions(bool &closedOld)
  {
   closedOld = false;
   ulong newest     = 0;
   long  newestTime = -1;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      if(!SelectMyPosition(i))
         continue;
      long t = PositionGetInteger(POSITION_TIME_MSC);
      if(t > newestTime)
        {
         newestTime = t;
         newest     = posInfo.Ticket();
        }
     }
   if(newest == 0)
      return(0);

   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      if(!SelectMyPosition(i) || posInfo.Ticket() == newest)
         continue;
      closedOld = true;
      if(!trade.PositionClose(posInfo.Ticket()))
         Fail("Eski orderni yopish");
     }
   return(newest);
  }

//--- SL ni narx ketidan suradi (faqat foyda tomonga). Amaldagi SL darajasini qaytaradi.
//--- BUY: SL = Bid - Masofa,  SELL: SL = Ask + Masofa
double TrailPosition(const ulong ticket, const MqlTick &tick)
  {
   if(!posInfo.SelectByTicket(ticket))
      return(0.0);

   bool   isBuy = (posInfo.PositionType() == POSITION_TYPE_BUY);
   double curSL = posInfo.StopLoss();
   double newSL = isBuy ? NormPrice(tick.bid - Distance()) : NormPrice(tick.ask + Distance());

   if(curSL != 0.0)
     {
      double gain = isBuy ? (newSL - curSL) : (curSL - newSL);
      if(gain < MinMove() || InFreeze(curSL, isBuy ? tick.bid : tick.ask))
         return(curSL);
     }
   if(!trade.PositionModify(ticket, newSL, posInfo.TakeProfit()))
     {
      Fail("SL ni surish");
      return(curSL);
     }
   return(newSL);
  }

//==================================================================== Stop orderlar
//--- Ochiq order yo'q: stop order narxdan "Masofa"da turadi va narx ketidan
//--- suriladi (BUY STOP faqat pastga, SELL STOP faqat tepaga)
void ManageFlatStop(const ENUM_ORDER_TYPE type, const MqlTick &tick)
  {
   bool   isBuyStop = (type == ORDER_TYPE_BUY_STOP);
   double price     = isBuyStop ? NormPrice(tick.ask + Distance()) : NormPrice(tick.bid - Distance());

   ulong ticket = FindOrder(type);
   if(ticket == 0)
     {
      PlaceStop(isBuyStop, price);
      return;
     }
   if(!ordInfo.Select(ticket))
      return;
   double cur  = ordInfo.PriceOpen();
   double gain = isBuyStop ? (cur - price) : (price - cur);
   if(gain < MinMove() || InFreeze(cur, isBuyStop ? tick.ask : tick.bid))
      return;
   MoveStop(ticket, isBuyStop, price);
  }

//--- Ochiq order bor: teskari stop order aynan uning SL i turgan joyda turadi
void ManageReverseOrder(const ENUM_ORDER_TYPE type, const double level, const MqlTick &tick)
  {
   bool   isBuyStop = (type == ORDER_TYPE_BUY_STOP);
   double price     = NormPrice(level);

   ulong ticket = FindOrder(type);
   if(ticket == 0)
     {
      PlaceStop(isBuyStop, price);
      return;
     }
   if(!ordInfo.Select(ticket))
      return;
   double cur = ordInfo.PriceOpen();
   if(MathAbs(cur - price) < TickSize() / 2.0)
      return;
   if(InFreeze(cur, isBuyStop ? tick.ask : tick.bid))
      return;
   MoveStop(ticket, isBuyStop, price);
  }

//--- Stop orderning o'z SL i: narxidan "Masofa" uzoqlikda (BUY STOP - pastda, SELL STOP - tepada)
double StopOrderSL(const bool isBuyStop, const double price)
  {
   return(NormPrice(isBuyStop ? price - Distance() : price + Distance()));
  }

void PlaceStop(const bool isBuyStop, const double price)
  {
   double sl = StopOrderSL(isBuyStop, price);
   bool ok = isBuyStop
             ? trade.BuyStop(g_lot, price, _Symbol, sl, 0.0, g_timeType, 0, "TrailReverse")
             : trade.SellStop(g_lot, price, _Symbol, sl, 0.0, g_timeType, 0, "TrailReverse");
   if(!ok)
      Fail(isBuyStop ? "BUY STOP qo'yish" : "SELL STOP qo'yish");
  }

void MoveStop(const ulong ticket, const bool isBuyStop, const double price)
  {
   if(!trade.OrderModify(ticket, price, StopOrderSL(isBuyStop, price), 0.0, g_timeType, 0))
      Fail(isBuyStop ? "BUY STOP ni surish" : "SELL STOP ni surish");
  }

//--- Berilgan turdagi bitta orderni qaytaradi, ortiqcha yoki boshqa lotdagilarni o'chiradi
ulong FindOrder(const ENUM_ORDER_TYPE type)
  {
   ulong found = 0;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      if(!SelectMyOrder(i) || ordInfo.OrderType() != type)
         continue;
      bool wrongLot = (MathAbs(ordInfo.VolumeInitial() - g_lot) > 1e-8);
      if(found == 0 && !wrongLot)
        {
         found = ordInfo.Ticket();
         continue;
        }
      if(!trade.OrderDelete(ordInfo.Ticket()))
         Fail("Ortiqcha orderni o'chirish");
     }
   return(found);
  }

bool HasOrders()
  {
   for(int i = OrdersTotal() - 1; i >= 0; i--)
      if(SelectMyOrder(i))
         return(true);
   return(false);
  }

//--- type < 0 bo'lsa robotning barcha stop orderlari o'chiriladi
void DeleteOrders(const int type)
  {
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      if(!SelectMyOrder(i))
         continue;
      if(type >= 0 && ordInfo.OrderType() != (ENUM_ORDER_TYPE)type)
         continue;
      if(!trade.OrderDelete(ordInfo.Ticket()))
         Fail("Orderni o'chirish");
     }
  }

//==================================================================== Yordamchi
bool SelectMyPosition(const int index)
  {
   return(posInfo.SelectByIndex(index) && posInfo.Symbol() == _Symbol && posInfo.Magic() == InpMagic);
  }

bool SelectMyOrder(const int index)
  {
   return(ordInfo.SelectByIndex(index) && ordInfo.Symbol() == _Symbol && ordInfo.Magic() == InpMagic);
  }

//--- "SS:DD" matnini kun boshidan daqiqaga aylantiradi (xato bo'lsa -1)
int ParseTime(const string text)
  {
   string parts[];
   if(StringSplit(text, ':', parts) != 2)
      return(-1);
   StringTrimLeft(parts[0]);
   StringTrimRight(parts[0]);
   StringTrimLeft(parts[1]);
   StringTrimRight(parts[1]);
   if(StringLen(parts[0]) == 0 || StringLen(parts[1]) == 0)
      return(-1);
   int h = (int)StringToInteger(parts[0]);
   int m = (int)StringToInteger(parts[1]);
   if(h < 0 || h > 23 || m < 0 || m > 59)
      return(-1);
   return(h * 60 + m);
  }

//--- Ish vaqti ichidami (boshlanish kiradi, tugash kirmaydi; tunni kesib o'tishi mumkin)
bool InTradingTime()
  {
   if(!InpUseTime)
      return(true);
   MqlDateTime t;
   TimeCurrent(t);
   int now = t.hour * 60 + t.min;
   if(g_startMin == g_endMin)
      return(true);
   if(g_startMin < g_endMin)
      return(now >= g_startMin && now < g_endMin);
   return(now >= g_startMin || now < g_endMin);
  }

//--- Broker ruxsat bergan eng kichik masofa (punkt)
int MinStopPoints()
  {
   int stops  = (int)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   int freeze = (int)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL);
   int level  = MathMax(stops, freeze);
   return(level > 0 ? level + 1 : 1);
  }

//--- SL va stop order masofasi (broker minimumidan kichik bo'lmaydi)
double Distance()
  {
   return(MathMax(InpDistance, MinStopPoints() * _Point));
  }

double TickSize()
  {
   double ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   return(ts > 0 ? ts : _Point);
  }

double NormPrice(const double price)
  {
   double ts = TickSize();
   return(NormalizeDouble(MathRound(price / ts) * ts, _Digits));
  }

//--- Surish qadami (kamida 1 tik)
double MinMove()
  {
   double ts = TickSize();
   return(MathMax(InpStep, ts) - ts / 2.0);
  }

//--- Narx freeze level ichida bo'lsa, order/SL ni o'zgartirib bo'lmaydi
bool InFreeze(const double level, const double market)
  {
   long freeze = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL);
   return(freeze > 0 && MathAbs(level - market) <= freeze * _Point);
  }

double NormalizeLot(double lot)
  {
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double minL = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxL = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(step > 0)
      lot = MathRound(lot / step) * step;
   lot = MathMax(minL, MathMin(maxL, lot));
   int digits = (step > 0) ? (int)MathMax(0.0, MathCeil(-MathLog10(step) - 1e-9)) : 2;
   return(NormalizeDouble(lot, digits));
  }

void Fail(const string what)
  {
   //--- bozor yopiq (kunlik tanaffus, dam olish): jurnalni to'ldirmasdan 15 soniyadan keyin qayta urinamiz
   if(trade.ResultRetcode() == TRADE_RETCODE_MARKET_CLOSED)
     {
      g_pauseUntil = TimeCurrent() + 15;
      return;
     }
   PrintFormat("TrailReverse | %s: xato %u (%s)", what, trade.ResultRetcode(), trade.ResultRetcodeDescription());
   g_pauseUntil = TimeCurrent() + 1;
  }

void ShowStatus(const bool timeOk, const ulong pos)
  {
   if(MQLInfoInteger(MQL_TESTER) && !MQLInfoInteger(MQL_VISUAL_MODE))
      return;

   string text = "TrailReverse\n";
   if(InpUseTime)
      text += StringFormat("Ish vaqti %s - %s: %s\n", InpStartTime, InpEndTime, timeOk ? "HA" : "YO'Q");
   else
      text += "Ish vaqti: cheklanmagan\n";

   if(pos != 0 && posInfo.SelectByTicket(pos))
      text += StringFormat("Ochiq: %s %.2f | foyda %.2f %s | SL %s\n",
                           posInfo.PositionType() == POSITION_TYPE_BUY ? "BUY" : "SELL",
                           posInfo.Volume(), posInfo.Profit() + posInfo.Swap(),
                           AccountInfoString(ACCOUNT_CURRENCY),
                           DoubleToString(posInfo.StopLoss(), _Digits));
   else
      text += "Ochiq order yo'q\n";

   for(int i = OrdersTotal() - 1; i >= 0; i--)
      if(SelectMyOrder(i))
         text += StringFormat("Stop order: %s %s\n",
                              ordInfo.OrderType() == ORDER_TYPE_BUY_STOP ? "BUY STOP" : "SELL STOP",
                              DoubleToString(ordInfo.PriceOpen(), _Digits));
   Comment(text);
  }
//+------------------------------------------------------------------+
