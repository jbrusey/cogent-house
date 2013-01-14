//$Id: AccessibleBitVectorC.nc,v 1.5 2010/01/20 19:59:07 scipio Exp $

/* "Copyright (c) 2000-2003 The Regents of the University of California.  
 * All rights reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its
 * documentation for any purpose, without fee, and without written agreement
 * is hereby granted, provided that the above copyright notice, the following
 * two paragraphs and the author appear in all copies of this software.
 * 
 * IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR
 * DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT
 * OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF THE UNIVERSITY
 * OF CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 * THE UNIVERSITY OF CALIFORNIA SPECIFICALLY DISCLAIMS ANY WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
 * AND FITNESS FOR A PARTICULAR PURPOSE.  THE SOFTWARE PROVIDED HEREUNDER IS
 * ON AN "AS IS" BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO OBLIGATION TO
 * PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS."
 */

/**
 * Generic bit vector implementation. Note that if you use this bit vector
 * from interrupt code, you must use appropriate <code>atomic</code>
 * statements to ensure atomicity. Updated 24/05/2011 to allow  direct
 * access to the bit vector
 *
 * @param max_bits Bit vector length.
 *
 * @author Cory Sharp <cssharp@eecs.berkeley.edu>
 * @author Ross Wilkins <ross.wilkins87@googlemail.com> 
 */

generic module AccessibleBitVectorC(uint16_t max_bits) @safe()
{
  provides interface Init;
  provides interface AccessibleBitVector;
}
implementation
{
  enum
  {
    ELEMENT_SIZE = 8*sizeof(uint8_t),
    ARRAY_SIZE = (max_bits + ELEMENT_SIZE-1) / ELEMENT_SIZE,
  };

  uint8_t m_bits[ ARRAY_SIZE ];

  async command uint8_t* AccessibleBitVector.getArray()
  {
    return m_bits;
  }

  async command void AccessibleBitVector.setArrayElement(int i, uint8_t value)
  {
    m_bits[i]=value;
  }

  async command uint8_t AccessibleBitVector.getArrayLength()
  {
    return ARRAY_SIZE;
  }

  uint16_t getIndex(uint16_t bitnum)
  {
    return bitnum / ELEMENT_SIZE;
  }

  uint16_t getMask(uint16_t bitnum)
  {
    return 1 << (bitnum % ELEMENT_SIZE);
  }

  command error_t Init.init()
  {
    call AccessibleBitVector.clearAll();
    return SUCCESS;
  }

  async command void AccessibleBitVector.clearAll()
  {
    memset(m_bits, 0, sizeof(m_bits));
  }

  async command void AccessibleBitVector.setAll()
  {
    memset(m_bits, 255, sizeof(m_bits));
  }

  async command bool AccessibleBitVector.get(uint16_t bitnum)
  {
    atomic {return (m_bits[getIndex(bitnum)] & getMask(bitnum)) ? TRUE : FALSE;}
  }

  async command void AccessibleBitVector.set(uint16_t bitnum)
  {
    atomic {m_bits[getIndex(bitnum)] |= getMask(bitnum);}
  }

  async command void AccessibleBitVector.clear(uint16_t bitnum)
  {
    atomic {m_bits[getIndex(bitnum)] &= ~getMask(bitnum);}
  }

  async command void AccessibleBitVector.toggle(uint16_t bitnum)
  {
    atomic {m_bits[getIndex(bitnum)] ^= getMask(bitnum);}
  }

  async command void AccessibleBitVector.assign(uint16_t bitnum, bool value)
  {
    if(value)
      call AccessibleBitVector.set(bitnum);
    else
      call AccessibleBitVector.clear(bitnum);
  }

  async command uint16_t AccessibleBitVector.size()
  {
    return max_bits;
  }
}

