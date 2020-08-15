#
# Copyright 2016,2020 Clayton Smith (argilo@gmail.com)
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

"""This module encodes and decodes Security+ and Security+ 2.0 rolling and fixed
codes, provides utility functions to prepare on-off keying sequences for
transmission, and pretty-prints the codes. It can be used to build stand-alone
applications.
"""

from __future__ import division

_OOK = {
    -1: [0, 0, 0, 0],
    0: [0, 0, 0, 1],
    1: [0, 0, 1, 1],
    2: [0, 1, 1, 1]
}

_ORDER = {
    0b0000: (0, 2, 1),
    0b0001: (2, 0, 1),
    0b0010: (0, 1, 2),
    0b0100: (1, 2, 0),
    0b0101: (1, 0, 2),
    0b0110: (2, 1, 0),
    0b1000: (1, 2, 0),
    0b1001: (2, 1, 0),
    0b1010: (0, 1, 2),
}

_INVERT = {
    0b0000: (True, True, False),
    0b0001: (False, True, False),
    0b0010: (False, False, True),
    0b0100: (True, True, True),
    0b0101: (True, False, True),
    0b0110: (False, True, True),
    0b1000: (True, False, False),
    0b1001: (False, False, False),
    0b1010: (True, False, True),
}


def decode(code):
    """Decode a Security+ transmission and return the rolling and fixed codes.

    Arguments:
    code -- a list containing the 40 payload symbols from a pair of packets
    """

    rolling = 0
    fixed = 0

    for i in range(0, 40, 2):
        if i in [0, 20]:
            acc = 0

        digit = code[i]
        rolling = (rolling * 3) + digit
        acc += digit

        digit = (code[i+1] - acc) % 3
        fixed = (fixed * 3) + digit
        acc += digit

    rolling = int("{0:032b}".format(rolling)[::-1], 2)
    fixed = int("{0:032b}".format(fixed), 2)
    return rolling, fixed


def _decode_v2_half(code):
    if code[:2] != [0, 0]:
        raise ValueError("First two bits of packet were not zero")

    try:
        order = _ORDER[(code[2] << 3) | (code[3] << 2) | (code[4] << 1) | code[5]]
        invert = _INVERT[(code[6] << 3) | (code[7] << 2) | (code[8] << 1) | code[9]]
    except KeyError:
        raise ValueError("Illegal value for ternary bit")

    parts_permuted = [code[10::3], code[11::3], code[12::3]]
    for i in range(3):
        if invert[i]:
            parts_permuted[i] = [bit ^ 1 for bit in parts_permuted[i]]

    parts = [[], [], []]
    for i in range(3):
        parts[order[i]] = parts_permuted[i]

    rolling = []
    for i in range(2, 10, 2):
        rolling.append((code[i] << 1) | code[i+1])
    for i in range(0, 10, 2):
        rolling.append((parts[2][i] << 1) | parts[2][i+1])
    if 3 in rolling:
        raise ValueError("Illegal value for ternary bit")

    fixed = parts[0] + parts[1]

    return rolling, fixed


def decode_v2(code):
    """Decode a Security+ 2.0 transmission and return the rolling and fixed codes.

    Arguments:
    code -- a list containing the 80 payload bits from a pair of packets
    """
    rolling1, fixed1 = _decode_v2_half(code[:40])
    rolling2, fixed2 = _decode_v2_half(code[40:])

    rolling_digits = rolling2[8:] + rolling1[8:]
    rolling_digits += rolling2[4:8] + rolling1[4:8]
    rolling_digits += rolling2[:4] + rolling1[:4]

    rolling = 0
    for digit in rolling_digits:
        rolling = (rolling * 3) + digit
    if rolling >= 2**28:
        raise ValueError("Rolling code was not in expected range")
    rolling = int("{0:028b}".format(rolling)[::-1], 2)

    fixed = int("".join(str(bit) for bit in fixed1 + fixed2), 2)
    return rolling, fixed


def encode(rolling, fixed):
    """Encode a Security+ payload into 40 payload symbols

    Arguments:
    rolling -- the rolling code
    fixed -- the fixed code
    """

    rolling = int("{0:032b}".format(rolling & 0xfffffffe)[::-1], 2)
    rolling_base3 = [0] * 20
    fixed_base3 = [0] * 20
    for i in range(19, -1, -1):
        rolling_base3[i] = rolling % 3
        rolling //= 3
        fixed_base3[i] = fixed % 3
        fixed //= 3
    code = []
    for i in range(20):
        if i in [0, 10]:
            acc = 0
        acc += rolling_base3[i]
        code.append(rolling_base3[i])
        acc += fixed_base3[i]
        code.append(acc % 3)
    return code


