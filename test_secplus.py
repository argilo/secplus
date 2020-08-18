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

    def test_encode_v2_decode_v2(self):
        for _ in range(100000):
            rolling = random.randrange(2**28)
            fixed = random.randrange(2**40)

            rolling_out, fixed_out = secplus.decode_v2(secplus.encode_v2(rolling, fixed))

            self.assertEqual(rolling, rolling_out)
            self.assertEqual(fixed, fixed_out)


if __name__ == '__main__':
    unittest.main()
