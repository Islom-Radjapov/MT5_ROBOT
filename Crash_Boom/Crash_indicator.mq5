//int login1 = 23084175;
int login1 = 31541048;
//datetime date = D'2024.12.31 23:59';


#property indicator_chart_window
#property indicator_buffers 6
#property indicator_plots   4
//--- plot TMA
#property indicator_label1  "TMA"
#property indicator_type1   DRAW_COLOR_LINE
#property indicator_color1  clrWhite, clrWhite, clrWhite
#property indicator_style1  STYLE_SOLID
#property indicator_width1  1
//--- plot Top
#property indicator_label2  "Top"
#property indicator_type2   DRAW_LINE
#property indicator_color2  clrRed
#property indicator_style2  STYLE_SOLID
#property indicator_width2  5
//--- plot Bottom
#property indicator_label3  "Bottom"
#property indicator_type3   DRAW_LINE
#property indicator_color3  clrRed
#property indicator_style3  STYLE_SOLID
#property indicator_width3  5

#property indicator_label4  "Arrow"
#property indicator_type4   DRAW_COLOR_ARROW
#property indicator_color4  clrRed
#property indicator_style4  STYLE_SOLID
#property indicator_width4  3

//--- enums
enum ENUM_INPUT_YES_NO {
   INPUT_YES   =  1, // Yes
   INPUT_NO    =  0  // No
};////                           
//--- input parameters
input string Settings = "All settings are ok";

uint              InpPeriodTMA      =  38;         // TMA period
uint              InpPeriodATR      =  100;        // ATR period
double            InpMultiplierATR  =  2.0;        // ATR multiplier
double            InpThreshold      =  0.5;        // Trend threshold
ENUM_INPUT_YES_NO InpRedraw         =  INPUT_YES;  // Redraw

//--- indicator buffers
double         BufferTMA[];
double         BufferColors[];
double         BufferTop[];
double         BufferBottom[];
double         BufferATR[];
double         ArrowBuffer[];
//--- global variables
double         multiplier;
double         threshold;
int            period_tma;
int            period_atr;
int            period_max;
int            handle_atr;



void OnDeinit(const int reason) {
   REASON_CHARTCHANGE;
   Comment("");
}
  
  
int OnInit() {
//--- set global variables
   period_tma=int(InpPeriodTMA<1 ? 1 : InpPeriodTMA);
   period_atr=int(InpPeriodATR<1 ? 1 : InpPeriodATR);
   period_max=fmax(period_atr,period_tma);
   multiplier=InpMultiplierATR;
   threshold=InpThreshold;
//--- indicator buffers mapping
   SetIndexBuffer(0,BufferTMA,INDICATOR_DATA);
   SetIndexBuffer(1,BufferColors,INDICATOR_COLOR_INDEX);
   SetIndexBuffer(2,BufferTop,INDICATOR_DATA);
   SetIndexBuffer(3,BufferBottom,INDICATOR_DATA);
   SetIndexBuffer(4,BufferATR,INDICATOR_CALCULATIONS);

//--- setting indicator parameters
   //IndicatorSetString(INDICATOR_SHORTNAME,"Line ("+(string)period_tma+","+(string)period_atr+","+DoubleToString(multiplier,1)+","+DoubleToString(threshold,2)+")");
   IndicatorSetInteger(INDICATOR_DIGITS,Digits());
//--- setting buffer arrays as timeseries
   ArraySetAsSeries(BufferTMA,true);
   ArraySetAsSeries(BufferColors,true);
   ArraySetAsSeries(BufferTop,true);
   ArraySetAsSeries(BufferBottom,true);
   ArraySetAsSeries(BufferATR,true);
   //ArraySetAsSeries(ArrowBuffer,true);
   


   
//--- create handles
   ResetLastError();
   handle_atr=iATR(NULL,PERIOD_CURRENT,period_atr);
   if(handle_atr==INVALID_HANDLE) {
      Print("The iATR(",(string)period_atr,") object was not created: Error ",GetLastError());
      return INIT_FAILED;
   }
//---

   if (AccountInfoInteger(ACCOUNT_LOGIN) == login1) {
      //&& TimeCurrent() < date) {
      return(INIT_SUCCEEDED);
   } else {
      Alert("Account not authorized, Contact EA author to validate account");
      Delete_indicator(handle_atr);
      return(INIT_FAILED);
   }
}


