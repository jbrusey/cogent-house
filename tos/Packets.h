/* Packets.h - Header file containing all packet formats sent/received

   Copyright (C) 2011 Ross Wilkins

   This File is part of Cogent-House

   Cogent-House is free software: you can redistribute it and/or
   modify it under the terms of the GNU General Public License as
   published by the Free Software Foundation, either version 3 of the
   License, or (at your option) any later version.

   Cogent-House is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
   General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program. If not, see
   <http://www.gnu.org/licenses/>.



===================
Packet Header
===================

Header file containing all packet formats sent/received


:author: Ross Wilkins
:email: ross.wilkins87@googlemail.com
:date:  06/01/2011
*/

#ifndef _PACKETS_H
#define _PACKETS_H

// state codes
enum {
  SC_TEMPERATURE = 0,
  SC_D_TEMPERATURE = 1,
  SC_HUMIDITY = 2,
  SC_D_HUMIDITY = 3,
  SC_PAR = 4,
  SC_TSR = 5,
  SC_VOLTAGE = 6,
  SC_D_VOLTAGE = 7,
  SC_CO2 = 8,
  SC_D_CO2 = 9,
  SC_TEMPADC0 = 10,
  SC_D_TEMPADC0 = 11,
  SC_TEMPADC1 = 12,
  SC_D_TEMPADC1 = 13,
  SC_TEMPADC2 = 14,
  SC_D_TEMPADC2 = 15,
  SC_TEMPADC3 = 16,
  SC_D_TEMPADC3 = 17,
  SC_FLOW1 = 18,
  SC_D_FLOW1 = 19,
  SC_FLOW3 = 20,
  SC_D_FLOW3 = 21,
  SC_FLOW7 = 22,
  SC_D_FLOW7 = 23,
  SC_SOLAR = 24,
  SC_D_SOLAR = 25,
  SC_SOLARADC3 = 26,
  SC_D_SOLARADC3 = 27,
  SC_BLACKBULB = 28,
  SC_D_BLACKBULB = 29,
  SC_DUTY_TIME= 30,
  SC_ERRNO = 31,
  SC_SIZE = 32 // SC_SIZE must be 1 greater than last entry
};

#include "Node/PackState/packstate.h"

// raw sensors
enum { 
  RS_TEMPERATURE = 0,
  RS_HUMIDITY = 1,
  RS_PAR = 2,
  RS_TSR = 3,
  RS_VOLTAGE = 4,
  RS_CO2 = 5,
  RS_TEMPADC0 = 6,
  RS_TEMPADC1 = 7,
  RS_TEMPADC2 = 8,
  RS_TEMPADC3 = 9,
  RS_FLOWADC1 = 10,
  RS_FLOWADC3 = 11,
  RS_FLOWADC7 = 12,
  RS_SOLAR = 13,
  RS_SOLARADC3 = 14,
  RS_BLACKBULB = 15,
  RS_DUTY = 16,
  RS_SIZE = 17 // must be 1 greater than last entry
};


//separate packets structure for mote type

enum {
  AM_ACKMSG = 3,
  AM_STATEV1MSG = 4,
  AM_CONFIGMSG = 5,
  DIS_SETTINGS = 6,
  AM_STATEMSG = 7,
  SPECIAL = 0xc7,
  MAX_HOPS = 4,
  CLUSTER_HEAD_TYPE = 10,
  CLUSTER_HEAD_MIN_TYPE = 10,
};


/* error codes should be prime. As each error occurs during a sense
   cycle, it is multiplied into last_errno. Factorising the
   resulting value gives both the number of occurences and the type.
*/

enum {
  ERR_SEND_CANCEL_FAIL = 2,
  ERR_SEND_TIMEOUT = 3,
  ERR_SEND_FAILED = 5,
  ERR_SEND_WHILE_PACKET_PENDING = 7,
  ERR_SEND_WHILE_SENDING = 11,
  ERR_NO_ACK=13,
  ERR_HEARTBEAT=17
};


enum {
  NODE_TYPE_MAX = 10
};


typedef nx_struct StateMsg {
  nx_uint16_t ctp_parent_id;
  nx_uint32_t timestamp;
  nx_uint8_t special;
  nx_uint8_t seq;
  nx_int16_t rssi;
  nx_uint8_t packed_state_mask[bitset_size(SC_SIZE)];
  nx_float packed_state[SC_SIZE];
} StateMsg; // varies depending on SC_SIZE 


typedef nx_struct ConfigPerType {
  nx_uint32_t samplePeriod;
  nx_bool blink;
  nx_uint8_t configured [bitset_size(RS_SIZE)];
} ConfigPerType;

typedef nx_struct ConfigMsg {
  nx_uint8_t typeCount;
  ConfigPerType byType [NODE_TYPE_MAX];
  nx_uint8_t special;
} ConfigMsg;

typedef struct CRCStruct {
  nx_uint16_t node_id;
  nx_uint16_t seq;
} CRCStruct;

typedef nx_struct AckMsg {
  nx_uint16_t node_id;
  nx_uint8_t seq;
  nx_uint16_t crc;
} AckMsg;


#endif
