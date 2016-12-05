```
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
```

secplus
=======

This project is a software implementation of the Security+ rolling code system used in garage door openers made by Chamberlain, LiftMaster, Craftsman and others. Much of the system is described in US patent 6,980,655; the remaining details were determined by analyzing the data transmitted by Security+ remotes.

Transmissions use on-off keying, with an alphabet of three symbols (0, 1, 2) corresponding to three different pulse widths:
* 0: 1.5ms off, 0.5ms on
* 1: 1ms off, 1ms on
* 2: 0.5ms off, 1.5ms on

The payload consists of 40 symbols, which are transmited in two frames of 20 symbols each. A single synchronization symbol is prepended to each frame: 0 for the first frame, and 2 for the second. 58ms of silence occurs after each frame, but the receiver I tested with accepts as little as 20ms. Remotes repeat the frame pair a minimum of four times, or continuously for as long as the button is held down.

The payload consists of a rolling code and a fixed code, each appoximately 32 bits long. These values are combined and encoded into 40 ternary symbols for transmission. Despite being described as such in patents, the encoding is not encryption as there is no key.

The rolling code is incremented by three each time the remote button is pressed, and the fixed code remains the same. PIN pads use half of the fixed code symbols to transmit the four-digit PIN that was entered. Receivers accept codes so long as the fixed code corresponds to a programmed remote, and the current rolling code is less than 3072 above the last rolling code. Receivers will also accept any two consecutive rolling codes (and adjust the stored rolling code accordingly) so long as the two codes are not within 1024 below the last rolling code.

secplus.py
----------

This Python module encodes and decodes the rolling and fixed codes, and provides utility functions to prepare an on-off keying sequence for transmission, and pretty-print the codes.

secplus_rx.grc, secplus_rx.py
-----------------------------

This GNU Radio flow graph receives Security+ transmissions on 315.15 MHz and pretty-prints them. It has been tested on an RTL-SDR and a HackRF.

secplus_tx.grc, secplus_tx.py
-----------------------------

This GNU Radio flow graph encodes and transmits Security+ frames. It has been tested on a HackRF.
