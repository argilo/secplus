#
# Copyright 2016,2020-2024 Clayton Smith (argilo@gmail.com)
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


def _reverse_int(n, bits):
    result = 0
    for _ in range(bits):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result


def encode(rolling, fixed):
    """Encode a Security+ payload into 40 payload symbols

    Arguments:
    rolling -- the rolling code
    fixed -- the fixed code

    Raises a ValueError if the rolling or fixed code is too large.
    """

    if rolling >= 2**32:
        raise ValueError("Rolling code must be less than 2^32")
    if fixed >= 3**20:
        raise ValueError("Fixed code must be less than 3^20")

    rolling = _reverse_int(rolling & 0xfffffffe, 32)
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

    rolling = _reverse_int(rolling, 32)
    return rolling, fixed


def _v2_calc_parity(fixed, data):
    data &= 0xffff0fff
    parity = (fixed >> 32) & 0xf
    for offset in range(0, 32, 4):
        parity ^= ((data >> offset) & 0xf)
    data |= (parity << 12)
    return data


def _v2_check_parity(fixed, data):
    parity = (fixed >> 32) & 0xf
    for offset in range(0, 32, 4):
        parity ^= ((data >> offset) & 0xf)
    if parity != 0:
        raise ValueError("Parity bits are incorrect")


def _encode_v2_rolling(rolling):
    rolling = _reverse_int(rolling, 28)
    rolling_base3 = [0] * 18
    for i in range(17, -1, -1):
        rolling_base3[i] = rolling % 3
        rolling //= 3
    rolling1 = rolling_base3[14:18] + rolling_base3[6:10] + rolling_base3[1:2]
    rolling2 = rolling_base3[10:14] + rolling_base3[2:6] + rolling_base3[0:1]
    return rolling1, rolling2


def _decode_v2_rolling(rolling1, rolling2):
    rolling_digits = rolling2[8:] + rolling1[8:]
    rolling_digits += rolling2[4:8] + rolling1[4:8]
    rolling_digits += rolling2[:4] + rolling1[:4]

    rolling = 0
    for digit in rolling_digits:
        rolling = (rolling * 3) + digit
    if rolling >= 2**28:
        raise ValueError("Rolling code was not in expected range")
    return _reverse_int(rolling, 28)


def _v2_combine_halves(rolling1, rolling2, fixed1, fixed2, data1, data2):
    rolling = _decode_v2_rolling(rolling1, rolling2)
    fixed = int("".join(str(bit) for bit in fixed1 + fixed2), 2)
    if data1 is None:
        data = None
    else:
        data = int("".join(str(bit) for bit in data1 + data2), 2)
        _v2_check_parity(fixed, data)
    return rolling, fixed, data


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


def _v2_scramble(indicator, parts):
    order = _ORDER[(indicator[0] << 3) | (indicator[1] << 2) | (indicator[2] << 1) | indicator[3]]
    invert = _INVERT[(indicator[4] << 3) | (indicator[5] << 2) | (indicator[6] << 1) | indicator[7]]

    parts_permuted = [parts[order[i]] for i in range(3)]
    for i in range(3):
        if invert[i]:
            parts_permuted[i] = [bit ^ 1 for bit in parts_permuted[i]]

    payload = []
    for i in range(len(parts_permuted[0])):
        payload += [parts_permuted[0][i], parts_permuted[1][i], parts_permuted[2][i]]
    return payload


def _v2_unscramble(indicator, payload):
    try:
        order = _ORDER[(indicator[0] << 3) | (indicator[1] << 2) | (indicator[2] << 1) | indicator[3]]
        invert = _INVERT[(indicator[4] << 3) | (indicator[5] << 2) | (indicator[6] << 1) | indicator[7]]
    except KeyError:
        raise ValueError("Illegal value for ternary bit")

    parts_permuted = [payload[0::3], payload[1::3], payload[2::3]]
    for i in range(3):
        if invert[i]:
            parts_permuted[i] = [bit ^ 1 for bit in parts_permuted[i]]

    parts = [[], [], []]
    for i in range(3):
        parts[order[i]] = parts_permuted[i]

    return parts


def _encode_v2_half_parts(rolling, fixed, data):
    indicator = []
    for digit in rolling[:4]:
        indicator.append(digit >> 1)
        indicator.append(digit & 1)

    parts = [fixed[:10], fixed[10:], []]
    for digit in rolling[4:]:
        parts[2].append(digit >> 1)
        parts[2].append(digit & 1)

    if data is None:
        packet_type = 0
    if data is not None:
        packet_type = 1
        parts[0] += data[:8]
        parts[1] += data[8:]
        for digit in rolling[:4]:
            parts[2].append(digit >> 1)
            parts[2].append(digit & 1)

    payload = _v2_scramble(indicator, parts)

    return packet_type, indicator, payload


