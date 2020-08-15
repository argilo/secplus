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

from __future__ import print_function
import numpy as np
from gnuradio import gr
import secplus


class blk(gr.sync_block):
    """Decoder for Chamberlain garage door openers"""

    def __init__(self, samp_rate=10000, threshold=0.02):
        gr.sync_block.__init__(
            self,
            name='Security+ 2.0 Decoder',

            in_sig=[np.float32],
            out_sig=[]
        )
        self.samp_rate = samp_rate
        self.threshold = threshold
        self.last_sample = 0.0
        self.last_edge = 0
        self.buffer = []
        self.last_pair = []
        self.pair = []

    def work(self, input_items, output_items):
        for n, sample in enumerate(input_items[0]):
            current_sample = self.nitems_read(0) + n
            if self.last_sample < self.threshold <= sample:
                # rising edge
                self.process_edge(True, current_sample - self.last_edge)
                self.last_edge = current_sample
            elif self.last_sample >= self.threshold > sample:
                # falling edge
                self.process_edge(False, current_sample - self.last_edge)
                self.last_edge = current_sample
            if current_sample - self.last_edge >= 0.625e-3 * self.samp_rate:
                self.buffer.append(0)
                self.buffer.append(0)
                self.process_buffer()
                self.buffer = []
            self.last_sample = sample
        return len(input_items[0])

    def process_edge(self, rising, samples):
        if samples < 0.125e-3 * self.samp_rate:
            self.buffer = []
        elif samples < 0.375e-3 * self.samp_rate:
            self.buffer.append(0 if rising else 1)
        elif samples < 0.625e-3 * self.samp_rate:
            self.buffer.append(0 if rising else 1)
            self.buffer.append(0 if rising else 1)
        else:
            self.buffer = []

    def process_buffer(self):
        manchester = "".join(str(b) for b in self.buffer)
        start = manchester.find("1010101010101010101010101010101001010101")
        if start == -1:
            return
        manchester = manchester[start:start+124]
        baseband = []
        for i in range(0, len(manchester), 2):
            if manchester[i:i+2] == "01":
                baseband.append(1)
            elif manchester[i:i+2] == "10":
                baseband.append(0)
            else:
                return
    
        if baseband[21] == 0:
            self.pair = baseband[22:]
        elif baseband[21] == 1 and len(self.pair) == 40:
            self.pair += baseband[22:]

        if len(self.pair) == 80 and self.pair != self.last_pair:
            rolling, fixed = secplus.decode_v2(self.pair)
            print(secplus.pretty_v2(rolling, fixed))
            self.last_pair = self.pair
