/*
 * Copyright 2022 Clayton Smith (argilo@gmail.com)
 *
 * This file is part of secplus.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#ifndef SECPLUS_H
#define SECPLUS_H

#include <stdint.h>

extern int encode_v2(uint32_t rolling, uint64_t fixed, uint32_t data,
                     uint8_t frame_type, uint8_t *packet);

extern int decode_v2(uint8_t frame_type, const uint8_t *packet,
                     uint32_t *rolling, uint64_t *fixed, uint32_t *data);

extern int encode_wireline(uint32_t rolling, uint64_t fixed, uint32_t data,
                           uint8_t *packet);

extern int decode_wireline(const uint8_t *packet, uint32_t *rolling,
                           uint64_t *fixed, uint32_t *data);

#endif
