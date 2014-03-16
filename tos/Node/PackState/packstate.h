/*************************************************************
 *
 * packstate.h
 *
 * <insert gpl header>
 *
 * pack or unpack a series of floating point variables x1, x2, x3 with
 * associated integer keys k1, k2, k3 \in [0,N) into a packed form
 * consisting of a bitvector of length N, and a array of floats.
 *
 * 
 *************************************************************
 */

#ifndef _PACKSTATE_H
#define _PACKSTATE_H

#define bitset_size(X) ((X + 7) / 8)


typedef struct packed_state_t {
  unsigned char mask[bitset_size(SC_SIZE)];
  float p[SC_PACKED_SIZE]; // packed limit is smaller than full set
} packed_state_t;

typedef struct unpacked_state_t {
  float u[SC_SIZE];
} unpacked_state_t;

#endif
