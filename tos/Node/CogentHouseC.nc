// -*- c -*-
#include "Packets.h"
#include "Collection.h"
#include "Filter.h"
#include "subtracttime.h"
#include <stdint.h>
#ifdef DEBUG
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#endif 

configuration CogentHouseC {}
implementation
{

  /************* MAIN COMPONENTS ***********/
  
  components MainC, CogentHouseP, LedsC, HilTimerMilliC;
#ifdef DEBUG
  components PrintfC, SerialStartC;
#endif

  CogentHouseP.Boot -> MainC.Boot; 
  CogentHouseP.Leds -> LedsC;
  CogentHouseP.LocalTime -> HilTimerMilliC;

  //BlinkStatus
  components BlinkStatusC;
  CogentHouseP.BlinkStatus -> BlinkStatusC;

  //Timers
  components new TimerMilliC() as SenseTimer;
  components new TimerMilliC() as SendTimeOutTimer;

  CogentHouseP.SenseTimer -> SenseTimer;
  CogentHouseP.SendTimeOutTimer -> SendTimeOutTimer;

  // Instantiate and wire our collection service
  components CollectionC, ActiveMessageC;
  components new CollectionSenderC(AM_STATEMSG) as StateSender;

  CogentHouseP.RadioControl -> ActiveMessageC;
  CogentHouseP.CollectionControl -> CollectionC;
  CogentHouseP.CtpInfo -> CollectionC;
  CogentHouseP.StateSender -> StateSender;

  components new CollectionSenderC(AM_BOOTMSG) as BootSender;
  components BootMessageC;
  CogentHouseP.BootMessage -> BootMessageC;
  BootMessageC.BootSender -> BootSender;
  
  //LPL
  CogentHouseP.LowPowerListening -> ActiveMessageC;

  components SensingC;
  CogentHouseP.PackState -> SensingC;
  CogentHouseP.Configured -> SensingC;
  CogentHouseP.Sensing -> SensingC;
  CogentHouseP.TransmissionControl -> SensingC;


  /*********** ACK CONFIG *************/

  components DisseminationC;
  components new DisseminatorC(AckMsg, AM_ACKMSG);
  components CrcC;

  CogentHouseP.DisseminationControl -> DisseminationC;
  CogentHouseP.AckValue -> DisseminatorC;
  CogentHouseP.CRCCalc -> CrcC;

}
