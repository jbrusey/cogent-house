#ifndef SENSOR_H
#define SENSOR_H

//Message constructs
typedef nx_struct radio_model_msg  {
	nx_int32_t trigger;
} radio_model_msg_t;

enum {AM_RADIO_MODEL_MSG = 10};

#endif
