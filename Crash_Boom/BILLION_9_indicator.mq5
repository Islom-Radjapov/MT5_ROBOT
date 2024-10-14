

int Login = 31541048;


#property copyright "BILLION Trading Club"
#property link      "https://t.me/+998331583333"
#property version   "9.0"
#property description "Billion Intelligent Robot's  \nTel: +998331583333";
#property description "\n\n\n\n\n\n\t\t\t\tDeveloper  IslomRadjapov   Tel: +998977099197";

#property indicator_chart_window
#property indicator_buffers 2
#property indicator_plots   1
//--- plot ColorArrow


#property indicator_label1  "ColorArrow"
#property indicator_type1   DRAW_COLOR_ARROW
#property indicator_color1  clrRed
#property indicator_style1  STYLE_SOLID
#property indicator_width1  1
 

//--- An indicator buffer for the plot
double ColorArrowBuffer[];
double rsiBuffer[];
double rsiarray[];
//--- A buffer to store color indexes


//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
  {
 
//--- indicator buffers mapping
   SetIndexBuffer(0,ColorArrowBuffer,INDICATOR_DATA);
   SetIndexBuffer(0,ColorArrowBuffer,INDICATOR_COLOR_INDEX);
//--- зададим код символа для отрисовки в PLOT_ARROW
   PlotIndexSetInteger(0,PLOT_ARROW, 234);
//--- зададим cмещение стрелок по вертикали в пикселях 
   PlotIndexSetInteger(0,PLOT_ARROW_SHIFT, -20);
//--- установим в качестве пустого значения 0
   PlotIndexSetDouble(0,PLOT_EMPTY_VALUE, 0);
   PlotIndexSetInteger(0,PLOT_LINE_WIDTH,2);
   
   if ( AccountInfoInteger(ACCOUNT_LOGIN) == Login) { //&& TimeCurrent() < date) {
      return(INIT_SUCCEEDED);
   }
   else {
      Alert("Account not authorized, Contact indicator author to validate account");
      ExpertRemove();
      return(INIT_FAILED);
   }


//---
   //return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
  {
  
  bool candle = false;
//--- Calculation loop
   for(int i = 80000; i < rates_total; i++) {
   
      if (open[i] > close[i]) {
         candle = false;
      }
      
      bool res = false;
      int b=0, s=0;
      

      
      for (int y = 1; y < 25; y++) {
         
         if (close[i-y] < open[i-y]) {
            s++;
         } else if (close[i-y] > open[i-y]) {
            b++;
         }
         
         if (b > 15 && s == 0) {
            if (close[i] - 10000 * _Point < close[i-y]) {
               res = true;
               break;
            }
         }
      }
      

      if (res == true) {
         ColorArrowBuffer[i-1]=close[i-1];
      } else {
         ColorArrowBuffer[i-1]=NULL;
      }
      
   }



//--- return value of prev_calculated for next call
   return(rates_total);
  }
