#ifndef SENSOR_H
#define SENSOR_H

//Message constructs
typedef nx_struct radio_sense_msg {
  nx_uint16_t node_id; //0 1
  nx_uint32_t timestamp; //2345
} radio_sense_msg_t;

enum {
  AM_RADIO_SENSE_MSG = 8,
  AM_LEAF_ACK_MSG = 9
};

#endif
