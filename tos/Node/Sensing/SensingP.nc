// -*- c -*-

#ifdef DEBUG
#include "printfloat.h"
#endif

module SensingP
{
  uses {

    //SIP Modules
    interface Read<FilterState *> as ReadSensor[uint8_t id];
    interface TransmissionControl;
    interface PackState;
    interface LocalTime<TMilli>;

    interface BitVector as ExpectReadDone;
    interface AccessibleBitVector as Configured;
    interface AccessibleBitVector as ConfiguredPhaseTwo;

  }
  provides {
    interface Read<bool> as SensingRead;
  }

}
implementation {

  bool overflow_occurred = FALSE;
  bool phase_one = FALSE;

  task void phaseTwoSensing();
  
  /********* Data Send Methods **********/

  void packstate_add(int key, float value) {
      if (call PackState.add(key, value) == FAIL)
	overflow_occurred = TRUE;
	/*reportError(ERR_PACK_STATE_OVERFLOW);*/
  }



  /* checkDataGathered
   * - only transmit data once all sensors have been read
   */
  task void checkDataGathered() {
    bool allDone = TRUE;
    uint8_t i;

    for (i = 0; i < RS_SIZE; i++) {
      if (call ExpectReadDone.get(i)) {
	allDone = FALSE;
	break;
      }
    }

    if (allDone) {
      if (phase_one) {
	/* if we have only completed phase one, we need now to start
	   any phase two sensing */
	phase_one = FALSE;
	post phaseTwoSensing();
      } /* if phase one */
      else {
#ifdef DEBUG
	printf("allDone %lu\n", call LocalTime.get());
	printfflush();
#endif
	
	if (call TransmissionControl.hasEvent()) {
#ifdef DEBUG
	  printf("hasEvent %lu\n", call LocalTime.get());
	  printfflush();
#endif
	
	  signal SensingRead.readDone(SUCCESS, overflow_occurred);
	} /* if hasEvent */
	else
	  signal SensingRead.readDone(FAIL, overflow_occurred);
      } /* else */
    } /* if allDone */
  }


  /* SensingRead.read
   *
   * - begin sensing cycle by requesting, in parallel, for all active
   * sensors to start reading.
   */
  command error_t SensingRead.read() {
    int i;

    overflow_occurred = FALSE;

    call ExpectReadDone.clearAll();
    call PackState.clear();

    phase_one = TRUE;
    
    for (i = 0; i < RS_SIZE; i++) { 
      if (call Configured.get(i)) {
	call ExpectReadDone.set(i);
	if (call ReadSensor.read[i]() != SUCCESS)
	  call ExpectReadDone.clear(i);
      }
    }
    /* it could be that no sensors are active but we still need to
       send a packet (e.g. for duty cycle info)
    */
    post checkDataGathered();

    return SUCCESS;
  }

  /* perform any phase two sensing */
  task void phaseTwoSensing() {
    int i;
    for (i = 0; i < RS_SIZE; i++) {
      if (call ConfiguredPhaseTwo.get(i)) {
	call ExpectReadDone.set(i);
	if (call ReadSensor.read[i]() != SUCCESS)
	  call ExpectReadDone.clear(i);
      }
    }
    post checkDataGathered();
  }


  event void ReadSensor.readDone[uint8_t id](error_t result, FilterState* data) {
    uint8_t state_code, delta_state_code = 0;

#ifdef DEBUG
    printf("readDone %lu: %u %u\nval=", call LocalTime.get(), id, result);
    printfloat(data->x);
    printf("\ndx=");
    printfloat(data->dx);
    printf("\n");
    printfflush();
#endif

    if (id < RS_NO_DELTA) { 
      /* state with delta */
      state_code = id * 2;
      delta_state_code = state_code + 1;
    }
    else 
      /* state without delta */
      state_code = id + SC_NO_DELTA - RS_NO_DELTA;

    if (call ExpectReadDone.get(id)) { 
      if (result == SUCCESS){
	packstate_add(state_code, data->x);
	if (id < RS_NO_DELTA) 
	  packstate_add(delta_state_code, data->dx);
	  
      }
      call ExpectReadDone.clear(id);
      post checkDataGathered();
	
    }
  }

 default command error_t ReadSensor.read[uint8_t id]() { 
   return FAIL;
 }

}
