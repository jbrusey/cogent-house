// -*- c -*-
#define NEW_PRINTF_SEMANTICS
#include "printf.h"
#include "minunit.h"
#include <stdint.h>

#define HIGH_COVARIANCE 1e20

configuration KalmanTestC {}

implementation
{
  components MainC, KalmanTestP;
  components new KalmanC(0., 1., TRUE, 1e-7, 0.0025, HIGH_COVARIANCE) as KalmanDeltaSine;
  components new KalmanC(0., 1., TRUE, 0.02, 0.0025, HIGH_COVARIANCE) as KalmanDelta;
  components new KalmanC(0., 1., TRUE, 0.02, 0.0025, 0.) as KalmanDeltaSineDiscretised;
  components new KalmanC(0., 1., TRUE, 0.02, 0.0025, 0.) as KalmanDeltaSineDiscretisedRandom;
  components new KalmanC(0., 1., TRUE, 0.02, 0.0025, 0.) as KalmanTimeOverflow;
  components PrintfC;
  components SerialStartC;
  components RandomC;
  components LedsC;

  KalmanTestP.Boot -> MainC.Boot; 
  KalmanTestP.Random -> RandomC;
  KalmanTestP.Leds -> LedsC;

  KalmanTestP.KalmanDeltaSine -> KalmanDeltaSine;
  KalmanTestP.KalmanDelta -> KalmanDelta;
  KalmanTestP.KalmanDeltaSineDiscretised -> KalmanDeltaSineDiscretised;
  KalmanTestP.KalmanDeltaSineDiscretisedRandom -> KalmanDeltaSineDiscretisedRandom;
  KalmanTestP.KalmanTimeOverflow -> KalmanTimeOverflow;
}

