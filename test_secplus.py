#!/usr/bin/env python3

import random
import unittest
import secplus


class TestSecplus(unittest.TestCase):

    def test_encode_decode(self):
        for _ in range(100000):
            rolling = random.randrange(2**32) & 0xfffffffe
            fixed = random.randrange(3**20)

            rolling_out, fixed_out = secplus.decode(secplus.encode(rolling, fixed))

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(fixed, fixed_out)

    def test_encode_rolling_limit(self):
        rolling = 2**32
        fixed = 3**20 - 1

        with self.assertRaisesRegex(ValueError, "Rolling code must be less than 2\^32"):
            secplus.encode(rolling, fixed)

    def test_encode_fixed_limit(self):
        rolling = 2**32 - 1
        fixed = 3**20

        with self.assertRaisesRegex(ValueError, "Fixed code must be less than 3\^20"):
            secplus.encode(rolling, fixed)

    def test_encode_v2_decode_v2(self):
        for _ in range(100000):
            rolling = random.randrange(2**28)
            fixed = random.randrange(2**40)

            rolling_out, fixed_out = secplus.decode_v2(secplus.encode_v2(rolling, fixed))

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(fixed, fixed_out)

    def test_encode_v2_rolling_limit(self):
        rolling = 2**28
        fixed = 2**40 - 1

        with self.assertRaisesRegex(ValueError, "Rolling code must be less than 2\^28"):
            secplus.encode_v2(rolling, fixed)

    def test_encode_v2_fixed_limit(self):
        rolling = 2**28 - 1
        fixed = 2**40

        with self.assertRaisesRegex(ValueError, "Fixed code must be less than 2\^40"):
            secplus.encode_v2(rolling, fixed)


if __name__ == '__main__':
    unittest.main()
