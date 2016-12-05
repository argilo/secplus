#
# Copyright 2016 Clayton Smith (argilo@gmail.com)
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

from __future__ import division

def decode(code):
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

def encode(counter, fixed):
    counter = int("{0:032b}".format(counter & 0xfffffffe)[::-1], 2)
    counter_base3 = [0] * 20
    fixed_base3 = [0] * 20
    for i in range(19, -1, -1):
        counter_base3[i] = counter % 3
        counter //= 3
        fixed_base3[i] = fixed % 3
        fixed //= 3
    code = []
    for i in range(20):
        if i in [0, 10]:
            acc = 0
        acc += counter_base3[i]
        code.append(counter_base3[i])
        acc += fixed_base3[i]
        code.append(acc % 3)
    return code

def ook(counter, fixed, fast=True):
    OOK = { -1: [0,0,0,0], 0: [0,0,0,1], 1: [0,0,1,1], 2: [0,1,1,1] }
    code = encode(counter, fixed)
    blank = [-1] * (10 if fast else 29)
    code = [0] + code[0:20] + blank + [2] + code[20:40] + blank
    ook_bits = []
    for symbol in code:
        ook_bits += OOK[symbol]
    return ook_bits

def pretty(rolling, fixed):
    return "rolling={0}  fixed={1}  ({2})".format(rolling, fixed, fixed_pretty(fixed))

def fixed_pretty(fixed):
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
    elif id1 == 2:
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
