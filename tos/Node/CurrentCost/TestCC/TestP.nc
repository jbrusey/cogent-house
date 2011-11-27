// -*- c -*-
#include "printf.h"
#include "printfloat.h"
module TestP
{
  provides {
    interface SplitControl as DummySerialControl;
    interface UartStream as DummyUartStream;
  }
  uses {
    interface Boot;
    interface Read<ccStruct *> as ReadWattage;
    interface SplitControl as CurrentCostControl;
    interface Timer<TMilli> as SensingTimer;
    interface Timer<TMilli> as ByteTimer;
    interface LocalTime<TMilli>;
  }

}

implementation
{

  /* ------------------------------------------------------------
   * current cost serial dummy interface
   * ------------------------------------------------------------
   */
  bool starting = FALSE;
  bool started = FALSE;

  task void UartResource_granted() { 
    starting = FALSE;
    started = TRUE;
    signal DummySerialControl.startDone(SUCCESS);
  }

  command error_t DummySerialControl.start() {
    if (starting) 
      return SUCCESS;
    if (started)
      return EALREADY;
    
#ifdef DEBUG
    printf("acquiring uart\n");
    printfflush();
#endif

    starting = TRUE;
    post UartResource_granted();
    return SUCCESS;
  }

  task void stopTask() { 
    signal DummySerialControl.stopDone(SUCCESS);
  }

  command error_t DummySerialControl.stop() {
    if (starting) 
      return EBUSY;
    if (!started)
      return EALREADY;
    
#ifdef DEBUG
    printf("releasing uart\n");
    printfflush();
#endif 
    
    //call UartResource.release();
    started = FALSE;
    post stopTask();
    return SUCCESS;
  }


  /* ------------------------------------------------------------
   *
   * ------------------------------------------------------------
   */
  bool sensing = TRUE;

  enum {
    PERIOD = 30720
  };

  event void Boot.booted()
  {
    call SensingTimer.startOneShot(10240);
    call ByteTimer.startOneShot(100);
    call CurrentCostControl.start();
  }

  event void CurrentCostControl.startDone(error_t error) {
#ifdef DEBUG
    printf("got start done %u\n", error);
    printfflush();
#endif
  }

  event void CurrentCostControl.stopDone(error_t error) {
#ifdef DEBUG
    printf("got stop done %u\n", error);
    printfflush();
#endif
    call SensingTimer.startOneShot(512); 
  }

	
  event void SensingTimer.fired() {
    if (sensing) { 
#ifdef DEBUG
      printf("start read\n");
#endif
      call ReadWattage.read();
      sensing = FALSE;
    }
    else {
#ifdef DEBUG
      printf("requested start\n");
#endif
      call CurrentCostControl.start();
      sensing = TRUE;
      call SensingTimer.startOneShot(PERIOD - 512);
    }
  }
	

  event void ReadWattage.readDone(error_t result, ccStruct *data) {
    if (result == SUCCESS) {
      printf("readDone: ");
      printfloat(data->min);
      printf(", ");
      printfloat(data->average);
      printf(", ");
      printfloat(data->max);
      printf(", ");
      printfloat(data->kwh);
      printf("\n");
    }
    else
      printf("readDone no data\n");

    printfflush();
#ifdef DEBUG
    printf("requested stop\n");
#endif
    call CurrentCostControl.stop();
  }

  /* ------------------------------------------------------------
   * DummyUartStream
   * ------------------------------------------------------------
   */

  async command error_t DummyUartStream.send( uint8_t* buf, uint16_t len )
  {
#ifdef DEBUG
    printf("send called\n");
    printfflush();
#endif
  }
  

  bool ri_enable = FALSE;

  /**
   * Enable the receive byte interrupt. The <code>receive</code> event
   * is signalled each time a byte is received.
   *
   * @return SUCCESS if interrupt was enabled, FAIL otherwise.
   */
  async command error_t DummyUartStream.enableReceiveInterrupt() {
    // start a timer to periodically send another byte from the test data.
    atomic ri_enable = TRUE;
    return SUCCESS;
  }

  /**
   * Disable the receive byte interrupt.
   *
   * @return SUCCESS if interrupt was disabled, FAIL otherwise.
   */
  async command error_t DummyUartStream.disableReceiveInterrupt() {
    atomic ri_enable = FALSE;
    return SUCCESS;
  }


  /**
   * Begin reception of a UART stream. If SUCCESS is returned,
   * <code>receiveDone</code> will be signalled when reception is
   * complete.
   *
   * @param 'uint8_t* COUNT(len) buf' Buffer for received bytes.
   * @param len Number of bytes to receive.
   * @return SUCCESS if request was accepted, FAIL otherwise.
   */
  async command error_t DummyUartStream.receive( uint8_t* buf, uint16_t len ) {}


  int byteState = 0;
  int p = 0;
  char msg1[] = 
"<msg>"
"<src>CC128-v0.11</src>"
"<dsb>00089</dsb>"
"<time>13:02:39</time>"
"<tmpr>18.7</tmpr>"
"<sensor>1</sensor>"
"<id>01234</id>"
"<type>1</type>"
"<ch1>"
"<watts>00345</watts>"
"</ch1>"
"<ch2>"
"<watts>02151</watts>"
"</ch2>"
"<ch3>"
"<watts>00000</watts>"
"</ch3>"
    "<imp>0000030733</imp><ipu>1000</ipu>"
"</msg>\01"
"<msg>"
"<src>CC128-v0.11</src>"
"<dsb>00089</dsb>"
"<time>13:02:39</time>"
"<tmpr>18.7</tmpr>"
"<sensor>1</sensor>"
"<id>01234</id>"
"<type>1</type>"
"<ch1>"
"<watts>06020</watts>"
"</ch1>"
"<ch2>"
"<watts>02151</watts>"
"</ch2>"
"<ch3>"
"<watts>00000</watts>"
"</ch3>"
    "<imp>0000030734</imp><ipu>1000</ipu>"
"</msg>\01"
"<msg>"
"<src>CC128-v0.11</src>"
"<dsb>00089</dsb>"
"<time>13:02:39</time>"
"<tmpr>18.7</tmpr>"
"<sensor>1</sensor>"
"<id>01234</id>"
"<type>1</type>"
"<ch1>"
"<watts>00123</watts>"
"</ch1>"
"<ch2>"
"<watts>02151</watts>"
"</ch2>"
"<ch3>"
"<watts>00000</watts>"
"</ch3>"
    "<imp>0000030735</imp><ipu>1000</ipu>"
"</msg>\01";

  char x [] = 
"<msg>"
"   <src>CC128-v0.11</src>     "
"   <dsb>00089</dsb>         "
"   <time>13:02:39</time>     "
"   <tmpr>18.7</tmpr>         "
"   <sensor>1</sensor>       "
"   <id>01234</id>            "
"   <type>1</type>             "
"   <ch1>                      "
"      <watts>00345</watts>    "
"   </ch1>"
"   <ch2>"
"      <watts>02151</watts>"
"   </ch2>"
"   <ch3>"
"      <watts>00000</watts>"
"   </ch3>"
    "</msg>\01"
"\r\n<msg><tmpr>13.0</tmpr></msg>\01"
"\r\n<msg><d1>12.0</d2></msg>\01"
"<msg>"
"   <src>CC128-v0.11</src>     "
"   <dsb>00089</dsb>         "
"   <time>13:02:39</time>     "
"   <tmpr>18.7</tmpr>         "
"   <sensor>1</sensor>       "
"   <id>01234</id>            "
"   <type>1</type>             "
"   <ch1>                      "
"      <watts>00345</watts>    "
"   </ch1>"
"   <ch2>"
"      <watts>02151</watts>"
"   </ch2>"
"   <ch3>"
"      <watts>00000</watts>"
"   </ch3>"
    "</msg>\01"
;


  event void ByteTimer.fired() {
    uint32_t delay = 10;
    char c;

    switch (byteState) { 
    case 0:
      p = 0;
      byteState++;
      break;
    case 1:
      c = msg1[p++];
      if (c == '\01') { 
	delay = 6000;
	printf("finished a message\n");
	printfflush();
      }
      else {
	atomic if (ri_enable) {
	  printf("%c", c);
	  signal DummyUartStream.receivedByte(c);
	}
      }
      if (p >= strlen(msg1))
	byteState = 0;
      break;
    }
    call ByteTimer.startOneShot(delay);
  }
    
}  
