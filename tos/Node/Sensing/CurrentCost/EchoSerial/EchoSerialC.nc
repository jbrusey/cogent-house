/* -*- c -*-

*/

module EchoSerialC
{
  uses
    {		
      interface UartStream as CurrentCostUartStream;
      interface SplitControl as CurrentCostControl;
      interface BigAsyncQueue<uint8_t> as ByteQueue;
      interface Boot;
      interface Leds;
    }
}
implementation
{
  event void Boot.booted()
  {
    call CurrentCostControl.start();
  }

  event void CurrentCostControl.startDone(error_t error) {
    printf("got start done %u\n", error);
    printfflush();
    if (error == SUCCESS) { 
      error = call CurrentCostUartStream.enableReceiveInterrupt();
    }

  }


  event void CurrentCostControl.stopDone(error_t error) {
    printf("got stop done %u\n", error);
    printfflush();
  }



  task void printBytes() { 
    uint8_t c;
    
    if (! call ByteQueue.empty()) {
      c = call ByteQueue.dequeue();
      printf("%c", c);
      post printBytes();
    }
  }
      
  // uint16_t queued = 0;

  bool match(char c, uint8_t *state, char* str) {
    if (*state < strlen(str) && c == str[*state]) {
      (*state)++;
      if (str[*state] == 0) {
	*state = 0;
	return TRUE;
      }
    } else {
      *state = 0;
    }
    return FALSE;
  }	

    
  typedef struct tag { 
    char *stag, *etag;
    uint8_t stag_i, etag_i;
    bool in_tag;
  } tag_t;
  


  /** inTag
   */
  bool inTag(uint8_t byte, tag_t *tag) { 

    if (! tag->in_tag) { 
      if (match((char) byte, &(tag->stag_i), tag->stag))
	tag->in_tag = TRUE;
    }
    else {
      if (match((char) byte, &(tag->etag_i), tag->etag))
	tag->in_tag = FALSE;
    }
    return tag->in_tag;
  }

  enum {
    NUM_BEGIN = 0,
    NUM_IN = 1,
    NUM_END = 2,
    NUM_OUT = 3
  };
  uint8_t in_num = NUM_BEGIN;

  bool inNumber(uint8_t byte, uint32_t *value) {
    if (in_num == NUM_BEGIN) { 
      if (byte >= '0' && byte <= '9') {
	in_num = NUM_IN;
	*value = byte - '0';
      }
    }
    else if (in_num == NUM_IN) {
      if (byte >= '0' && byte <= '9') { 
	*value = (*value) * 10 + (byte - '0');
      }
      else
	in_num = NUM_END;
    }
    else if (in_num == NUM_END)
      in_num = NUM_OUT;
    return in_num;
  }

  tag_t msg = {"<msg>", "</msg>", 0, 0, FALSE };
  tag_t ch1 = {"<ch1><watts>", "</watts></ch1>", 0, 0, FALSE };
  tag_t imp = {"<imp>", "</imp>", 0, 0, FALSE };
  uint32_t watts = 0;
  uint32_t impulses = 0;

  async event void CurrentCostUartStream.receivedByte(uint8_t byte) { 
    call ByteQueue.enqueue(byte);
    post printBytes();
    if (inTag(byte, &msg)) {  
      if (inTag(byte, &ch1)) { 
     	if (inNumber(byte, &watts) == NUM_END) {
	  printf("%lu", watts);
	  printfflush();
     	} 
       } 
      else if (inTag(byte, &imp)) { 
     	if (inNumber(byte, &impulses) == NUM_END) {
	  printf("%lu", impulses);
	  printfflush();
     	} 
       } 

      else { 
     	in_num = NUM_BEGIN; 
 	watts = 0; 
      } 

    } 
  }

  async event void CurrentCostUartStream.receiveDone(uint8_t *buf, uint16_t len, error_t error){}
  async event void CurrentCostUartStream.sendDone(uint8_t* buf, uint16_t len, error_t error) { }


}

