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
        self.pair = [None, None]
        self.pair_time = [None, None]

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
                self.process_buffer(current_sample)
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

    def process_buffer(self, current_sample):
        manchester = "".join(str(b) for b in self.buffer)
        start = manchester.find("1010101010101010101010101010101001010101")
        if start == -1:
            return

        if manchester[start+44:start+48] == "1010":
            packet_length = 40
        elif manchester[start+44:start+48] == "1001":
            packet_length = 64
        else:
            return

        manchester = manchester[start:start+44+(packet_length*2)]
        baseband = []
        for i in range(0, len(manchester), 2):
            if manchester[i:i+2] == "01":
                baseband.append(1)
            elif manchester[i:i+2] == "10":
                baseband.append(0)
            else:
                return
        packet = baseband[22:]

        if baseband[20:22] == [0, 0]:
            frame_id = 0
        elif baseband[20:22] == [0, 1]:
            frame_id = 1
        else:
            return

        self.pair_time[frame_id] = current_sample

        if self.pair[frame_id] == packet:
            return

        self.pair[frame_id] = packet
        
        if (self.pair[frame_id ^ 1] is not None) and (len(self.pair[frame_id ^ 1]) == packet_length):
            if self.pair_time[frame_id] - self.pair_time[frame_id ^ 1] < 0.35 * self.samp_rate:
                try:
                    rolling, fixed, data = secplus.decode_v2(self.pair[0] + self.pair[1])
                    print(secplus.pretty_v2(rolling, fixed, data))
                except ValueError:
                    pass