def encode_ook(rolling, fixed, fast=True):
    """Encode a Security+ payload and produce an OOK stream for transmission

    Arguments:
    rolling -- the rolling code
    fixed -- the fixed code
    fast -- when True, shortens the time between packets
    """

    code = encode(rolling, fixed)
    blank = [-1] * (10 if fast else 29)
    code = [0] + code[0:20] + blank + [2] + code[20:40] + blank
    ook_bits = []
    for symbol in code:
        ook_bits += _OOK[symbol]
    return ook_bits


def _encode_v2_half(rolling, fixed):
    code = [0, 0]
    parts = [fixed[:10], fixed[10:], []]

    for digit in rolling[:4]:
        code.append(digit >> 1)
        code.append(digit & 1)
    for digit in rolling[4:]:
        parts[2].append(digit >> 1)
        parts[2].append(digit & 1)

    order = _ORDER[(code[2] << 3) | (code[3] << 2) | (code[4] << 1) | code[5]]
    invert = _INVERT[(code[6] << 3) | (code[7] << 2) | (code[8] << 1) | code[9]]

    parts_permuted = [parts[order[i]] for i in range(3)]

    for i in range(3):
        if invert[i]:
            parts_permuted[i] = [bit ^ 1 for bit in parts_permuted[i]]

    for i in range(10):
        code += [parts_permuted[0][i], parts_permuted[1][i], parts_permuted[2][i]]

    return code


def encode_v2(rolling, fixed):
    """Encode a Security+ 2.0 payload into 80 payload bits

    Arguments:
    rolling -- the rolling code
    fixed -- the fixed code
    """

    rolling = int("{0:028b}".format(rolling)[::-1], 2)
    rolling_base3 = [0] * 18
    for i in range(17, -1, -1):
        rolling_base3[i] = rolling % 3
        rolling //= 3
    rolling1 = rolling_base3[14:18] + rolling_base3[6:10] + rolling_base3[1:2]
    rolling2 = rolling_base3[10:14] + rolling_base3[2:6] + rolling_base3[0:1]

    fixed_bits = [int(bit) for bit in "{0:040b}".format(fixed)]
    fixed1 = fixed_bits[:20]
    fixed2 = fixed_bits[20:]

    return _encode_v2_half(rolling1, fixed1) + _encode_v2_half(rolling2, fixed2)


def _manchester(code):
    output = []
    for bit in code:
        if bit == 0:
            output += [1, 0]
        else:
            output += [0, 1]
    return output


def encode_v2_manchester(rolling, fixed):
    """Encode a Security+ 2.0 payload and produce a Manchester stream for transmission

    Arguments:
    rolling -- the rolling code
    fixed -- the fixed code
    """

    preamble = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0]
    code = encode_v2(rolling, fixed)
    packet1 = preamble + [0] + code[:40]
    packet2 = preamble + [1] + code[40:]
    blank = [0] * 33

    return _manchester(packet1) + blank + _manchester(packet2) + blank


def pretty(rolling, fixed):
    """Pretty-print a Security+ rolling and fixed code"""
    return "Security+:  rolling={0}  fixed={1}  ({2})".format(rolling, fixed, _fixed_pretty(fixed))


def _fixed_pretty(fixed):
    switch_id = fixed % 3
    id0 = (fixed // 3) % 3
    id1 = (fixed // 3**2) % 3

    result = "id1={0} id0={1} switch={2}".format(id1, id0, switch_id)

    if id1 == 0:
        pad_id = (fixed // 3**3) % (3**7)
        result += " pad_id={0}".format(pad_id)
        pin = (fixed // 3**10) % (3**9)
        if 0 <= pin <= 9999:
            result += " pin={0:04}".format(pin)
        elif 10000 <= pin <= 11029:
            result += " pin=enter"
        pin_suffix = (fixed // 3**19) % 3
        if pin_suffix == 1:
            result += "#"
        elif pin_suffix == 2:
            result += "*"
    else:
        remote_id = (fixed // 3**3)
        result += " remote_id={0}".format(remote_id)
        if switch_id == 1:
            button = "left"
        elif switch_id == 0:
            button = "middle"
        elif switch_id == 2:
            button = "right"
        result += " button={0}".format(button)

    return result


def pretty_v2(rolling, fixed):
    """Pretty-print a Security+ 2.0 rolling and fixed code"""
    return "Security+ 2.0:  rolling={0}  fixed={1}  ({2})".format(rolling, fixed, _fixed_pretty_v2(fixed))


def _fixed_pretty_v2(fixed):
    return "button={0} remote_id={1}".format(fixed >> 32, fixed & 0xffffffff)
