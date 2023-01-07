/*
 * Copyright 2022 Clayton Smith (argilo@gmail.com)
 *
 * This file is part of secplus.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#include "secplus.h"

static void _v2_calc_parity(const uint64_t fixed, uint32_t *data) {
  uint32_t parity = (fixed >> 32) & 0xf;

  *data &= 0xffff0fff;
  for (int offset = 0; offset < 32; offset += 4) {
    parity ^= ((*data >> offset) & 0xf);
  }
  *data |= (parity << 12);
}

static int _v2_check_parity(const uint64_t fixed, const uint32_t data) {
  uint32_t parity = (fixed >> 32) & 0xf;

  for (int offset = 0; offset < 32; offset += 4) {
    parity ^= ((data >> offset) & 0xf);
  }

  if (parity != 0) {
    return -1;
  }

  return 0;
}

static int _decode_v2_rolling(const uint32_t rolling1, const uint32_t rolling2,
                              uint32_t *rolling) {
  uint32_t rolling_reversed = (rolling2 >> 8) & 3;
  rolling_reversed = (rolling_reversed * 3) + ((rolling1 >> 8) & 3);

  rolling_reversed = (rolling_reversed * 3) + ((rolling2 >> 16) & 3);
  rolling_reversed = (rolling_reversed * 3) + ((rolling2 >> 14) & 3);
  rolling_reversed = (rolling_reversed * 3) + ((rolling2 >> 12) & 3);
  rolling_reversed = (rolling_reversed * 3) + ((rolling2 >> 10) & 3);

  rolling_reversed = (rolling_reversed * 3) + ((rolling1 >> 16) & 3);
  rolling_reversed = (rolling_reversed * 3) + ((rolling1 >> 14) & 3);
  rolling_reversed = (rolling_reversed * 3) + ((rolling1 >> 12) & 3);
  rolling_reversed = (rolling_reversed * 3) + ((rolling1 >> 10) & 3);

  rolling_reversed = (rolling_reversed * 3) + ((rolling2 >> 6) & 3);
  rolling_reversed = (rolling_reversed * 3) + ((rolling2 >> 4) & 3);
  rolling_reversed = (rolling_reversed * 3) + ((rolling2 >> 2) & 3);
  rolling_reversed = (rolling_reversed * 3) + (rolling2 & 3);

  rolling_reversed = (rolling_reversed * 3) + ((rolling1 >> 6) & 3);
  rolling_reversed = (rolling_reversed * 3) + ((rolling1 >> 4) & 3);
  rolling_reversed = (rolling_reversed * 3) + ((rolling1 >> 2) & 3);
  rolling_reversed = (rolling_reversed * 3) + (rolling1 & 3);

  if (rolling_reversed >= 0x10000000) {
    return -1;
  }

  *rolling = 0;
  for (int bit = 0; bit < 28; bit++) {
    *rolling |= ((rolling_reversed >> bit) & 1) << (28 - bit - 1);
  }

  return 0;
}

static int _v2_combine_halves(const uint8_t frame_type, const uint32_t rolling1,
                              const uint32_t rolling2, const uint32_t fixed1,
                              const uint32_t fixed2, const uint16_t data1,
                              const uint16_t data2, uint32_t *rolling,
                              uint64_t *fixed, uint32_t *data) {
  int err = 0;

  err = _decode_v2_rolling(rolling1, rolling2, rolling);
  if (err < 0) {
    return err;
  }

  *fixed = ((uint64_t)fixed1 << 20) | fixed2;

  if (frame_type == 1) {
    *data = (data1 << 16) | data2;

    err = _v2_check_parity(*fixed, *data);
    if (err < 0) {
      return err;
    }
  }

  return 0;
}

static void _encode_v2_rolling(const uint32_t rolling, uint32_t *rolling1,
                               uint32_t *rolling2) {
  uint32_t rolling_reversed = 0;

  for (int bit = 0; bit < 28; bit++) {
    rolling_reversed |= ((rolling >> bit) & 1) << (28 - bit - 1);
  }

  *rolling1 = rolling_reversed % 3;
  rolling_reversed /= 3;
  *rolling1 |= (rolling_reversed % 3) << 2;
  rolling_reversed /= 3;
  *rolling1 |= (rolling_reversed % 3) << 4;
  rolling_reversed /= 3;
  *rolling1 |= (rolling_reversed % 3) << 6;
  rolling_reversed /= 3;

  *rolling2 = rolling_reversed % 3;
  rolling_reversed /= 3;
  *rolling2 |= (rolling_reversed % 3) << 2;
  rolling_reversed /= 3;
  *rolling2 |= (rolling_reversed % 3) << 4;
  rolling_reversed /= 3;
  *rolling2 |= (rolling_reversed % 3) << 6;
  rolling_reversed /= 3;

  *rolling1 |= (rolling_reversed % 3) << 10;
  rolling_reversed /= 3;
  *rolling1 |= (rolling_reversed % 3) << 12;
  rolling_reversed /= 3;
  *rolling1 |= (rolling_reversed % 3) << 14;
  rolling_reversed /= 3;
  *rolling1 |= (rolling_reversed % 3) << 16;
  rolling_reversed /= 3;

  *rolling2 |= (rolling_reversed % 3) << 10;
  rolling_reversed /= 3;
  *rolling2 |= (rolling_reversed % 3) << 12;
  rolling_reversed /= 3;
  *rolling2 |= (rolling_reversed % 3) << 14;
  rolling_reversed /= 3;
  *rolling2 |= (rolling_reversed % 3) << 16;
  rolling_reversed /= 3;

  *rolling1 |= (rolling_reversed % 3) << 8;
  rolling_reversed /= 3;

  *rolling2 |= (rolling_reversed % 3) << 8;
}

static const int8_t _ORDER[16] = {9,  33, 6, -1, 24, 18, 36, -1,
                                  24, 36, 6, -1, -1, -1, -1, -1};
static const int8_t _INVERT[16] = {6, 2, 1, -1, 7,  5,  3,  -1,
                                   4, 0, 5, -1, -1, -1, -1, -1};

static void _v2_scramble(const uint32_t *parts, const uint8_t frame_type,
                         uint8_t *packet_half) {
  const int8_t order = _ORDER[packet_half[0] >> 4];
  const int8_t invert = _INVERT[packet_half[0] & 0xf];
  int out_offset = 10;
  const int end = (frame_type == 0 ? 8 : 0);
  const uint32_t parts_permuted[3] = {
      (invert & 4) ? ~parts[(order >> 4) & 3] : parts[(order >> 4) & 3],
      (invert & 2) ? ~parts[(order >> 2) & 3] : parts[(order >> 2) & 3],
      (invert & 1) ? ~parts[order & 3] : parts[order & 3]};

  for (int i = 18 - 1; i >= end; i--) {
    packet_half[out_offset >> 3] |= ((parts_permuted[0] >> i) & 1)
                                    << (7 - (out_offset % 8));
    out_offset++;
    packet_half[out_offset >> 3] |= ((parts_permuted[1] >> i) & 1)
                                    << (7 - (out_offset % 8));
    out_offset++;
    packet_half[out_offset >> 3] |= ((parts_permuted[2] >> i) & 1)
                                    << (7 - (out_offset % 8));
    out_offset++;
  }
}

static int _v2_unscramble(const uint8_t frame_type, const uint8_t indicator,
                          const uint8_t *packet_half, uint32_t *parts) {
  const int8_t order = _ORDER[indicator >> 4];
  const int8_t invert = _INVERT[indicator & 0xf];
  int out_offset = 10;
  const int end = (frame_type == 0 ? 8 : 0);

  if ((order == -1) || (invert == -1)) {
    return -1;
  }

  uint32_t parts_permuted[3] = {0, 0, 0};
  for (int i = 18 - 1; i >= end; i--) {
    parts_permuted[0] |=
        ((packet_half[out_offset >> 3] >> (7 - (out_offset % 8))) & 1) << i;
    out_offset++;
    parts_permuted[1] |=
        ((packet_half[out_offset >> 3] >> (7 - (out_offset % 8))) & 1) << i;
    out_offset++;
    parts_permuted[2] |=
        ((packet_half[out_offset >> 3] >> (7 - (out_offset % 8))) & 1) << i;
    out_offset++;
  }

  parts[(order >> 4) & 3] =
      (invert & 4) ? ~parts_permuted[0] : parts_permuted[0];
  parts[(order >> 2) & 3] =
      (invert & 2) ? ~parts_permuted[1] : parts_permuted[1];
  parts[order & 3] = (invert & 1) ? ~parts_permuted[2] : parts_permuted[2];

  return 0;
}

static void _encode_v2_half_parts(const uint32_t rolling, const uint32_t fixed,
                                  const uint16_t data, const uint8_t frame_type,
                                  uint8_t *packet_half) {
  const uint32_t parts[3] = {((fixed >> 10) << 8) | (data >> 8),
                             ((fixed & 0x3ff) << 8) | (data & 0xff), rolling};

  packet_half[0] = (uint8_t)rolling;

  _v2_scramble(parts, frame_type, packet_half);
}

static int _decode_v2_half_parts(const uint8_t frame_type,
                                 const uint8_t indicator,
                                 const uint8_t *packet_half, uint32_t *rolling,
                                 uint32_t *fixed, uint16_t *data) {
  int err = 0;
  uint32_t parts[3];

  err = _v2_unscramble(frame_type, indicator, packet_half, parts);
  if (err < 0) {
    return err;
  }

  if ((frame_type == 1) && ((parts[2] & 0xff) != indicator)) {
    return -1;
  }

  for (int i = 8; i < 18; i += 2) {
    if (((parts[2] >> i) & 3) == 3) {
      return -1;
    }
  }

  *rolling = (parts[2] & 0x3ff00) | indicator;
  *fixed = ((parts[0] & 0x3ff00) << 2) | ((parts[1] & 0x3ff00) >> 8);
  *data = ((parts[0] & 0xff) << 8) | (parts[1] & 0xff);

  return 0;
}

static void _encode_v2_half(const uint32_t rolling, const uint32_t fixed,
                            const uint16_t data, const uint8_t frame_type,
                            uint8_t *packet_half) {
  _encode_v2_half_parts(rolling, fixed, data, frame_type, packet_half);

  // shift indicator two bits to the right
  packet_half[1] |= (packet_half[0] & 0x3) << 6;
  packet_half[0] >>= 2;

  // set frame type
  packet_half[0] |= (frame_type << 6);
}

int encode_v2(const uint32_t rolling, const uint64_t fixed, uint32_t data,
              const uint8_t frame_type, uint8_t *packet) {
  uint32_t rolling1, rolling2;
  const int packet_len = (frame_type == 0 ? 10 : 16);

  _encode_v2_rolling(rolling, &rolling1, &rolling2);
  _v2_calc_parity(fixed, &data);

  for (int i = 0; i < packet_len; i++) {
    packet[i] = 0x00;
  }

  _encode_v2_half(rolling1, fixed >> 20, data >> 16, frame_type, &packet[0]);
  _encode_v2_half(rolling2, fixed & 0xfffff, data & 0xffff, frame_type,
                  &packet[packet_len / 2]);

  return 0;
}

static int _decode_v2_half(const uint8_t frame_type, const uint8_t *packet_half,
                           uint32_t *rolling, uint32_t *fixed, uint16_t *data) {
  int err = 0;
  const uint8_t indicator = (packet_half[0] << 2) | (packet_half[1] >> 6);

  if ((packet_half[0] >> 6) != frame_type) {
    return -1;
  }

  err = _decode_v2_half_parts(frame_type, indicator, packet_half, rolling,
                              fixed, data);
  if (err < 0) {
    return err;
  }

  return 0;
}

int decode_v2(uint8_t frame_type, const uint8_t *packet, uint32_t *rolling,
              uint64_t *fixed, uint32_t *data) {
  int err = 0;
  uint32_t rolling1, rolling2;
  uint32_t fixed1, fixed2;
  uint16_t data1, data2;
  const int packet_len = (frame_type == 0 ? 10 : 16);

  err = _decode_v2_half(frame_type, &packet[0], &rolling1, &fixed1, &data1);
  if (err < 0) {
    return err;
  }

  err = _decode_v2_half(frame_type, &packet[packet_len / 2], &rolling2, &fixed2,
                        &data2);
  if (err < 0) {
    return err;
  }

  err = _v2_combine_halves(frame_type, rolling1, rolling2, fixed1, fixed2,
                           data1, data2, rolling, fixed, data);
  if (err < 0) {
    return err;
  }

  return 0;
}

static void _encode_wireline_half(const uint32_t rolling, const uint32_t fixed,
                                  const uint16_t data, uint8_t *packet_half) {
  _encode_v2_half_parts(rolling, fixed, data, 1, packet_half);
}

int encode_wireline(const uint32_t rolling, const uint64_t fixed, uint32_t data,
                    uint8_t *packet) {
  uint32_t rolling1, rolling2;

  _encode_v2_rolling(rolling, &rolling1, &rolling2);
  _v2_calc_parity(fixed, &data);

  packet[0] = 0x55;
  packet[1] = 0x01;
  packet[2] = 0x00;
  for (int i = 3; i < 19; i++) {
    packet[i] = 0x00;
  }

  _encode_wireline_half(rolling1, fixed >> 20, data >> 16, &packet[3]);
  _encode_wireline_half(rolling2, fixed & 0xfffff, data & 0xffff, &packet[11]);

  return 0;
}

static int _decode_wireline_half(const uint8_t *packet_half, uint32_t *rolling,
                                 uint32_t *fixed, uint16_t *data) {
  int err = 0;
  const uint8_t indicator = packet_half[0];

  if ((packet_half[1] >> 6) != 0) {
    return -1;
  }

  err = _decode_v2_half_parts(1, indicator, packet_half, rolling, fixed, data);
  if (err < 0) {
    return err;
  }

  return 0;
}

int decode_wireline(const uint8_t *packet, uint32_t *rolling, uint64_t *fixed,
                    uint32_t *data) {
  int err = 0;
  uint32_t rolling1, rolling2;
  uint32_t fixed1, fixed2;
  uint16_t data1, data2;

  if ((packet[0] != 0x55) || (packet[1] != 0x01) || (packet[2] != 0x00)) {
    return -1;
  }

  err = _decode_wireline_half(&packet[3], &rolling1, &fixed1, &data1);
  if (err < 0) {
    return err;
  }

  err = _decode_wireline_half(&packet[11], &rolling2, &fixed2, &data2);
  if (err < 0) {
    return err;
  }

  err = _v2_combine_halves(1, rolling1, rolling2, fixed1, fixed2, data1, data2,
                           rolling, fixed, data);
  if (err < 0) {
    return err;
  }

  return 0;
}
