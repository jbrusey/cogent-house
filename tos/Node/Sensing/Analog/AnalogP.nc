// -*- c -*-
/*************************************************************
 * AnalogP - module
 * 
 * generic ADC module that uses a 2.5 ref voltage. The ADC 12 bit
 * value is converted into a floating point voltage before being
 * returned.
 *
 * J. Brusey, 16/5/2015
 *************************************************************/

#include <Msp430Adc12.h>
generic module AnalogP(uint8_t channel) {
  provides {
    interface AdcConfigure<const msp430adc12_channel_config_t*>;
    interface Read<float> as ReadFloat;
  }

  uses { 
    interface Read<uint16_t> as ReadAdc;
  }

}
implementation {
  const float MAX_ADC = 4095.f;
  const float REF_VOLT = 2.5f;

  const msp430adc12_channel_config_t config = {
  inch: channel,
  sref: REFERENCE_VREFplus_AVss,
  ref2_5v: REFVOLT_LEVEL_2_5,
  adc12ssel: SHT_SOURCE_ACLK,
  adc12div: SHT_CLOCK_DIV_1,
  sht: SAMPLE_HOLD_4_CYCLES,
  sampcon_ssel: SAMPCON_SOURCE_SMCLK,
  sampcon_id: SAMPCON_CLOCK_DIV_1
  };
  
  async command const msp430adc12_channel_config_t* AdcConfigure.getConfiguration()
  {
    return &config;
  }

  /** ReadFloat.read() starts the read cycle by passing the request to the low-level driver
   */
  command error_t ReadFloat.read() {
    return call ReadAdc.read();
  }

  /** ReadAdc.readDone is signalled from the low-level driver when a sample has been taken. 
   */
  event void ReadAdc.readDone(error_t result, uint16_t val) {
    if (result == SUCCESS) { 
      signal ReadFloat.readDone(result, val / MAX_ADC * REF_VOLT);
    }
    else
      signal ReadFloat.readDone(result, 0.);
  }
}
