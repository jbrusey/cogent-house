// -*- c -*-
configuration CurrentCostSerialC
{
  provides interface SplitControl as UartControl;
  provides interface UartStream;
}

implementation
{
  components new Msp430Uart0C() as UartC;
  UartStream = UartC;
	
  components CurrentCostSerialP;
  UartControl = CurrentCostSerialP;
  CurrentCostSerialP.Msp430UartConfigure <- UartC.Msp430UartConfigure; 
  CurrentCostSerialP.UartResource -> UartC.Resource;	
}
