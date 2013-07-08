// -*- c -*- 
#include "packstate.h" 
#ifdef DEBUG
#include "printf.h"
#endif 
generic module PackStateC(uint8_t max_keys) @safe()
{
  provides interface PackState;
  uses interface AccessibleBitVector as Mask;
}
implementation
{
  unpacked_state_t ups;
  int count = 0;

  command void PackState.clear(){
    call Mask.clearAll();
    count = 0;
  }

  command int PackState.add(int key, float value){
    if (key < max_keys && count < SC_PACKED_SIZE) {
      call Mask.set(key);
      ups.u[key] = value;
      count++;
      return SUCCESS;
    }
    else
      return FAIL;
  }
		
  command int PackState.pack(packed_state_t *ps) {
    int i, j;
    memcpy(ps->mask, call Mask.getArray(), call Mask.getArrayLength());
    /** this is a bit of a slow way to do this. it would
	be better if bitset provided an iterator.
    */
    j = 0;
    for (i = 0; i < max_keys; i++) {
      if (call Mask.get(i)) {
	ps->p[j++] = ups.u[i];
      }
    }
    return j;
  }
	
  command void PackState.unpack(packed_state_t *ps) { 
    int i, j;
    memcpy(call Mask.getArray(), ps->mask, call Mask.getArrayLength());

    j = 0;
    count = 0;
    for (i = 0; i < max_keys; i++) { 
      if (call Mask.get(i)) { 
	ups.u[i] = ps->p[j++];
	count++;
      }
    }
  }

  command float PackState.get(int i) { 
    return ups.u[i];
  }

  command int PackState.haskey(int i) { 
    return call Mask.get(i);
  }


}

