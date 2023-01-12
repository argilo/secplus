#include <stdint.h>

#include "../src/secplus.h"

#define special_output_port (*((volatile char *)0x20))
#define special_input_port (*((volatile char *)0x22))

void get_bytes(uint8_t *in, uint8_t len) {
  for (int8_t i = 0; i < len; i++) {
    in[i] = special_input_port;
  }
}

void get_uint32(uint32_t *in) {
  for (int8_t i = 0; i < 4; i++) {
    *in >>= 8;
    *in |= (uint32_t)special_input_port << 24;
  }
}

void get_uint64(uint64_t *in) {
  for (int8_t i = 0; i < 8; i++) {
    *in >>= 8;
    *in |= (uint64_t)special_input_port << 56;
  }
}

void put_bytes(uint8_t *out, uint8_t len) {
  for (int8_t i = 0; i < len; i++) {
    special_output_port = out[i];
  }
}

void put_uint32(uint32_t out) {
  for (int8_t i = 0; i < 4; i++) {
    special_output_port = out & 0xff;
    out >>= 8;
  }
}

void put_uint64(uint64_t out) {
  for (int8_t i = 0; i < 8; i++) {
    special_output_port = out & 0xff;
    out >>= 8;
  }
}

void put_err(int8_t out) { special_output_port = out; }

int main() {
  int8_t err;
  int8_t cont = 1;

  uint32_t rolling;
  uint32_t fixed_v1;
  uint64_t fixed_v2;
  uint32_t data;

  uint8_t buf[40];

  while (cont) {
    switch (special_input_port) {
    case 0:
      cont = 0;
      break;
    case 1:
      get_uint32(&rolling);
      get_uint32(&fixed_v1);
      err = encode_v1(rolling, fixed_v1, &buf[0], &buf[20]);
      put_err(err);
      put_bytes(buf, 40);
      break;
    case 2:
      get_uint32(&rolling);
      get_uint64(&fixed_v2);
      get_uint32(&data);
      err = encode_v2(rolling, fixed_v2, data, 0, &buf[0], &buf[5]);
      put_err(err);
      put_bytes(buf, 10);
      break;
    case 3:
      get_uint32(&rolling);
      get_uint64(&fixed_v2);
      get_uint32(&data);
      err = encode_v2(rolling, fixed_v2, data, 1, &buf[0], &buf[8]);
      put_err(err);
      put_bytes(buf, 16);
      break;
    case 4:
      get_uint32(&rolling);
      get_uint64(&fixed_v2);
      get_uint32(&data);
      err = encode_wireline(rolling, fixed_v2, data, buf);
      put_err(err);
      put_bytes(buf, 19);
      break;
    case 5:
      get_bytes(buf, 40);
      err = decode_v1(&buf[0], &buf[20], &rolling, &fixed_v1);
      put_err(err);
      put_uint32(rolling);
      put_uint32(fixed_v1);
      break;
    case 6:
      get_bytes(buf, 10);
      err = decode_v2(0, &buf[0], &buf[5], &rolling, &fixed_v2, &data);
      put_err(err);
      put_uint32(rolling);
      put_uint64(fixed_v2);
      put_uint32(data);
      break;
    case 7:
      get_bytes(buf, 16);
      err = decode_v2(1, &buf[0], &buf[8], &rolling, &fixed_v2, &data);
      put_err(err);
      put_uint32(rolling);
      put_uint64(fixed_v2);
      put_uint32(data);
      break;
    case 8:
      get_bytes(buf, 19);
      err = decode_wireline(buf, &rolling, &fixed_v2, &data);
      put_err(err);
      put_uint32(rolling);
      put_uint64(fixed_v2);
      put_uint32(data);
      break;
    }
  }

  return 0;
}
