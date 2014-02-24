// -*- c -*- 

configuration SIPControllerC @safe()
{ 
  provides{
    interface TransmissionControl;
    interface SIPController<FilterState *>[uint8_t id];
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
  SIPControllerM.SIPController = SIPController;
  SIPControllerM.SinkStatePredict = SinkStatePredict;
  SIPControllerM.EstimateCurrentState = EstimateCurrentState;
  SIPControllerM.Heartbeat = Heartbeat;

}
