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

#define CLUSTER_HEAD (TOS_NODE_ID >= CLUSTER_HEAD_MIN_ID)


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
  SC_AQ = 9,
  SC_VOC = 10,
  SC_POWER = 11,
  SC_HEAT = 12,
  SC_DUTY_TIME= 13,
  SC_ERRNO = 14,
  SC_POWER_MIN = 15,
  SC_POWER_MAX = 16,
  SC_POWER_KWH = 17,
  SC_HEAT_ENERGY = 18,
  SC_HEAT_VOLUME = 19,
  SC_D_CO2 = 20,
  SC_D_VOC = 21,
  SC_D_AQ = 22,
  SC_WALL_TEMP = 23,
  SC_D_WALL_TEMP = 24,
  SC_WALL_HUM = 25,
  SC_D_WALL_HUM = 26, 
  SC_OPTI = 40,
  SC_TEMPADC1 = 41,
  SC_D_TEMPADC1 = 42,
  SC_GAS = 43,
  SC_D_OPTI = 44,
  SC_WINDOW = 45,
  SC_BB = 46,
  SC_D_BB = 47,
  SC_SIZE = 48, // SC_SIZE must be 1 greater than last entry

  /* procedure for increasing SC_SIZE:
   *
   *  1. first check if old_size + 7 // 8 == new_size + 7 // 8
   *  (where // is integer divide).
   *  
   *  2. if this is NOT the case, change AM_STATEMSG to a new
   *  value. This will ensure that packets from old nodes do not
   *  break BaseLogger.
   */

  SC_PACKED_SIZE = 15, /* SC_PACKED_SIZE must allow for maximum number
			  of simultaneous sensing modes */
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
  RS_AQ = 6,
  RS_VOC = 7,
  RS_POWER = 8,
  RS_HM_ENERGY = 9,
  RS_HM_VOLUME = 10,
  RS_DUTY = 11,
  RS_OPTI = 12,
  RS_CLAMP = 13,
  RS_TEMPADC1 = 14,
  RS_GAS= 15,
  RS_WINDOW= 16,
  RS_AC= 17,
  RS_BB=18,
  RS_WALL_TEMP=19,
  RS_WALL_HUM=20,
  RS_SIZE = 21 // must be 1 greater than last entry
};

//separate packets structure for mote type

enum {
  AM_ACKMSG = 3,
  AM_STATEV1MSG = 4,
  AM_CONFIGMSG = 5,
  DIS_SETTINGS = 6,
  AM_STATEMSG = 7,
  AM_BOOTMSG = 8,
  SPECIAL = 0xc7,
  MAX_HOPS = 4,
  NODE_TYPE_BASE = 0,
  NODE_TYPE_HEATMETER = 4,
  NODE_TYPE_OPTI = 5,
  NODE_TYPE_TEMP = 6,
  NODE_TYPE_GAS = 7,
  NODE_TYPE_WINDOW = 8,
  CLUSTER_HEAD_CO2_TYPE = 10,
  CLUSTER_HEAD_VOC_TYPE = 11,
  CLUSTER_HEAD_CC_TYPE = 12,
  CLUSTER_HEAD_BB_TYPE = 13,
  CLUSTER_HEAD_WALL_TYPE = 14,
  CLUSTER_HEAD_MIN_ID = 10 << 12 //min cluster head type
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
  ERR_HEARTBEAT = 13,
  ERR_ACK_CRC_CORRUPT = 17,
  ERR_PACK_STATE_OVERFLOW = 19
};



enum {
  ERR_QUEUE_FULL = 1,
  ERR_UART_FAIL = 2,
}; //root errors (only in range 1-7)

enum {
  NODE_TYPE_MAX = 15
};


typedef nx_struct StateMsg {
  nx_uint16_t ctp_parent_id;
  nx_uint32_t timestamp;
  nx_uint8_t special;
  nx_uint8_t seq;
  nx_int16_t rssi;
  nx_uint8_t packed_state_mask[bitset_size(SC_SIZE)];
  nx_float packed_state[SC_PACKED_SIZE];
} StateMsg; // varies depending on SC_SIZE and SC_PACKED_SIZE


typedef nx_struct BootMsg {
  nx_uint8_t special;
  nx_bool clustered;
  nx_uint8_t version[14];
} BootMsg;

typedef nx_struct ConfigPerType {
  nx_uint32_t samplePeriod;
  nx_bool blink;
  nx_uint8_t configured [bitset_size(RS_SIZE)];
} ConfigPerType;

typedef nx_struct ConfigMsg {
  nx_uint8_t typeCount;
  ConfigPerType byType [NODE_TYPE_MAX + 1];
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