//*********************************************************          Start        ***********************************************************************************8
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[]) {
      /*Comment("Indicator timeout => ", date);

   if (TimeCurrent() > date) {
      Alert("The Indicator has expired, Contact author to validate account");
      Delete_indicator(handle_atr);
   }*/
  
//--- Установка массивов буферов как таймсерий
   ArraySetAsSeries(close,true);
//--- Проверка и расчёт количества просчитываемых баров
   if(rates_total<fmax(period_max,4)) return 0;
//--- Проверка и расчёт количества просчитываемых баров
   int limit=rates_total-prev_calculated;
   if(limit>1) {
      limit=rates_total-period_max-2;
      ArrayInitialize(BufferTMA,EMPTY_VALUE);
      ArrayInitialize(BufferColors,2);
      ArrayInitialize(BufferTop,EMPTY_VALUE);
      ArrayInitialize(BufferBottom,EMPTY_VALUE);
      ArrayInitialize(ArrowBuffer,EMPTY_VALUE);
      ArrayInitialize(BufferATR,0);
   }
//--- Подготовка данных
   int count=(limit>1 ? rates_total : 1);
   int copied=CopyBuffer(handle_atr,0,0,count,BufferATR);
   if(copied!=count) return 0;
   
//--- Расчёт индикатора
   for(int i = limit; i >= 0 && !IsStopped(); i--) {
      int tcount = period_tma;
      bool period_last =(i==0 ? true : false);

      while (tcount > 0) {
         tcount = ( !period_last ? 0 : tcount - 1);
         double sum = 0;
         double sumw = (period_tma + 2) * (period_tma + 1) / 2;
         for (int j = 0; j <= period_tma; j++) {
            sum += (period_tma - j + 1) * close[i+j];
            if(InpRedraw) {
               if ( i - j > 0) {
                  sum += (period_tma - j + 1) * close[i-j];
                  sumw += (period_tma - j + 1);
               }
            }
         }
         if(sumw != 0) {
            BufferTMA[i]=sum/sumw;
         }
      }
   }

//--- Канал и Цвет
   for(int i=limit; i>=0 && !IsStopped(); i--) {
      double slope=(BufferTMA[i]-BufferTMA[i+1])/(0.1*BufferATR[i]);
      double range=BufferATR[i]*multiplier;
      BufferTop[i]=BufferTMA[i]+range;
      BufferBottom[i]=BufferTMA[i]-range;
      
      if(slope>threshold)
         BufferColors[i]=BufferColors[i+1]=0;
      else if(slope<-threshold)
         BufferColors[i]=BufferColors[i+1]=1;
      else
         BufferColors[i]=BufferColors[i+1]=2;
     }

   return(rates_total);
  }
//+------------------------------------------------------------------+





 bool LabelCreate(const long              chart_ID=0,               // ID графика 
                 const string            name="Label",             // имя метки 
                 const int               sub_window=0,             // номер подокна 
                 const int               x=0,                      // координата по оси X 
                 const int               y=0,                      // координата по оси Y 
                 const ENUM_BASE_CORNER  corner=CORNER_RIGHT_LOWER, // угол графика для привязки 
                 const string            text="Label",             // текст 
                 const string            font="Arial",             // шрифт 
                 const int               font_size=10,             // размер шрифта 
                 const color             clr=clrRed,               // цвет 
                 const double            angle=0.0,                // наклон текста 
                 const ENUM_ANCHOR_POINT anchor=ANCHOR_LEFT_LOWER, // способ привязки 
                 const bool              back=false,               // на заднем плане 
                 const bool              selection=false,          // выделить для перемещений 
                 const bool              hidden=true,              // скрыт в списке объектов 
                 const long              z_order=0)                // приоритет на нажатие мышью  
   { 
//--- сбросим значение ошибки 
   ResetLastError(); 
//--- создадим текстовую метку 
   if(!ObjectCreate(chart_ID,name,OBJ_LABEL,sub_window,0,0)) { 
      Print(__FUNCTION__, 
            ": не удалось создать текстовую метку! Код ошибки = ",GetLastError()); 
      return(false); 
     } 
//--- установим координаты метки 
   ObjectSetInteger(chart_ID,name,OBJPROP_XDISTANCE,x); 
   ObjectSetInteger(chart_ID,name,OBJPROP_YDISTANCE,y); 
//--- установим угол графика, относительно которого будут определяться координаты точки 
   ObjectSetInteger(chart_ID,name,OBJPROP_CORNER,corner); 
//--- установим текст 
   ObjectSetString(chart_ID,name,OBJPROP_TEXT,text); 
//--- установим шрифт текста 
   ObjectSetString(chart_ID,name,OBJPROP_FONT,font); 
//--- установим размер шрифта 
   ObjectSetInteger(chart_ID,name,OBJPROP_FONTSIZE,font_size); 
//--- установим угол наклона текста 
   ObjectSetDouble(chart_ID,name,OBJPROP_ANGLE,angle); 
//--- установим способ привязки 
   ObjectSetInteger(chart_ID,name,OBJPROP_ANCHOR,anchor); 
//--- установим цвет 
   ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr); 
//--- отобразим на переднем (false) или заднем (true) плане 
   ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back); 
//--- включим (true) или отключим (false) режим перемещения метки мышью 
   ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection); 
   ObjectSetInteger(chart_ID,name,OBJPROP_SELECTED,selection); 
//--- скроем (true) или отобразим (false) имя графического объекта в списке объектов 
   ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden); 
//--- установим приоритет на получение события нажатия мыши на графике 
   ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order); 
//--- успешное выполнение 
   return(true); 
  } 
  
  
  
bool LabelDelete(const long   chart_ID = 0,   // ID графика 
                 const string name="Label") // имя метки 
  { 
//--- сбросим значение ошибки 
   ResetLastError(); 
//--- удалим метку 
   if(!ObjectDelete(chart_ID, name)) { 
      Print(__FUNCTION__, 
            ": не удалось удалить текстовую метку! Код ошибки = ",GetLastError()); 
      return(false); 
     } 
//--- успешное выполнение 
   return(true); 
  } 
  



bool Delete_indicator(double MA_handle) {
   long total = ChartGetInteger(ChartID(), CHART_WINDOWS_TOTAL) + 1;
   for(int h = 0; h < total; h++) {
      for(int i = 0; i < ChartIndicatorsTotal(0, h) + 1; i++) {
         ChartIndicatorDelete(0, h, ChartIndicatorName(0, h, i) );
      }
   }
   return 1;
}