def _decode_v2_half_parts(packet_type, indicator, payload):
    if packet_type == 0:
        payload_length = 30
    elif packet_type == 1:
        payload_length = 54
    elif packet_type == 2:
        raise ValueError("Unsupported packet type")
    else:
        raise ValueError("Invalid packet type")

    if len(payload) != payload_length:
        raise ValueError("Incorrect payload length")

    parts = _v2_unscramble(indicator, payload)

    rolling = []
    for i in range(0, len(indicator), 2):
        rolling.append((indicator[i] << 1) | indicator[i+1])
    for i in range(0, len(parts[2]), 2):
        rolling.append((parts[2][i] << 1) | parts[2][i+1])
    if 3 in rolling:
        raise ValueError("Illegal value for ternary bit")

    fixed = parts[0][:10] + parts[1][:10]

    if packet_type == 0:
        data = None
    elif packet_type == 1:
        if rolling[:4] != rolling[-4:]:
            raise ValueError("Last four ternary bits do not repeat first four")
        rolling = rolling[:-4]
        data = parts[0][10:] + parts[1][10:]

    return rolling, fixed, data


def _v2_check_limits(rolling, fixed, data):
    if rolling >= 2**28:
        raise ValueError("Rolling code must be less than 2^28")
    if fixed >= 2**40:
        raise ValueError("Fixed code must be less than 2^40")
    if data is not None:
        if data >= 2**32:
            raise ValueError("Data must be less than 2^32")


def _encode_v2_half(rolling, fixed, data):
    packet_type, indicator, payload = _encode_v2_half_parts(rolling, fixed, data)
    packet_type_bits = [packet_type >> 1, packet_type & 1]
    return packet_type_bits + indicator + payload


def encode_v2(rolling, fixed, data=None):
    """Encode a Security+ 2.0 payload into 80 or 128 bits

    Arguments:
    rolling -- the rolling code (28 bits)
    fixed -- the fixed code (40 bits)
    data -- the data (32 bits, optional)

    Raises a ValueError if the rolling or fixed code is too large.
    """

    _v2_check_limits(rolling, fixed, data)

    rolling1, rolling2 = _encode_v2_rolling(rolling)

    fixed_bits = [int(bit) for bit in f"{fixed:040b}"]
    fixed1 = fixed_bits[:20]
    fixed2 = fixed_bits[20:]

    if data is None:
        data1 = None
        data2 = None
    else:
        data = _v2_calc_parity(fixed, data)
        data_bits = [int(bit) for bit in f"{data:032b}"]
        data1 = data_bits[:16]
        data2 = data_bits[16:]

    return _encode_v2_half(rolling1, fixed1, data1) + _encode_v2_half(rolling2, fixed2, data2)


def _decode_v2_half(code):
    packet_type = (code[0] << 1) | code[1]
    indicator = code[2:10]
    payload = code[10:]
    return _decode_v2_half_parts(packet_type, indicator, payload)


def decode_v2(code):
    """Decode a Security+ 2.0 transmission and return the rolling code, fixed
    code, and data.

    Arguments:
    code -- a list containing the 80 or 128 payload bits from a pair of packets

    Raises a ValueError if the payload bits are invalid for any reason.
    """
    half_len = len(code) // 2
    rolling1, fixed1, data1 = _decode_v2_half(code[:half_len])
    rolling2, fixed2, data2 = _decode_v2_half(code[half_len:])
    return _v2_combine_halves(rolling1, rolling2, fixed1, fixed2, data1, data2)


def _encode_wireline_half(rolling, fixed, data):
    _, indicator, payload = _encode_v2_half_parts(rolling, fixed, data)
    return indicator + [0, 0] + payload


