// -*- c -*-
#ifdef DEBUG
#  include "printf.h"
#endif
module CurrentCostSerialP
{
  provides interface SplitControl as SerialControl;
  provides interface Msp430UartConfigure;
  uses interface Resource as UartResource;
}

implementation
{

  msp430_uart_union_config_t msp430_uart_2400_config = {
    {
    utxe : 0,		// 1:enable tx module
    urxe :1 ,		// 1:enable rx module
    ubr : UBR_1MHZ_57600,    //Baud rate (use enum msp430_uart_rate_t for predefined rates)  
    umctl: UMCTL_1MHZ_57600, 
    mm : 0,     		//Multiprocessor mode (0=idle-line protocol; 1=address-bit protocol)
    listen: 0,		//Listen enable (0=disabled; 1=enabled, feed tx back to receiver)
    clen: 1,    		//Character length (0=7-bit data; 1=8-bit data)
    spb : 0,    		//Stop bits (0=one stop bit; 1=two stop bits)
    pev : 0,    		//Parity select (0=odd; 1=even)
    pena: 0,   		//Parity enable (0=disabled; 1=enabled)
    urxse: 0,   		//Receive start-edge detection (0=disabled; 1=enabled)
    ssel: 0x02, 		//Clock source (00=UCLKI; 01=ACLK; 10=SMCLK; 11=SMCLK)
    ckpl: 0,    		//Clock polarity (0=normal; 1=inverted)
    urxwie : 0, 		// Wake-up interrupt-enable (0=all set URXIFGx; 1=only address sets URXIFGx)
    urxeie : 0  		// Erroneous-character receive (0=rejected; 1=received and URXIFGx set)
    }
  };

  bool starting = FALSE;
  bool started = FALSE;

  command error_t SerialControl.start() {
    if (starting) 
      return SUCCESS;
    if (started)
      return EALREADY;
    
#ifdef DEBUG
    printf("acquiring uart\n");
    printfflush();
#endif

    starting = TRUE;
    return call UartResource.request();
  }

  event void UartResource.granted() { 
    starting = FALSE;
    started = TRUE;
    signal SerialControl.startDone(SUCCESS);
  }


  task void stopTask() { 
    signal SerialControl.stopDone(SUCCESS);
  }

  command error_t SerialControl.stop() {
    if (starting) 
      return EBUSY;
    if (!started)
      return EALREADY;
    
#ifdef DEBUG
    printf("releasing uart\n");
    printfflush();
#endif 
    
    call UartResource.release();
    started = FALSE;
    post stopTask();
    return SUCCESS;
  }

	
  async command msp430_uart_union_config_t* Msp430UartConfigure.getConfig() {
    return &msp430_uart_2400_config;
  }

}
