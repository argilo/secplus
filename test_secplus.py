#!/usr/bin/env python3
#
# Copyright 2020,2022 Clayton Smith (argilo@gmail.com)
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

import random
import unittest
import secplus


class TestSecplus(unittest.TestCase):
    TEST_CYCLES = 20000

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
    01010001000000101100110011110100001010111111011111111111011111110101100000011110110111010110110011110110110010011111110110110110
    """.split()

    v2_rolling_list = list(range(240124710, 240124726)) + list(range(240129675, 240129679))
    v2_fixed_list = [0x1074c58200]*4 + [0x0e74c58200]*4 + [0x0f74c58200]*4 + [0x1174c58200]*4 + [0xfa36d91000]*3 + [0xe336d91000]
    v2_data_list = [None]*16 + [0xfb03d000]*3 + [0x3000]

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

    def test_encode_decode(self):
        for _ in range(self.TEST_CYCLES):
            rolling = random.randrange(2**32) & 0xfffffffe
            fixed = random.randrange(3**20)

            rolling_out, fixed_out = secplus.decode(secplus.encode(rolling, fixed))

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(fixed, fixed_out)

    def test_encode_rolling_limit(self):
        rolling = 2**32
        fixed = 3**20 - 1

        with self.assertRaisesRegex(ValueError, r"Rolling code must be less than 2\^32"):
            secplus.encode(rolling, fixed)

    def test_encode_fixed_limit(self):
        rolling = 2**32 - 1
        fixed = 3**20

        with self.assertRaisesRegex(ValueError, r"Fixed code must be less than 3\^20"):
            secplus.encode(rolling, fixed)

    def test_encode(self):
        for code, rolling, fixed in zip(self.v1_codes, self.v1_rolling_list, self.v1_fixed_list):
            code = [int(bit) for bit in code]
            code_out = secplus.encode(rolling, fixed)

            self.assertEqual(code, code_out)

    def test_encode_ook_fast(self):
        rolling, fixed = self.v1_rolling_list[0], self.v1_fixed_list[0]
        ook_out = secplus.encode_ook(rolling, fixed)
        ook = "000100010001001100010001000100010111001100110011011101110011000101110111011101110011" \
            + "0000000000000000000000000000000000000000" \
            + "011100010011001100110111011100110011000100110111001100010011000100010011001100110001" \
            + "0000000000000000000000000000000000000000"
        ook = [int(bit) for bit in ook]
        self.assertEqual(ook, ook_out)

    def test_encode_ook_slow(self):
        rolling, fixed = self.v1_rolling_list[0], self.v1_fixed_list[0]
        ook_out = secplus.encode_ook(rolling, fixed, fast=False)
        ook = "000100010001001100010001000100010111001100110011011101110011000101110111011101110011" \
            + "000000000000000000000000000000000000000000000000000000000000" \
            + "00000000000000000000000000000000000000000000000000000000" \
            + "011100010011001100110111011100110011000100110111001100010011000100010011001100110001" \
            + "000000000000000000000000000000000000000000000000000000000000" \
            + "00000000000000000000000000000000000000000000000000000000"
        ook = [int(bit) for bit in ook]
        self.assertEqual(ook, ook_out)

    def test_decode(self):
        for code, rolling, fixed in zip(self.v1_codes, self.v1_rolling_list, self.v1_fixed_list):
            code = [int(bit) for bit in code]
            rolling_out, fixed_out = secplus.decode(code)

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(fixed, fixed_out)

    def test_decode_robustness(self):
        for _ in range(self.TEST_CYCLES):
            random_code = [random.randrange(3) for _ in range(40)]
            rolling, fixed = secplus.decode(random_code)
            self.assertLess(rolling, 2**32)
            self.assertLess(fixed, 3**20)

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
        for _ in range(self.TEST_CYCLES):
            rolling = random.randrange(2**28)
            fixed = random.randrange(2**40)

            rolling_out, fixed_out, data_out = secplus.decode_v2(secplus.encode_v2(rolling, fixed))

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(fixed, fixed_out)
            self.assertIsNone(data_out)

    def test_encode_v2_decode_v2_with_data(self):
        for _ in range(self.TEST_CYCLES):
            rolling = random.randrange(2**28)
            fixed = random.randrange(2**40)
            data = random.randrange(2**32)

            rolling_out, fixed_out, data_out = secplus.decode_v2(secplus.encode_v2(rolling, fixed, data))

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(fixed, fixed_out)
            self.assertEqual(data, data_out)

    def test_encode_v2_rolling_limit(self):
        rolling = 2**28
        fixed = 2**40 - 1

        with self.assertRaisesRegex(ValueError, r"Rolling code must be less than 2\^28"):
            secplus.encode_v2(rolling, fixed)

    def test_encode_v2_fixed_limit(self):
        rolling = 2**28 - 1
        fixed = 2**40

        with self.assertRaisesRegex(ValueError, r"Fixed code must be less than 2\^40"):
            secplus.encode_v2(rolling, fixed)

    def test_encode_v2_data_limit(self):
        rolling = 2**28 - 1
        fixed = 2**40 - 1
        data = 2**32

        with self.assertRaisesRegex(ValueError, r"Data must be less than 2\^32"):
            secplus.encode_v2(rolling, fixed, data)

    def test_encode_v2(self):
        for code, rolling, fixed, data in zip(self.v2_codes, self.v2_rolling_list,
                                              self.v2_fixed_list, self.v2_data_list):
            code = [int(bit) for bit in code]
            code_out = secplus.encode_v2(rolling, fixed, data)

            self.assertEqual(code, code_out)

    def test_encode_v2_manchester(self):
        rolling, fixed = self.v2_rolling_list[0], self.v2_fixed_list[0]
        manchester_out = secplus.encode_v2_manchester(rolling, fixed)
        manchester = "10101010101010101010101010101010010101011010" \
            + "10101001101010011010101001100101010101101010010101010101100101100101011001010110" \
            + "000000000000000000000000000000000" \
            + "10101010101010101010101010101010010101011001" \
            + "10100110100110010110101001010110100101010110100110100101100101100101100101100101" \
            + "000000000000000000000000000000000"
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
            with self.assertRaisesRegex(ValueError, "Unsupported packet type"):
                secplus.decode_v2(broken_code)

    def test_decode_v2_invalid_type(self):
        code = [int(bit) for bit in self.v2_codes[0]]

        for offset in (0, 40):
            broken_code = code.copy()
            broken_code[offset] = 1
            broken_code[offset+1] = 1
            with self.assertRaisesRegex(ValueError, "Invalid packet type"):
                secplus.decode_v2(broken_code)

    def test_decode_v2_incorrect_payload_length(self):
        for code in self.v2_codes:
            code = [int(bit) for bit in code]
            if len(code) == 80:
                broken_code = code + [random.randrange(2) for _ in range(80, 128)]
            elif len(code) == 128:
                broken_code = code[:80]
            with self.assertRaisesRegex(ValueError, "Incorrect payload length"):
                secplus.decode_v2(broken_code)

    def test_decode_v2_invalid_ternary(self):
        code = [int(bit) for bit in self.v2_codes[0]]

        for bit in [2, 4, 6, 8, 42, 44, 46, 48]:
            broken_code = code.copy()
            broken_code[bit] = 1
            broken_code[bit+1] = 1
            with self.assertRaisesRegex(ValueError, "Illegal value for ternary bit"):
                secplus.decode_v2(broken_code)

    def test_decode_v2_invalid_ternary_2(self):
        code = "00101010011101111000010100011000010011100010101001110100011110110010110001000101"
        code = [int(bit) for bit in code]

        for bit in [12, 18, 24, 30, 36, 52, 58, 64, 70, 76]:
            broken_code = code.copy()
            broken_code[bit] = 1
            broken_code[bit+3] = 1
            with self.assertRaisesRegex(ValueError, "Illegal value for ternary bit"):
                secplus.decode_v2(broken_code)

    def test_decode_v2_incorrect_last_four_ternary(self):
        code = "01001010011101101001101100011110100000111001001011001010001101110100101001100001001100000000001100000000100100001100001000000001"
        code = [int(bit) for bit in code]

        for bit in [42, 48, 54, 60, 106, 112, 118, 124]:
            correct_bit = (code[bit] << 1) | code[bit+3]
            broken_code = code.copy()
            for broken_bit in ((correct_bit + 1) % 3, (correct_bit + 2) % 3):
                broken_code[bit] = broken_bit >> 1
                broken_code[bit+3] = broken_bit & 1
                with self.assertRaisesRegex(ValueError, "Last four ternary bits do not repeat first four"):
                    secplus.decode_v2(broken_code)

    def test_decode_v2_invalid_rolling_code(self):
        code = "00101010011101111000010100011000010011100010101001110100011110110010110001000101"
        code = [int(bit) for bit in code]

        broken_code = code.copy()
        for bit in [12, 18, 24, 30, 36, 52, 58, 64, 70, 76]:
            broken_code[bit] = 1
            broken_code[bit+3] = 0
        with self.assertRaisesRegex(ValueError, "Rolling code was not in expected range"):
            secplus.decode_v2(broken_code)

    def test_decode_v2_robustness(self):
        for _ in range(self.TEST_CYCLES):
            random_code = [random.randrange(2) for _ in range(random.choice([80, 128]))]
            try:
                rolling, fixed, data = secplus.decode_v2(random_code)
                self.assertLess(rolling, 2**28)
                self.assertLess(fixed, 2**40)
                if data is not None:
                    self.assertLess(data, 2**32)
            except ValueError:
                pass

        for _ in range(self.TEST_CYCLES):
            rolling = random.randrange(2**28)
            fixed = random.randrange(2**40)
            data = random.randrange(2**32)
            code = secplus.encode_v2(rolling, fixed, data)
            random_code = [b if random.random() > 1/64 else b ^ 1 for b in code]
            try:
                rolling, fixed, data = secplus.decode_v2(random_code)
                self.assertLess(rolling, 2**28)
                self.assertLess(fixed, 2**40)
                self.assertLess(data, 2**32)
            except ValueError:
                pass

    def test_pretty_v2(self):
        for rolling, fixed, data in zip(self.v2_rolling_list, self.v2_fixed_list, self.v2_data_list):
            button = fixed >> 32
            remote_id = fixed & 0xffffffff
            pretty = f"Security+ 2.0:  rolling={rolling}  fixed={fixed}  (button={button} remote_id={remote_id})"
            if data == 0xfb03d000:
                pretty += f"  data={data}  (pin=1019 data3=13 data4=0)"
            elif data == 0x3000:
                pretty += f"  data={data}  (pin=enter)"
            pretty_out = secplus.pretty_v2(rolling, fixed, data)
            self.assertEqual(pretty, pretty_out)

    def test_encode_wireline_decode_wireline(self):
        for _ in range(self.TEST_CYCLES):
            rolling = random.randrange(2**28)
            fixed = random.randrange(2**40)
            data = random.randrange(2**32)

            rolling_out, fixed_out, data_out = secplus.decode_wireline(secplus.encode_wireline(rolling, fixed, data))

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(fixed, fixed_out)
            self.assertEqual(data, data_out)

    def test_decode_wireline_robustness(self):
        for _ in range(self.TEST_CYCLES):
            random_code = bytes([0x55, 0x01, 0x00] + [random.randrange(256) for _ in range(16)])
            try:
                rolling, fixed, data = secplus.decode_wireline(random_code)
                self.assertLess(rolling, 2**28)
                self.assertLess(fixed, 2**40)
                self.assertLess(data, 2**32)
            except ValueError:
                pass

        for _ in range(self.TEST_CYCLES):
            rolling = random.randrange(2**28)
            fixed = random.randrange(2**40)
            data = random.randrange(2**32)
            code = secplus.encode_wireline(rolling, fixed, data)
            random_code = bytes(b if random.random() > 1/19 else random.randrange(256) for b in code)
            try:
                rolling, fixed, data = secplus.decode_wireline(random_code)
                self.assertLess(rolling, 2**28)
                self.assertLess(fixed, 2**40)
                self.assertLess(data, 2**32)
            except ValueError:
                pass

    def test_decode_wireline_input_validation(self):
        with self.assertRaisesRegex(ValueError, "Input must be bytes"):
            secplus.decode_wireline("foo")
        with self.assertRaisesRegex(ValueError, "Input must be 19 bytes long"):
            secplus.decode_wireline(b"foo")
        with self.assertRaisesRegex(ValueError, "First three bytes must be 0x55, 0x01, 0x00"):
            secplus.decode_wireline(b"foo bar foo bar foo")

    def test_encode_wireline_rolling_limit(self):
        rolling = 2**28
        fixed = 2**40 - 1
        data = 2**32 - 1

        with self.assertRaisesRegex(ValueError, r"Rolling code must be less than 2\^28"):
            secplus.encode_wireline(rolling, fixed, data)

    def test_encode_wireline_fixed_limit(self):
        rolling = 2**28 - 1
        fixed = 2**40
        data = 2**32 - 1

        with self.assertRaisesRegex(ValueError, r"Fixed code must be less than 2\^40"):
            secplus.encode_wireline(rolling, fixed, data)

    def test_encode_wireline_data_limit(self):
        rolling = 2**28 - 1
        fixed = 2**40 - 1
        data = 2**32

        with self.assertRaisesRegex(ValueError, r"Data must be less than 2\^32"):
            secplus.encode_wireline(rolling, fixed, data)

    def test_decode_wireline_bits_8_9(self):
        for code in self.wireline_codes:
            for byte_offset in (4, 12):
                for bit_mask in (0x40, 0x80, 0xc0):
                    broken_code = code.copy()
                    broken_code[byte_offset] |= bit_mask
                    with self.assertRaisesRegex(ValueError, "Unexpected values for bits 8 and 9"):
                        secplus.decode_wireline(bytes(broken_code))

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


if __name__ == '__main__':
    unittest.main()
