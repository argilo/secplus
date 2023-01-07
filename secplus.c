/*
 * Copyright 2022 Clayton Smith (argilo@gmail.com)
 *
 * This file is part of secplus.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#include "secplus.h"

static const uint8_t _ORDER[11][3] = {
    {0, 2, 1}, {2, 0, 1}, {0, 1, 2}, {0, 0, 0}, {1, 2, 0}, {1, 0, 2},
    {2, 1, 0}, {0, 0, 0}, {1, 2, 0}, {2, 1, 0}, {0, 1, 2}};

static const uint8_t _INVERT[11][3] = {
    {1, 1, 0}, {0, 1, 0}, {0, 0, 1}, {0, 0, 0}, {1, 1, 1}, {1, 0, 1},
    {0, 1, 1}, {0, 0, 0}, {1, 0, 0}, {0, 0, 0}, {1, 0, 1}};

static void _encode_v2_rolling(uint32_t rolling, uint8_t *rolling1,
                               uint8_t *rolling2) {
  uint32_t rolling_reversed = 0;

  for (int bit = 0; bit < 28; bit++) {
    rolling_reversed |= ((rolling >> bit) & 1) << (28 - bit - 1);
  }

  rolling1[3] = rolling_reversed % 3;
  rolling_reversed /= 3;
  rolling1[2] = rolling_reversed % 3;
  rolling_reversed /= 3;
  rolling1[1] = rolling_reversed % 3;
  rolling_reversed /= 3;
  rolling1[0] = rolling_reversed % 3;
  rolling_reversed /= 3;

  rolling2[3] = rolling_reversed % 3;
  rolling_reversed /= 3;
  rolling2[2] = rolling_reversed % 3;
  rolling_reversed /= 3;
  rolling2[1] = rolling_reversed % 3;
  rolling_reversed /= 3;
  rolling2[0] = rolling_reversed % 3;
  rolling_reversed /= 3;

  rolling1[7] = rolling_reversed % 3;
  rolling_reversed /= 3;
  rolling1[6] = rolling_reversed % 3;
  rolling_reversed /= 3;
  rolling1[5] = rolling_reversed % 3;
  rolling_reversed /= 3;
  rolling1[4] = rolling_reversed % 3;
  rolling_reversed /= 3;

  rolling2[7] = rolling_reversed % 3;
  rolling_reversed /= 3;
  rolling2[6] = rolling_reversed % 3;
  rolling_reversed /= 3;
  rolling2[5] = rolling_reversed % 3;
  rolling_reversed /= 3;
  rolling2[4] = rolling_reversed % 3;
  rolling_reversed /= 3;

  rolling1[8] = rolling_reversed % 3;
  rolling_reversed /= 3;

  rolling2[8] = rolling_reversed % 3;
}

static void _v2_calc_parity(uint64_t fixed, uint32_t *data) {
  uint32_t parity = (fixed >> 32) & 0xf;

  *data &= 0xffff0fff;
  for (int offset = 0; offset < 32; offset += 4) {
    parity ^= ((*data >> offset) & 0xf);
  }
  *data |= (parity << 12);
}

static void _v2_scramble(uint8_t indicator, uint32_t *parts, int bits,
                         int out_offset, uint8_t *packet_half) {
  const uint8_t *order = _ORDER[indicator >> 4];
  const uint8_t *invert = _INVERT[indicator & 0xf];
  uint32_t parts_permuted[3];

  for (int i = 0; i < 3; i++) {
    parts_permuted[i] = invert[i] ? ~parts[order[i]] : parts[order[i]];
  }

  for (int i = bits - 1; i >= 0; i--) {
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

static void _encode_v2_half_parts(uint8_t *rolling, uint32_t fixed,
                                  uint16_t data, uint8_t *indicator,
                                  uint8_t *packet_half) {
  uint32_t parts[3] = {0};

  parts[0] = ((fixed >> 10) << 8) | (data >> 8);
  parts[1] = ((fixed & 0x3ff) << 8) | (data & 0xff);

  parts[2] |= (rolling[4] << 16);
  parts[2] |= (rolling[5] << 14);
  parts[2] |= (rolling[6] << 12);
  parts[2] |= (rolling[7] << 10);
  parts[2] |= (rolling[8] << 8);
  parts[2] |= (rolling[0] << 6);
  parts[2] |= (rolling[1] << 4);
  parts[2] |= (rolling[2] << 2);
  parts[2] |= rolling[3];

  *indicator = (uint8_t)parts[2];

  _v2_scramble(*indicator, parts, 18, 10, packet_half);
}

static void _encode_wireline_half(uint8_t *rolling, uint32_t fixed,
                                  uint16_t data, uint8_t *packet_half) {
  _encode_v2_half_parts(rolling, fixed, data, &packet_half[0], packet_half);
}

int encode_wireline(uint32_t rolling, uint64_t fixed, uint32_t data,
                    uint8_t *packet) {
  uint8_t rolling1[9], rolling2[9];

  _encode_v2_rolling(rolling, rolling1, rolling2);
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
