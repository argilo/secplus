#!/usr/bin/env python3
#
# Copyright 2020 Clayton Smith (argilo@gmail.com)
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

    def test_encode_decode(self):
        for _ in range(20000):
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

    def test_encode_v2_decode_v2(self):
        for _ in range(20000):
            rolling = random.randrange(2**28)
            fixed = random.randrange(2**40)

            rolling_out, fixed_out = secplus.decode_v2(secplus.encode_v2(rolling, fixed))

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(fixed, fixed_out)

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

    def test_decode_v2_zero_bits(self):
        codes = """
        10000000001101101101101101101101101101100000000000110110110110110110110110110110
        01000000001101101101101101101101101101100000000000110110110110110110110110110110
        00000000001101101101101101101101101101101000000000110110110110110110110110110110
        00000000001101101101101101101101101101100100000000110110110110110110110110110110
        """.split()

        for code in codes:
            code = [int(bit) for bit in code]
            with self.assertRaisesRegex(ValueError, "First two bits of packet were not zero"):
                secplus.decode_v2(code)


if __name__ == '__main__':
    unittest.main()
