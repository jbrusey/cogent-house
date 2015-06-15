// -*- c -*- 

configuration SIPControllerC @safe()
{ 
  provides{
    interface TransmissionControl;
    interface Read<FilterState *> as Sensor[uint8_t id];
  }
  uses{
    interface Predict as SinkStatePredict;
    interface FilterWrapper<FilterState *> as EstimateCurrentState[uint8_t id];
    interface Heartbeat;
  }
}
implementation
{
  components MainC;
  components SIPControllerM;
  

  MainC.SoftwareInit -> SIPControllerM.Init;

  SIPControllerM.TransmissionControl = TransmissionControl;
  SIPControllerM.Sensor = Sensor;
  SIPControllerM.SinkStatePredict = SinkStatePredict;
  SIPControllerM.EstimateCurrentState = EstimateCurrentState;
  SIPControllerM.Heartbeat = Heartbeat;

}