def encode_wireline(rolling, fixed, data):
    """Encode a Security+ 2.0 wireline payload into 19 bytes

    Arguments:
    rolling -- the rolling code (28 bits)
    fixed -- the fixed code (40 bits)
    data -- the data (32 bits)

    Raises a ValueError if the rolling code, fixed code, or data is too large.
    """

    _v2_check_limits(rolling, fixed, data)

    rolling1, rolling2 = _encode_v2_rolling(rolling)

    fixed_bits = [int(bit) for bit in f"{fixed:040b}"]
    fixed1 = fixed_bits[:20]
    fixed2 = fixed_bits[20:]

    data = _v2_calc_parity(fixed, data)
    data_bits = [int(bit) for bit in f"{data:032b}"]
    data1 = data_bits[:16]
    data2 = data_bits[16:]

    payload_bits = _encode_wireline_half(rolling1, fixed1, data1) + _encode_wireline_half(rolling2, fixed2, data2)
    packet = [0x55, 0x01, 0x00]
    for n in range(len(payload_bits) // 8):
        byte = 0
        for bit in range(8):
            byte |= payload_bits[n * 8 + bit] << (7 - bit)
        packet.append(byte)
    return bytes(packet)


def encode_wireline_command(rolling, device_id, command, payload):
    """Encode a Security+ 2.0 wireline payload into 19 bytes

    Arguments:
    rolling -- the rolling code (28 bits)
    device_id -- the device ID (40 bits)
    command -- the command number (12 bits)
    payload -- the payload value (20 bits)

    Raises a ValueError if the rolling code, fixed code, or data is too large.
    """

    if command >= 2**12:
        raise ValueError("Command must be less than 2^12")
    if payload >= 2**20:
        raise ValueError("Payload value must be less than 2^20")

    fixed = (device_id & 0xf0ffffffff) | ((command & 0xf00) << 24)
    data = ((payload & 0xff) << 24) | ((payload & 0xff00) << 8) | ((payload & 0xf0000) >> 8) | (command & 0xff)

    return encode_wireline(rolling, fixed, data)


def _decode_wireline_half(code):
    if code[8:10] != [0, 0]:
        raise ValueError("Unexpected values for bits 8 and 9")
    indicator = code[:8]
    payload = code[10:]
    return _decode_v2_half_parts(1, indicator, payload)


def decode_wireline(code):
    """Decode a Security+ 2.0 wireline transmission and return the rolling code,
    fixed code, and data.

    Arguments:
    code -- a bytes object with the 19 bytes of a serial packet

    Raises a ValueError if the payload bytes are invalid for any reason.
    """
    if not isinstance(code, bytes):
        raise ValueError("Input must be bytes")
    if len(code) != 19:
        raise ValueError("Input must be 19 bytes long")
    if code[:3] != bytes([0x55, 0x01, 0x00]):
        raise ValueError("First three bytes must be 0x55, 0x01, 0x00")

    code_bits = []
    for b in code[3:]:
        for bit in range(7, -1, -1):
            code_bits.append((b >> bit) & 1)

    half_len = len(code_bits) // 2
    rolling1, fixed1, data1 = _decode_wireline_half(code_bits[:half_len])
    rolling2, fixed2, data2 = _decode_wireline_half(code_bits[half_len:])
    return _v2_combine_halves(rolling1, rolling2, fixed1, fixed2, data1, data2)


def decode_wireline_command(code):
    """Decode a Security+ 2.0 wireline transmission and return the rolling code,
    device ID, command number, and payload value

    Arguments:
    code -- a bytes object with the 19 bytes of a serial packet

    Raises a ValueError if the payload bytes are invalid for any reason.
    """
    rolling, fixed, data = decode_wireline(code)
    device_id = fixed & 0xf0ffffffff
    command = ((fixed >> 24) & 0xf00) | (data & 0xff)
    payload = ((data << 8) & 0xf0000) | ((data >> 8) & 0xff00) | (data >> 24)
    return rolling, device_id, command, payload


_OOK = {
    -1: [0, 0, 0, 0],
    0: [0, 0, 0, 1],
    1: [0, 0, 1, 1],
    2: [0, 1, 1, 1]
}


def encode_ook(rolling, fixed, fast=True):
    """Encode a Security+ payload and produce an OOK stream for transmission

    The resulting pulses should be transmitted at a baud rate of 2000. That is,
    each 0 (off) or 1 (on) should be 0.5 ms long.

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


def _manchester(code):
    output = []
    for bit in code:
        if bit == 0:
            output += [1, 0]
        else:
            output += [0, 1]
    return output


def encode_v2_manchester(rolling, fixed, data=None, fast=True):
    """Encode a Security+ 2.0 payload and produce a Manchester stream for transmission

    The resulting pulses should be transmitted at a baud rate of 4000. That is,
    each 0 (off) or 1 (on) should be 0.25 ms long.

    Arguments:
    rolling -- the rolling code (28 bits)
    fixed -- the fixed code (40 bits)
    data -- the data (32 bits, optional)
    fast -- when True, shortens the time between packets
    """

    preamble = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
    code = encode_v2(rolling, fixed, data)
    half_len = len(code) // 2
    packet1 = preamble + [0, 0] + code[:half_len]
    packet2 = preamble + [0, 1] + code[half_len:]
    blank = [0] * (33 if fast else 400 - 2 * len(packet1))

    return _manchester(packet1) + blank + _manchester(packet2) + blank


def pretty(rolling, fixed):
    """Pretty-print a Security+ rolling and fixed code"""
    return f"Security+:  rolling={rolling}  fixed={fixed}  ({_fixed_pretty(fixed)})"


def _fixed_pretty(fixed):
    switch_id = fixed % 3
    id0 = (fixed // 3) % 3
    id1 = (fixed // 3**2) % 3

    result = f"id1={id1} id0={id0} switch={switch_id}"

    if id1 == 0:
        pad_id = (fixed // 3**3) % (3**7)
        result += f" pad_id={pad_id}"
        pin = (fixed // 3**10) % (3**9)
        if 0 <= pin <= 9999:
            result += f" pin={pin:04}"
        elif 10000 <= pin <= 11029:
            result += " pin=enter"
        pin_suffix = (fixed // 3**19) % 3
        if pin_suffix == 1:
            result += "#"
        elif pin_suffix == 2:
            result += "*"
    else:
        remote_id = (fixed // 3**3)
        result += f" remote_id={remote_id}"
        if switch_id == 0:
            button = "middle"
        elif switch_id == 1:
            button = "left"
        else:
            button = "right"
        result += f" button={button}"

    return result


def pretty_v2(rolling, fixed, data=None):
    """Pretty-print a Security+ 2.0 rolling code, fixed code, and data"""
    pretty = f"Security+ 2.0:  rolling=0x{rolling:07x}  fixed=0x{fixed:010x}  ({_fixed_pretty_v2(fixed)})"
    if data is not None:
        pretty += f"  data=0x{data:08x}  ({_data_pretty_v2(fixed, data)})"
    return pretty


def _fixed_pretty_v2(fixed):
    button = (fixed >> 32) & 0xf
    remote_id = fixed & 0xf0ffffffff
    return f"button={button} remote_id=0x{remote_id:010x}"


def _data_pretty_v2(fixed, data):
    button = (fixed >> 32) & 0xf

    byte1 = data >> 24
    byte2 = (data >> 16) & 0xff
    pin = (byte2 << 8) | byte1

    tail = data & 0xfff

    if button == 3:
        return f"pin=enter tail=0x{tail:03x}"
    else:
        if button == 1:
            suffix = "*"
        elif button == 2:
            suffix = "#"
        else:
            suffix = ""

        return f"pin={pin:04}{suffix} tail=0x{tail:03x}"


_WIRELINE_COMMANDS = {
    # sent by opener
    0x081: "status",
    0x084: "unknown_1",
    0x085: "unknown_2",
    0x0a1: "pair_3_resp",
    0x284: "motor_on",
    0x393: "learn_3_resp",
    0x401: "pair_2_resp",
    0x48c: "openings",

    # sent by switch
    0x080: "get_status",
    0x0a0: "pair_3",
    0x181: "learn_2",
    0x18c: "lock",
    0x280: "open",
    0x281: "light",
    0x285: "motion",
    0x391: "learn_1",
    0x392: "learn_3",
    0x400: "pair_2",
    0x48b: "get_openings",
}

_DOOR_STATUS = {
    1: "open",
    2: "closed",
    3: "stopped",
    4: "opening",
    5: "closing",
}


def pretty_wireline(rolling, device_id, command, payload):
    command_name = _WIRELINE_COMMANDS.get(command, "<unknown>")

    msg = ""
    if command == 0x081:
        door = _DOOR_STATUS.get(payload >> 16, "<unknown>")
        learn = (payload >> 5) & 1
        unk1 = (payload >> 4) & 1
        unk2 = (payload >> 2) & 1
        light = (payload >> 1) & 1
        lock = payload & 1
        blocked = (payload >> 14) & 1
        unk3 = (payload >> 13) & 1
        msg = f"door={door} learn={learn} light={light} lock={lock} blocked={blocked^1} unk1={unk1} unk2={unk2} unk3={unk3}"
    elif command == 0x280:
        msg = "pressed" if ((payload >> 8) & 1) else "released"
    elif command == 0x48c:
        openings = payload & 0xffff
        msg = f"number={openings}"

    return f"rolling=0x{rolling:07x} device_id=0x{device_id:010x} command=0x{command:03x} payload=0x{payload:05x} {command_name} {msg}".strip()
