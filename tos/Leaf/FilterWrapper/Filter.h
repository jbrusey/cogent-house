#ifndef FILTER_H
#define FILTER_H

typedef struct {
  uint32_t time;
  float z, x, dx;
} FilterState;

#endif
