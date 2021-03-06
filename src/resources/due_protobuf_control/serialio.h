#ifndef __SERIALIO__H__
#define __SERIALIO__H__

#include <Arduino.h>

extern int g_xout;
extern int g_yout;

typedef enum {
  SEARCHING = 1,
  READING = 2,
  READING_ESCAPED = 3,
  DONE = 4
} serial_state_t;

typedef struct {
  uint8_t message_type;
  void (*callback)(char* buffer, int len);
} type_callback_map_t;

typedef enum {
  NACK = 0,
  ACK = 1,
  MOVE = 2
} message_types_t;

void serialio_feed(void);

#endif