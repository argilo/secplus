#!/usr/bin/env python3
#
# Copyright 2020,2022-2024 Clayton Smith (argilo@gmail.com)
#
# This file is part of secplus.
#
# secplus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# secplus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with secplus.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import random
import unittest
import secplus
import struct
import sys
from ctypes import *


class TestSecplus(unittest.TestCase):
    test_cycles = int(os.getenv("TEST_CYCLES") or "1000")

    v1_codes = """
    0010000211122102222101112211012101001110
    0021121200000001021001111102210202010102
    1122021222211211102201001020111022200012
    0021202121010102222112202102211011111200
    0002020110221012220212200211121101111221
    0010111102022102222112122001202000100011
    1111012200000020120212012222211000020221
    1100111121120211022112120110112101001112
    1100002102102222001120100222211011210002
    1111122020000012110120022020002011101021
    0010001012101110201120102121011011212201
    0021121222212012000020101012102011210021
    1102221122112110210210220210211212100020
    1120002010000002212110112011002212022110
    0202022201120212212102102202200002022121
    0112102010221010001202101101001100001110
    """.split()

    v1_rolling_list = [
        2320616984, 2320616988, 2320616990, 2320616994,
        3869428096, 3869428100, 3869428102, 3869428106,
        570150738, 570150742, 570150744, 570150748,
        2615434906, 2615434910, 2615434912, 2615434916,
    ]
    v1_fixed_list = [876029923]*4 + [876029922]*4 + [876029921]*4 + [595667170, 72906373, 2397429307, 1235167840]

    v1_pretty = """
    Security+:  rolling=2320616984  fixed=876029923  (id1=2 id0=0 switch=1 remote_id=32445552 button=left)
    Security+:  rolling=2320616988  fixed=876029923  (id1=2 id0=0 switch=1 remote_id=32445552 button=left)
    Security+:  rolling=2320616990  fixed=876029923  (id1=2 id0=0 switch=1 remote_id=32445552 button=left)
    Security+:  rolling=2320616994  fixed=876029923  (id1=2 id0=0 switch=1 remote_id=32445552 button=left)
    Security+:  rolling=3869428096  fixed=876029922  (id1=2 id0=0 switch=0 remote_id=32445552 button=middle)
    Security+:  rolling=3869428100  fixed=876029922  (id1=2 id0=0 switch=0 remote_id=32445552 button=middle)
    Security+:  rolling=3869428102  fixed=876029922  (id1=2 id0=0 switch=0 remote_id=32445552 button=middle)
    Security+:  rolling=3869428106  fixed=876029922  (id1=2 id0=0 switch=0 remote_id=32445552 button=middle)
    Security+:  rolling=570150738  fixed=876029921  (id1=1 id0=2 switch=2 remote_id=32445552 button=right)
    Security+:  rolling=570150742  fixed=876029921  (id1=1 id0=2 switch=2 remote_id=32445552 button=right)
    Security+:  rolling=570150744  fixed=876029921  (id1=1 id0=2 switch=2 remote_id=32445552 button=right)
    Security+:  rolling=570150748  fixed=876029921  (id1=1 id0=2 switch=2 remote_id=32445552 button=right)
    Security+:  rolling=2615434906  fixed=595667170  (id1=0 id0=0 switch=1 pad_id=1478 pin=enter)
    Security+:  rolling=2615434910  fixed=72906373  (id1=0 id0=0 switch=1 pad_id=1478 pin=1234)
    Security+:  rolling=2615434912  fixed=2397429307  (id1=0 id0=0 switch=1 pad_id=1478 pin=1234*)
    Security+:  rolling=2615434916  fixed=1235167840  (id1=0 id0=0 switch=1 pad_id=1478 pin=1234#)
    """.strip().split("\n")

    v2_codes = """
    00010001000010111110001111110110111011100010010110001110011110010011011011011011
    00010000101011110011000010011011010110000010001000000111110101101100100110100110
    00100010011101000101010000101001100000010000100101111000101000001100101100101101
    00100010000000101000111001100000101001010000010110010101111001001111111011011111
    00001000100110110010101001011100110001010010000110111010011010010001001011011011
    00001000010010000100001111101010000111100001101000110101100001101000000100100000
    00000000001111111101110000100111111100000001010110111001010001001010010011011011
    00101010101111101001110000010111111010000001000110111000011010010001001011011001
    00010101010010001010011111110110101001110010100110000111011110111010010011011011
    00010101000100111100111011010010001101010010011000010101000101101000000100100000
    00100000101011010011110000101001000010000010000101001100111100110101101111101101
    00100000011001100101100110011111110100110001100110001110011010110011011111011111
    00000110001010011001110001000011111000100000010110110001011101101011011111011011
    00000101101100101110001110111100000111010000001000111000110000010100100110100110
    00101001011111111000111011001100111010000010100101111001101001000101101100101101
    00101001001001011110001111101000011110100010010110001010011110110011011111011111
    01000100001011011000011010100011110101111001001000001001101011010100100001110010010110011010011110010011110110011110010010010011
    01100110101100101000101100011101111010110001001000000001010101100100001010001101101011111101101011101101001001101001111101111101
    01100110010110110010110111000110100001101010010011011010000111110100000000010110100010100110100010110100010010110010110110110110
    01010001000000101100110011110110011010111101001101101101010100100101100000011110110111010110110011110110110011011111110110110110
    01010000101001000101011110011011100111010000100000000000011101000101010001001010010001011010011000010011010001000011010010010011
    01011000010011011110000000100010000100000111111110110110100011010100101010001101100001101101101001101101101001100001100101100101
    01011000001011011110001001101011011101001100100101101101101101100100100000010111110010110110110011110111110110011010110110110110
    """.split()

    v2_rolling_list = list(range(240124710, 240124726)) + list(range(240129675, 240129682))
    v2_fixed_list = [0x1074c58200]*4 + [0x0e74c58200]*4 + [0x0f74c58200]*4 + [0x1174c58200]*4 + [0xfa36d91000]*3 + [0xe036d91000, 0xe136d91000, 0xe236d91000, 0xe336d91000]
    v2_data_list = [None]*16 + [0xfb03d000]*3 + [0xfb037000, 0xfb036000, 0xfb035000, 0x3000]

    wireline_codes = [
        [0x55, 0x1, 0x0, 0x5a, 0x3a, 0x32, 0xc7, 0x29, 0xb2, 0xc9, 0x65, 0x8a, 0x28, 0xb3, 0xc6, 0x35, 0x52, 0x4e, 0x79],
        [0x55, 0x1, 0x0, 0x15, 0x3e, 0x96, 0x91, 0xec, 0xb6, 0x9a, 0x69, 0x92, 0xa, 0x30, 0xc7, 0x81, 0xe0, 0x46, 0xe1],
        [0x55, 0x1, 0x0, 0x14, 0x28, 0x5f, 0xb5, 0x7e, 0xff, 0xbe, 0xff, 0x84, 0x3a, 0xbb, 0xc6, 0x35, 0x3b, 0x66, 0x77],
        [0x55, 0x1, 0x0, 0x6a, 0x22, 0xf6, 0xde, 0x2b, 0xa4, 0xd3, 0x4d, 0x22, 0x7, 0x34, 0xc7, 0xa9, 0x76, 0x56, 0xe1],
        [0x55, 0x1, 0x0, 0x69, 0x2b, 0xc0, 0x5, 0x46, 0x12, 0x8, 0x4, 0x14, 0x1c, 0xe7, 0x9c, 0x2b, 0xd6, 0x9c, 0xaf],
        [0x55, 0x1, 0x0, 0x48, 0x29, 0x1b, 0x47, 0x60, 0x9a, 0x4d, 0x24, 0x2, 0x1c, 0x74, 0xf1, 0xa9, 0x86, 0x82, 0x5c],
        [0x55, 0x1, 0x0, 0x46, 0x6, 0xec, 0xbe, 0x1d, 0x65, 0xb6, 0x4b, 0xa4, 0x39, 0xef, 0xaa, 0x1e, 0x1f, 0x7f, 0xbd],
        [0x55, 0x1, 0x0, 0xa1, 0x35, 0xd, 0x39, 0x98, 0x69, 0xa4, 0x93, 0x52, 0xe, 0x28, 0xab, 0x99, 0xe0, 0xc2, 0x61],
        [0x55, 0x1, 0x0, 0xa4, 0x27, 0x8e, 0xfb, 0x1c, 0xd6, 0x7f, 0x9b, 0x28, 0x5, 0x93, 0xcf, 0xb4, 0x40, 0xcb, 0x6],
        [0x55, 0x1, 0x0, 0xa2, 0x18, 0x71, 0x96, 0xaa, 0xd, 0x12, 0x61, 0x19, 0x14, 0x80, 0x82, 0x4c, 0x69, 0x68, 0x15],
        [0x55, 0x1, 0x0, 0x49, 0x20, 0x8e, 0x2d, 0xc, 0x1a, 0x4, 0xb, 0x89, 0x8, 0x2, 0x9, 0x22, 0xe4, 0x84, 0xe],
        [0x55, 0x1, 0x0, 0x48, 0x14, 0x14, 0x64, 0x28, 0x88, 0x4d, 0x2c, 0x6a, 0x25, 0xa7, 0xdf, 0xdd, 0xc0, 0x43, 0x47],
        [0x55, 0x1, 0x0, 0x2, 0x1, 0x55, 0x19, 0x28, 0x24, 0x92, 0x59, 0x82, 0x1, 0x2e, 0xbf, 0x69, 0xc4, 0xd2, 0x7c],
        [0x55, 0x1, 0x0, 0x1, 0xa, 0x70, 0xaf, 0xf3, 0x49, 0x24, 0x90, 0x64, 0x37, 0x7e, 0xb3, 0x6b, 0x8d, 0xde, 0xec],
        [0x55, 0x1, 0x0, 0x58, 0x5, 0x38, 0x46, 0xb1, 0x96, 0x5b, 0x24, 0x12, 0x39, 0x24, 0x58, 0x1, 0x44, 0xc2, 0x62],
        [0x55, 0x1, 0x0, 0x56, 0x3b, 0xe3, 0xb9, 0x4e, 0x69, 0xa6, 0x93, 0x4, 0xf, 0xf6, 0x7d, 0xb5, 0x5f, 0xef, 0x72],
    ]

    wireline_rolling_list = list(range(1375, 1383)) + list(range(732, 740))
    wireline_fixed_list = [
        0xc21895590c, 0xc11895590c, 0xc11895590c, 0xc11895590c, 0xc11895590c, 0xc31895590c, 0xc11895590c, 0xc31895590c,
        0x10aad8002e, 0x10aad8002e, 0x10aad8002e, 0x10aad8002e, 0x13aad8002e, 0x13aad8002e, 0x13aad8002e, 0x13aad8002e,
    ]
    wireline_data_list = [
        0xf085, 0x728c, 0x728c, 0x728c, 0x728c, 0xa191, 0x8081, 0x8092,
        0x360e281, 0x260f281, 0x360e281, 0x260f281, 0x8193, 0x8193, 0x8193, 0x8193,
    ]
    wireline_device_id_list = [fixed & 0xf0ffffffff for fixed in wireline_fixed_list]
    wireline_command_list = [
        0x285, 0x18c, 0x18c, 0x18c, 0x18c, 0x391, 0x181, 0x392,
        0x081, 0x081, 0x081, 0x081, 0x393, 0x393, 0x393, 0x393,
    ]
    wireline_payload_list = [
        0x00000, 0x20000, 0x20000, 0x20000, 0x20000, 0x10000, 0x00000, 0x00000,
        0x26003, 0x26002, 0x26003, 0x26002, 0x10000, 0x10000, 0x10000, 0x10000,
    ]

    @classmethod
    def setUpClass(cls):
        if os.getenv("TEST_MODE") == "c":
            print("Testing C implementation.", file=sys.stderr)
            substitute_c()
        elif os.getenv("TEST_MODE") == "avr":
            print("Testing C implementation in AVR simulator.", file=sys.stderr)
            cls._process = substitute_avr()
        else:
            print("Testing Python implementation.", file=sys.stderr)

    @classmethod
    def tearDownClass(cls):
        if os.getenv("TEST_MODE") == "avr":
            shutdown_avr(cls._process)

    def test_encode_decode(self):
        for _ in range(self.test_cycles):
            rolling = random.randrange(2**32) & 0xfffffffe
            fixed = random.randrange(3**20)

            rolling_out, fixed_out = secplus.decode(secplus.encode(rolling, fixed))

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(fixed, fixed_out)

    def test_encode_rolling_limit(self):
        rolling = 2**32
        fixed = 3**20 - 1

        with self.assertRaises(ValueError) as cm:
            secplus.encode(rolling, fixed)
        self.assertEqual(str(cm.exception), "Rolling code must be less than 2^32")

    def test_encode_fixed_limit(self):
        rolling = 2**32 - 1
        fixed = 3**20

        with self.assertRaises(ValueError) as cm:
            secplus.encode(rolling, fixed)
        self.assertIn(str(cm.exception), ["Fixed code must be less than 3^20", "Invalid input"])

    def test_encode(self):
        for code, rolling, fixed in zip(self.v1_codes, self.v1_rolling_list, self.v1_fixed_list):
            code = [int(bit) for bit in code]
            code_out = secplus.encode(rolling, fixed)

            self.assertEqual(code, code_out)

    def test_encode_ook_fast(self):
        for code, rolling, fixed in zip(self.v1_codes, self.v1_rolling_list, self.v1_fixed_list):
            ook_out = secplus.encode_ook(rolling, fixed)
            ook = "0001" \
                + "".join("0" * (3-int(bit)) + "1" * (1+int(bit)) for bit in code[:20]) \
                + "0000000000000000000000000000000000000000" \
                + "0111" \
                + "".join("0" * (3-int(bit)) + "1" * (1+int(bit)) for bit in code[20:]) \
                + "0000000000000000000000000000000000000000"
            ook = [int(bit) for bit in ook]
            self.assertEqual(ook, ook_out)

    def test_encode_ook_slow(self):
        for code, rolling, fixed in zip(self.v1_codes, self.v1_rolling_list, self.v1_fixed_list):
            ook_out = secplus.encode_ook(rolling, fixed, fast=False)
            ook = "0001" \
                + "".join("0" * (3-int(bit)) + "1" * (1+int(bit)) for bit in code[:20]) \
                + ("0" * 116) \
                + "0111" \
                + "".join("0" * (3-int(bit)) + "1" * (1+int(bit)) for bit in code[20:]) \
                + ("0" * 116)
            ook = [int(bit) for bit in ook]
            self.assertEqual(ook, ook_out)

    def test_decode(self):
        for code, rolling, fixed in zip(self.v1_codes, self.v1_rolling_list, self.v1_fixed_list):
            code = [int(bit) for bit in code]
            rolling_out, fixed_out = secplus.decode(code)

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(fixed, fixed_out)

    def test_decode_robustness(self):
        for _ in range(self.test_cycles):
            random_code = [random.randrange(3) for _ in range(40)]
            rolling, fixed = secplus.decode(random_code)
            self.assertLessEqual(rolling, 2**32-1)
            self.assertLessEqual(fixed, 3**20-1)

    def test_pretty(self):
        for pretty, rolling, fixed in zip(self.v1_pretty, self.v1_rolling_list, self.v1_fixed_list):
            pretty = pretty.lstrip()
            pretty_out = secplus.pretty(rolling, fixed)
            self.assertEqual(pretty, pretty_out)

    def test_pretty_invalid_pin(self):
        for pin in range(11030, 3**9):
            rolling = random.randrange(2**32) & 0xfffffffe
            pad_id = random.randrange(3**7)
            fixed = pin * (3**10) + pad_id * (3**3)
            pretty = f"Security+:  rolling={rolling}  fixed={fixed}  (id1=0 id0=0 switch=0 pad_id={pad_id})"
            pretty_out = secplus.pretty(rolling, fixed)
            self.assertEqual(pretty, pretty_out)

    def test_encode_v2_decode_v2(self):
        for _ in range(self.test_cycles):
            rolling = random.randrange(2**28)
            fixed = random.randrange(2**40)

            rolling_out, fixed_out, data_out = secplus.decode_v2(secplus.encode_v2(rolling, fixed))

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(fixed, fixed_out)
            self.assertIsNone(data_out)

    def test_encode_v2_decode_v2_with_data(self):
        for _ in range(self.test_cycles):
            rolling = random.randrange(2**28)
            fixed = random.randrange(2**40)
            data = random.randrange(2**32)

            rolling_out, fixed_out, data_out = secplus.decode_v2(secplus.encode_v2(rolling, fixed, data))

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(fixed, fixed_out)
            self.assertEqual(data & 0xffff0fff, data_out & 0xffff0fff)

    def test_encode_v2_rolling_limit(self):
        rolling = 2**28
        fixed = 2**40 - 1

        with self.assertRaises(ValueError) as cm:
            secplus.encode_v2(rolling, fixed)
        self.assertIn(str(cm.exception), ["Rolling code must be less than 2^28", "Invalid input"])

    def test_encode_v2_fixed_limit(self):
        rolling = 2**28 - 1
        fixed = 2**40

        with self.assertRaises(ValueError) as cm:
            secplus.encode_v2(rolling, fixed)
        self.assertIn(str(cm.exception), ["Fixed code must be less than 2^40", "Invalid input"])

    def test_encode_v2_data_limit(self):
        rolling = 2**28 - 1
        fixed = 2**40 - 1
        data = 2**32

        with self.assertRaises(ValueError) as cm:
            secplus.encode_v2(rolling, fixed, data)
        self.assertEqual(str(cm.exception), "Data must be less than 2^32")

    def test_encode_v2_parity(self):
        for code, rolling, fixed, data in zip(self.v2_codes, self.v2_rolling_list,
                                              self.v2_fixed_list, self.v2_data_list):
            if data is None:
                continue
            code = [int(bit) for bit in code]
            for parity_errors in range(1, 16):
                code_out = secplus.encode_v2(rolling, fixed, data ^ (parity_errors << 12))
            self.assertEqual(code, code_out)

    def test_encode_v2(self):
        for code, rolling, fixed, data in zip(self.v2_codes, self.v2_rolling_list,
                                              self.v2_fixed_list, self.v2_data_list):
            code = [int(bit) for bit in code]
            code_out = secplus.encode_v2(rolling, fixed, data)

            self.assertEqual(code, code_out)

    def test_encode_v2_manchester_fast(self):
        for code, rolling, fixed, data in zip(self.v2_codes, self.v2_rolling_list,
                                              self.v2_fixed_list, self.v2_data_list):
            manchester_out = secplus.encode_v2_manchester(rolling, fixed, data)
            manchester = "10101010101010101010101010101010010101011010" \
                + "".join("10" if bit == "0" else "01" for bit in code[:len(code) // 2]) \
                + "000000000000000000000000000000000" \
                + "10101010101010101010101010101010010101011001" \
                + "".join("10" if bit == "0" else "01" for bit in code[len(code) // 2:]) \
                + "000000000000000000000000000000000"
            manchester = [int(bit) for bit in manchester]
            self.assertEqual(manchester, manchester_out)

    def test_encode_v2_manchester_slow(self):
        for code, rolling, fixed, data in zip(self.v2_codes, self.v2_rolling_list,
                                              self.v2_fixed_list, self.v2_data_list):
            manchester_out = secplus.encode_v2_manchester(rolling, fixed, data, fast=False)
            manchester = "10101010101010101010101010101010010101011010" \
                + "".join("10" if bit == "0" else "01" for bit in code[:len(code) // 2]) \
                + ("0" * (400 - len(code) - 44)) \
                + "10101010101010101010101010101010010101011001" \
                + "".join("10" if bit == "0" else "01" for bit in code[len(code) // 2:]) \
                + ("0" * (400 - len(code) - 44))
            manchester = [int(bit) for bit in manchester]
            self.assertEqual(manchester, manchester_out)

    def test_decode_v2(self):
        for code, rolling, fixed, data in zip(self.v2_codes, self.v2_rolling_list,
                                              self.v2_fixed_list, self.v2_data_list):
            code = [int(bit) for bit in code]
            rolling_out, fixed_out, data_out = secplus.decode_v2(code)

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(fixed, fixed_out)
            self.assertEqual(data, data_out)

    def test_decode_v2_unsupported_type(self):
        code = [int(bit) for bit in self.v2_codes[0]]

        for offset in (0, 40):
            broken_code = code.copy()
            broken_code[offset] = 1
            broken_code[offset+1] = 0
            with self.assertRaises(ValueError) as cm:
                secplus.decode_v2(broken_code)
            self.assertIn(str(cm.exception), ["Unsupported packet type", "Invalid input"])

    def test_decode_v2_invalid_type(self):
        code = [int(bit) for bit in self.v2_codes[0]]

        for offset in (0, 40):
            broken_code = code.copy()
            broken_code[offset] = 1
            broken_code[offset+1] = 1
            with self.assertRaises(ValueError) as cm:
                secplus.decode_v2(broken_code)
            self.assertIn(str(cm.exception), ["Invalid packet type", "Invalid input"])

    def test_decode_v2_incorrect_payload_length(self):
        for code in self.v2_codes:
            code = [int(bit) for bit in code]
            if len(code) == 80:
                broken_code = code + [random.randrange(2) for _ in range(80, 128)]
            elif len(code) == 128:
                broken_code = code[:80]
            with self.assertRaises(ValueError) as cm:
                secplus.decode_v2(broken_code)
            self.assertIn(str(cm.exception), ["Incorrect payload length", "Invalid input"])

    def test_decode_v2_invalid_ternary(self):
        code = [int(bit) for bit in self.v2_codes[0]]

        for bit in [2, 4, 6, 8, 42, 44, 46, 48]:
            broken_code = code.copy()
            broken_code[bit] = 1
            broken_code[bit+1] = 1
            with self.assertRaises(ValueError) as cm:
                secplus.decode_v2(broken_code)
            self.assertIn(str(cm.exception), ["Illegal value for ternary bit", "Invalid input"])

    def test_decode_v2_invalid_ternary_2(self):
        code = "00101010011101111000010100011000010011100010101001110100011110110010110001000101"
        code = [int(bit) for bit in code]

        for bit in [12, 18, 24, 30, 36, 52, 58, 64, 70, 76]:
            broken_code = code.copy()
            broken_code[bit] = 1
            broken_code[bit+3] = 1
            with self.assertRaises(ValueError) as cm:
                secplus.decode_v2(broken_code)
            self.assertIn(str(cm.exception), ["Illegal value for ternary bit", "Invalid input"])

    def test_decode_v2_incorrect_last_four_ternary(self):
        code = "01001010011101101001101100011110100000111001001011001010001101110100101001100001001100000000001100000000100100001100001000000001"
        code = [int(bit) for bit in code]

        for bit in [42, 48, 54, 60, 106, 112, 118, 124]:
            correct_bit = (code[bit] << 1) | code[bit+3]
            broken_code = code.copy()
            for broken_bit in ((correct_bit + 1) % 3, (correct_bit + 2) % 3):
                broken_code[bit] = broken_bit >> 1
                broken_code[bit+3] = broken_bit & 1
                with self.assertRaises(ValueError) as cm:
                    secplus.decode_v2(broken_code)
                self.assertIn(str(cm.exception), ["Last four ternary bits do not repeat first four", "Invalid input"])

    def test_decode_v2_invalid_rolling_code(self):
        code = "00101010011101111000010100011000010011100010101001110100011110110010110001000101"
        code = [int(bit) for bit in code]

        broken_code = code.copy()
        for bit in [12, 18, 24, 30, 36, 52, 58, 64, 70, 76]:
            broken_code[bit] = 1
            broken_code[bit+3] = 0
        with self.assertRaises(ValueError) as cm:
            secplus.decode_v2(broken_code)
        self.assertIn(str(cm.exception), ["Rolling code was not in expected range", "Invalid input"])

    def test_decode_v2_incorrect_parity(self):
        code = "01001010011101101001101100011110100000111001001011001010001101110100101001100001001100000000001100000000100100001100001000000001"
        code = [int(bit) for bit in code]

        for bit in [22, 25, 28, 31] + list(range(40, 64, 3)) + list(range(41, 64, 3)) + list(range(104, 128, 3)) + list(range(105, 128, 3)):
            broken_code = code.copy()
            broken_code[bit] ^= 1
            with self.assertRaises(ValueError) as cm:
                secplus.decode_v2(broken_code)
            self.assertIn(str(cm.exception), ["Parity bits are incorrect", "Invalid input"])

    def test_decode_v2_robustness(self):
        for _ in range(self.test_cycles):
            random_code = [random.randrange(2) for _ in range([80, 128][random.randrange(2)])]
            try:
                rolling, fixed, data = secplus.decode_v2(random_code)
                self.assertLessEqual(rolling, 2**28-1)
                self.assertLessEqual(fixed, 2**40-1)
                if data is not None:
                    self.assertLessEqual(data, 2**32-1)
            except ValueError:
                pass

        for _ in range(self.test_cycles):
            rolling = random.randrange(2**28)
            fixed = random.randrange(2**40)
            data = random.randrange(2**32)
            code = secplus.encode_v2(rolling, fixed, data)
            random_code = [b if random.randrange(64) > 0 else b ^ 1 for b in code]
            try:
                rolling, fixed, data = secplus.decode_v2(random_code)
                self.assertLessEqual(rolling, 2**28-1)
                self.assertLessEqual(fixed, 2**40-1)
                self.assertLessEqual(data, 2**32-1)
            except ValueError:
                pass

    def test_pretty_v2(self):
        for rolling, fixed, data in zip(self.v2_rolling_list, self.v2_fixed_list, self.v2_data_list):
            button = (fixed >> 32) & 0xf
            remote_id = fixed & 0xf0ffffffff
            pretty = f"Security+ 2.0:  rolling=0x{rolling:07x}  fixed=0x{fixed:010x}  (button={button} remote_id=0x{remote_id:010x})"
            if data is not None:
                if button == 1:
                    pretty += f"  data=0x{data:08x}  (pin=1019* tail=0x000)"
                elif button == 2:
                    pretty += f"  data=0x{data:08x}  (pin=1019# tail=0x000)"
                elif button == 3:
                    pretty += f"  data=0x{data:08x}  (pin=enter tail=0x000)"
                else:
                    pretty += f"  data=0x{data:08x}  (pin=1019 tail=0x000)"
            pretty_out = secplus.pretty_v2(rolling, fixed, data)
            self.assertEqual(pretty, pretty_out)

    def test_encode_wireline_decode_wireline(self):
        for _ in range(self.test_cycles):
            rolling = random.randrange(2**28)
            fixed = random.randrange(2**40)
            data = random.randrange(2**32)

            rolling_out, fixed_out, data_out = secplus.decode_wireline(secplus.encode_wireline(rolling, fixed, data))

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(fixed, fixed_out)
            self.assertEqual(data & 0xffff0fff, data_out & 0xffff0fff)

    def test_decode_wireline_robustness(self):
        for _ in range(self.test_cycles):
            random_code = bytes([0x55, 0x01, 0x00] + [random.randrange(256) for _ in range(16)])
            try:
                rolling, fixed, data = secplus.decode_wireline(random_code)
                self.assertLessEqual(rolling, 2**28-1)
                self.assertLessEqual(fixed, 2**40-1)
                self.assertLessEqual(data, 2**32-1)
            except ValueError:
                pass

        for _ in range(self.test_cycles):
            rolling = random.randrange(2**28)
            fixed = random.randrange(2**40)
            data = random.randrange(2**32)
            code = secplus.encode_wireline(rolling, fixed, data)
            random_code = bytes(b if random.randrange(19) > 0 else random.randrange(256) for b in code)
            try:
                rolling, fixed, data = secplus.decode_wireline(random_code)
                self.assertLessEqual(rolling, 2**28-1)
                self.assertLessEqual(fixed, 2**40-1)
                self.assertLessEqual(data, 2**32-1)
            except ValueError:
                pass

    def test_decode_wireline_input_validation(self):
        with self.assertRaises(ValueError) as cm:
            secplus.decode_wireline("foo")
        self.assertEqual(str(cm.exception), "Input must be bytes")
        with self.assertRaises(ValueError) as cm:
            secplus.decode_wireline(b"foo")
        self.assertEqual(str(cm.exception), "Input must be 19 bytes long")
        with self.assertRaises(ValueError) as cm:
            secplus.decode_wireline(b"foo bar foo bar foo")
        self.assertIn(str(cm.exception), ["First three bytes must be 0x55, 0x01, 0x00", "Invalid input"])

    def test_encode_wireline_rolling_limit(self):
        rolling = 2**28
        fixed = 2**40 - 1
        data = 2**32 - 1

        with self.assertRaises(ValueError) as cm:
            secplus.encode_wireline(rolling, fixed, data)
        self.assertIn(str(cm.exception), ["Rolling code must be less than 2^28", "Invalid input"])

    def test_encode_wireline_fixed_limit(self):
        rolling = 2**28 - 1
        fixed = 2**40
        data = 2**32 - 1

        with self.assertRaises(ValueError) as cm:
            secplus.encode_wireline(rolling, fixed, data)
        self.assertIn(str(cm.exception), ["Fixed code must be less than 2^40", "Invalid input"])

    def test_encode_wireline_data_limit(self):
        rolling = 2**28 - 1
        fixed = 2**40 - 1
        data = 2**32

        with self.assertRaises(ValueError) as cm:
            secplus.encode_wireline(rolling, fixed, data)
        self.assertEqual(str(cm.exception), "Data must be less than 2^32")

    def test_decode_wireline_bits_8_9(self):
        for code in self.wireline_codes:
            for byte_offset in (4, 12):
                for bit_mask in (0x40, 0x80, 0xc0):
                    broken_code = code.copy()
                    broken_code[byte_offset] |= bit_mask
                    with self.assertRaises(ValueError) as cm:
                        secplus.decode_wireline(bytes(broken_code))
                    self.assertIn(str(cm.exception), ["Unexpected values for bits 8 and 9", "Invalid input"])

    def test_encode_wireline_parity(self):
        for code, rolling, fixed, data in zip(self.wireline_codes, self.wireline_rolling_list,
                                              self.wireline_fixed_list, self.wireline_data_list):
            code = bytes(code)
            for parity_errors in range(1, 16):
                code_out = secplus.encode_wireline(rolling, fixed, data ^ (parity_errors << 12))
            self.assertEqual(code, code_out)

    def test_encode_wireline(self):
        for code, rolling, fixed, data in zip(self.wireline_codes, self.wireline_rolling_list,
                                              self.wireline_fixed_list, self.wireline_data_list):
            code = bytes(code)
            code_out = secplus.encode_wireline(rolling, fixed, data)

            self.assertEqual(code, code_out)

    def test_decode_wireline(self):
        for code, rolling, fixed, data in zip(self.wireline_codes, self.wireline_rolling_list,
                                              self.wireline_fixed_list, self.wireline_data_list):
            rolling_out, fixed_out, data_out = secplus.decode_wireline(bytes(code))

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(fixed, fixed_out)
            self.assertEqual(data, data_out)

    def test_encode_wireline_command_decode_wireline_command(self):
        for _ in range(self.test_cycles):
            rolling = random.randrange(2**28)
            device_id = random.randrange(2**40) & 0xf0ffffffff
            command = random.randrange(2**12)
            payload = random.randrange(2**20)

            code = secplus.encode_wireline_command(rolling, device_id, command, payload)
            rolling_out, device_id_out, command_out, payload_out = secplus.decode_wireline_command(code)

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(device_id, device_id_out)
            self.assertEqual(command, command_out)
            self.assertEqual(payload, payload_out)

    def test_decode_wireline_command_robustness(self):
        for _ in range(self.test_cycles):
            random_code = bytes([0x55, 0x01, 0x00] + [random.randrange(256) for _ in range(16)])
            try:
                rolling, device_id, command, payload = secplus.decode_wireline_command(random_code)
                self.assertLessEqual(rolling, 2**28-1)
                self.assertLessEqual(device_id, 2**40-1)
                self.assertEqual(device_id & 0x0f00000000, 0)
                self.assertLessEqual(command, 2**12-1)
                self.assertLessEqual(payload, 2**20-1)
            except ValueError:
                pass

        for _ in range(self.test_cycles):
            rolling = random.randrange(2**28)
            device_id = random.randrange(2**40) & 0xf0ffffffff
            command = random.randrange(2**12)
            payload = random.randrange(2**20)
            code = secplus.encode_wireline_command(rolling, device_id, command, payload)
            random_code = bytes(b if random.randrange(19) > 0 else random.randrange(256) for b in code)
            try:
                rolling, device_id, command, payload = secplus.decode_wireline_command(random_code)
                self.assertLessEqual(rolling, 2**28-1)
                self.assertLessEqual(device_id, 2**40-1)
                self.assertEqual(device_id & 0x0f00000000, 0)
                self.assertLessEqual(command, 2**12-1)
                self.assertLessEqual(payload, 2**20-1)
            except ValueError:
                pass

    def test_decode_wireline_command_input_validation(self):
        with self.assertRaises(ValueError) as cm:
            secplus.decode_wireline_command("foo")
        self.assertEqual(str(cm.exception), "Input must be bytes")
        with self.assertRaises(ValueError) as cm:
            secplus.decode_wireline_command(b"foo")
        self.assertEqual(str(cm.exception), "Input must be 19 bytes long")
        with self.assertRaises(ValueError) as cm:
            secplus.decode_wireline_command(b"foo bar foo bar foo")
        self.assertIn(str(cm.exception), ["First three bytes must be 0x55, 0x01, 0x00", "Invalid input"])

    def test_encode_wireline_command_rolling_limit(self):
        rolling = 2**28
        device_id = 2**40 - 1
        command = 2**12 - 1
        payload = 2**20 - 1

        with self.assertRaises(ValueError) as cm:
            secplus.encode_wireline_command(rolling, device_id, command, payload)
        self.assertIn(str(cm.exception), ["Rolling code must be less than 2^28", "Invalid input"])

    def test_encode_wireline_command_device_id_limit(self):
        rolling = 2**28 - 1
        device_id = 2**40
        command = 2**12 - 1
        payload = 2**20 - 1

        with self.assertRaises(ValueError) as cm:
            secplus.encode_wireline_command(rolling, device_id, command, payload)
        self.assertIn(str(cm.exception), ["Device ID must be less than 2^40", "Invalid input"])

    def test_encode_wireline_command_command_limit(self):
        rolling = 2**28 - 1
        device_id = 2**40 - 1
        command = 2**12
        payload = 2**20 - 1

        with self.assertRaises(ValueError) as cm:
            secplus.encode_wireline_command(rolling, device_id, command, payload)
        self.assertIn(str(cm.exception), ["Command must be less than 2^12", "Invalid input"])

    def test_encode_wireline_command_payload_limit(self):
        rolling = 2**28 - 1
        device_id = 2**40 - 1
        command = 2**12 - 1
        payload = 2**20

        with self.assertRaises(ValueError) as cm:
            secplus.encode_wireline_command(rolling, device_id, command, payload)
        self.assertIn(str(cm.exception), ["Payload value must be less than 2^20", "Invalid input"])

    def test_decode_wireline_command_bits_8_9(self):
        for code in self.wireline_codes:
            for byte_offset in (4, 12):
                for bit_mask in (0x40, 0x80, 0xc0):
                    broken_code = code.copy()
                    broken_code[byte_offset] |= bit_mask
                    with self.assertRaises(ValueError) as cm:
                        secplus.decode_wireline_command(bytes(broken_code))
                    self.assertIn(str(cm.exception), ["Unexpected values for bits 8 and 9", "Invalid input"])

    def test_encode_wireline_command(self):
        for code, rolling, device_id, command, payload in zip(self.wireline_codes,
                                                              self.wireline_rolling_list,
                                                              self.wireline_device_id_list,
                                                              self.wireline_command_list,
                                                              self.wireline_payload_list):
            code = bytes(code)
            code_out = secplus.encode_wireline_command(rolling, device_id, command, payload)

            self.assertEqual(code, code_out)

    def test_decode_wireline_command(self):
        for code, rolling, device_id, command, payload in zip(self.wireline_codes,
                                                              self.wireline_rolling_list,
                                                              self.wireline_device_id_list,
                                                              self.wireline_command_list,
                                                              self.wireline_payload_list):
            rolling_out, device_id_out, command_out, payload_out = secplus.decode_wireline_command(bytes(code))

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(device_id, device_id_out)
            self.assertEqual(command, command_out)
            self.assertEqual(payload, payload_out)


def substitute_c():
    import platform

    if platform.system() == "Linux":
        libsecplus = cdll.LoadLibrary("./libsecplus.so")
    elif platform.system() == "Darwin":
        libsecplus = cdll.LoadLibrary("./libsecplus.dylib")
    else:
        raise Exception("Platform not supported")
    libsecplus.encode_v1.restype = c_int8
    libsecplus.decode_v1.restype = c_int8
    libsecplus.encode_v2.restype = c_int8
    libsecplus.decode_v2.restype = c_int8
    libsecplus.encode_wireline.restype = c_int8
    libsecplus.decode_wireline.restype = c_int8
    libsecplus.encode_wireline_command.restype = c_int8
    libsecplus.decode_wireline_command.restype = c_int8

    def encode(rolling, fixed):
        if rolling >= 2**32:
            raise ValueError("Rolling code must be less than 2^32")
        symbols1 = create_string_buffer(os.urandom(20), 20)
        symbols2 = create_string_buffer(os.urandom(20), 20)
        err = libsecplus.encode_v1(c_uint32(rolling), c_uint32(fixed), symbols1, symbols2)
        if err < 0:
            raise ValueError("Invalid input")
        return list(symbols1.raw + symbols2.raw)

    secplus.encode = encode

    def decode(code):
        symbols1 = create_string_buffer(bytes(code[:20]), 20)
        symbols2 = create_string_buffer(bytes(code[20:]), 20)
        rolling = c_uint32()
        fixed = c_uint32()
        err = libsecplus.decode_v1(symbols1, symbols2, byref(rolling), byref(fixed))
        if err < 0:
            raise ValueError("Invalid input")
        return rolling.value, fixed.value

    secplus.decode = decode

    def encode_v2(rolling, fixed, data=None):
        if data is None:
            packet_len = 5
            frame_type = 0
            data_c = 0
        else:
            if data >= 2**32:
                raise ValueError("Data must be less than 2^32")

            packet_len = 8
            frame_type = 1
            data_c = data
        packet1 = create_string_buffer(os.urandom(packet_len), packet_len)
        packet2 = create_string_buffer(os.urandom(packet_len), packet_len)
        err = libsecplus.encode_v2(c_uint32(rolling), c_uint64(fixed), c_uint32(data_c), c_uint8(frame_type), packet1, packet2)
        if err < 0:
            raise ValueError("Invalid input")

        code = []
        for byte in packet1.raw + packet2.raw:
            for bit in range(8):
                code.append((byte >> (7 - bit)) & 1)
        return code

    secplus.encode_v2 = encode_v2

    def decode_v2(code):
        frame_type = 0 if len(code) == 80 else 1

        code_bytes = []
        for offset in range(0, len(code), 8):
            byte = 0
            for bit in range(8):
                byte |= code[offset + bit] << (7 - bit)
            code_bytes.append(byte)
        packet = bytes(code_bytes)
        packet1 = packet[:len(packet) // 2]
        packet2 = packet[len(packet) // 2:]

        rolling = c_uint32()
        fixed = c_uint64()
        data = c_uint32()

        err = libsecplus.decode_v2(c_uint8(frame_type), packet1, packet2, byref(rolling), byref(fixed), byref(data))
        if err < 0:
            raise ValueError("Invalid input")
        return rolling.value, fixed.value, None if len(code) == 80 else data.value

    secplus.decode_v2 = decode_v2

    def encode_wireline(rolling, fixed, data):
        if data >= 2**32:
            raise ValueError("Data must be less than 2^32")

        packet = create_string_buffer(os.urandom(19), 19)
        err = libsecplus.encode_wireline(c_uint32(rolling), c_uint64(fixed), c_uint32(data), packet)
        if err < 0:
            raise ValueError("Invalid input")
        return packet.raw

    secplus.encode_wireline = encode_wireline

    def decode_wireline(code):
        if not isinstance(code, bytes):
            raise ValueError("Input must be bytes")
        if len(code) != 19:
            raise ValueError("Input must be 19 bytes long")

        rolling = c_uint32()
        fixed = c_uint64()
        data = c_uint32()

        err = libsecplus.decode_wireline(code, byref(rolling), byref(fixed), byref(data))
        if err < 0:
            raise ValueError("Invalid input")
        return rolling.value, fixed.value, data.value

    secplus.decode_wireline = decode_wireline

    def encode_wireline_command(rolling, device_id, command, payload):
        packet = create_string_buffer(os.urandom(19), 19)
        err = libsecplus.encode_wireline_command(c_uint32(rolling), c_uint64(device_id), c_uint16(command), c_uint32(payload), packet)
        if err < 0:
            raise ValueError("Invalid input")
        return packet.raw

    secplus.encode_wireline_command = encode_wireline_command

    def decode_wireline_command(code):
        if not isinstance(code, bytes):
            raise ValueError("Input must be bytes")
        if len(code) != 19:
            raise ValueError("Input must be 19 bytes long")

        rolling = c_uint32()
        device_id = c_uint64()
        command = c_uint16()
        payload = c_uint32()

        err = libsecplus.decode_wireline_command(code, byref(rolling), byref(device_id), byref(command), byref(payload))
        if err < 0:
            raise ValueError("Invalid input")
        return rolling.value, device_id.value, command.value, payload.value

    secplus.decode_wireline_command = decode_wireline_command


def substitute_avr():
    import subprocess

    sim = subprocess.Popen(["simulavr", "-d", "attiny85", "-f", "test/avr_test.elf", "-W", "0x20,-", "-R", "0x22,-", "-T", "exit"],
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def encode(rolling, fixed):
        if rolling >= 2**32:
            raise ValueError("Rolling code must be less than 2^32")

        sim.stdin.write(struct.pack("<BLL", 21, rolling, fixed))
        sim.stdin.flush()
        err = sim.stdout.read(1)[0]
        symbols = sim.stdout.read(40)

        if err != 0:
            raise ValueError("Invalid input")

        return list(symbols)

    secplus.encode = encode

    def decode(code):
        sim.stdin.write(bytes([41]))
        sim.stdin.write(bytes(code))
        sim.stdin.flush()
        err, rolling, fixed = struct.unpack("<BLL", sim.stdout.read(9))
        if err != 0:
            raise ValueError(f"Invalid input")
        return rolling, fixed

    secplus.decode = decode

    def encode_v2(rolling, fixed, data=None):
        if data is None:
            packet_len = 10
            command = 22
            data_c = 0
        else:
            if data >= 2**32:
                raise ValueError("Data must be less than 2^32")

            packet_len = 16
            command = 23
            data_c = data

        sim.stdin.write(struct.pack("<BLQL", command, rolling, fixed, data_c))
        sim.stdin.flush()
        err = sim.stdout.read(1)[0]
        packet = sim.stdout.read(packet_len)

        if err != 0:
            raise ValueError("Invalid input")

        code = []
        for byte in packet:
            for bit in range(8):
                code.append((byte >> (7 - bit)) & 1)
        return code

    secplus.encode_v2 = encode_v2

    def decode_v2(code):
        command = 42 if len(code) == 80 else 43

        code_bytes = []
        for offset in range(0, len(code), 8):
            byte = 0
            for bit in range(8):
                byte |= code[offset + bit] << (7 - bit)
            code_bytes.append(byte)
        packet = bytes(code_bytes)

        sim.stdin.write(bytes([command]))
        sim.stdin.write(packet)
        sim.stdin.flush()
        err, rolling, fixed, data = struct.unpack("<BLQL", sim.stdout.read(17))

        if err != 0:
            raise ValueError(f"Invalid input")
        return rolling, fixed, None if len(code) == 80 else data

    secplus.decode_v2 = decode_v2

    def encode_wireline(rolling, fixed, data):
        if data >= 2**32:
            raise ValueError("Data must be less than 2^32")

        sim.stdin.write(struct.pack("<BLQL", 24, rolling, fixed, data))
        sim.stdin.flush()
        err = sim.stdout.read(1)[0]
        packet = sim.stdout.read(19)

        if err != 0:
            raise ValueError("Invalid input")
        return packet

    secplus.encode_wireline = encode_wireline

    def decode_wireline(code):
        if not isinstance(code, bytes):
            raise ValueError("Input must be bytes")
        if len(code) != 19:
            raise ValueError("Input must be 19 bytes long")

        sim.stdin.write(bytes([44]))
        sim.stdin.write(code)
        sim.stdin.flush()
        err, rolling, fixed, data = struct.unpack("<BLQL", sim.stdout.read(17))

        if err != 0:
            raise ValueError("Invalid input")
        return rolling, fixed, data

    secplus.decode_wireline = decode_wireline

    def encode_wireline_command(rolling, device_id, command, payload):
        sim.stdin.write(struct.pack("<BLQHL", 25, rolling, device_id, command, payload))
        sim.stdin.flush()
        err = sim.stdout.read(1)[0]
        packet = sim.stdout.read(19)

        if err != 0:
            raise ValueError("Invalid input")
        return packet

    secplus.encode_wireline_command = encode_wireline_command

    def decode_wireline_command(code):
        if not isinstance(code, bytes):
            raise ValueError("Input must be bytes")
        if len(code) != 19:
            raise ValueError("Input must be 19 bytes long")

        sim.stdin.write(bytes([45]))
        sim.stdin.write(code)
        sim.stdin.flush()
        err, rolling, device_id, command, payload = struct.unpack("<BLQHL", sim.stdout.read(19))

        if err != 0:
            raise ValueError("Invalid input")
        return rolling, device_id, command, payload

    secplus.decode_wireline_command = decode_wireline_command

    return sim


def shutdown_avr(sim):
    sim.stdin.write(bytes([0]))
    sim.stdin.flush()
    sim.wait()


if __name__ == '__main__':
    result = unittest.main()
    if not result.wasSuccessful():
        sys.exit(1)
