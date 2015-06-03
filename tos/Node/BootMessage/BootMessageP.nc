// -*- c -*-
#include "BootPacket.h"

module BootMessageP
{
  uses {
    interface Timer<TMilli> as BootSendTimeOutTimer;
    interface Send as BootSender;
#ifdef DEBUG
    interface LocalTime<TMilli>;
#endif
  }
  provides {
    interface BootMessage;
  }

}
implementation {
  message_t	message_buffer;

  /** BootMessage.send - at boot time, send an initial packet (without
      checking for ack) that specifies the current version 
   */
  command error_t BootMessage.send()
  {
    BootMsg *newData;
    error_t result;
    uint16_t message_size;
    
#ifdef DEBUG
    printf("BootMessageP: send at %lu\n", call LocalTime.get());
    printfflush();
#endif

    message_size = sizeof (BootMsg);
    newData = call BootSender.getPayload(&message_buffer, message_size);
    if (newData != NULL) { 
      strncpy((char *) newData->version, 
	      make_string(VC_REVISION), 
	      sizeof newData->version);

      call BootSendTimeOutTimer.startOneShot(BOOT_TIMEOUT_TIME);
      
      if ((result = call BootSender.send(&message_buffer, message_size)) == SUCCESS) {
#ifdef DEBUG
	  printf("BootMessageP: message send start at %lu\n", call LocalTime.get());
	  printfflush();
#endif
      }
      return result;
    }
    else
      return FAIL;
  }

  /** BootSender.sendDone - sending of boot message has completed so
      now we can start normal sensing.
   */
  event void BootSender.sendDone(message_t *msg, error_t ok) {
#ifdef DEBUG
    printf("BootMessageP: sendDone at %lu ok=%u\n", call LocalTime.get(), ok);
    printfflush();
#endif
    if (ok == SUCCESS) { 
      call BootSendTimeOutTimer.stop();
      signal BootMessage.sendDone(SUCCESS);
    }
  }

  /** BootSendTimeOutTimer.fired - if the boot send message times out, cancel it
   */
  event void BootSendTimeOutTimer.fired() {
#ifdef DEBUG
    printf("BootMessageP: time out at %lu\n", call LocalTime.get());
    printfflush();
#endif
    call BootSender.cancel(&message_buffer);
    /* don't retry - just get on with the next sensing round */
    signal BootMessage.sendDone(FAIL);
  }
}
