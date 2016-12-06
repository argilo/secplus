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

import numpy as np
from gnuradio import gr
import secplus


class blk(gr.sync_block):
    """Decoder for Chamberlain garage door openers"""

    def __init__(self, samp_rate=10000, threshold=0.02):
        gr.sync_block.__init__(
            self,
            name='Security+ Decoder',

            in_sig=[np.float32],
            out_sig=[]
        )
        self.samp_rate = samp_rate
        self.threshold = threshold
        self.last_sample = 0.0
        self.last_rise = 0
        self.buffer = []
        self.last_pair = []
        self.pair = []

    def work(self, input_items, output_items):
        for n, sample in enumerate(input_items[0]):
            current_sample = self.nitems_read(0) + n
            if self.last_sample < self.threshold <= sample:
                # rising edge
                self.last_rise = current_sample
            elif self.last_sample >= self.threshold > sample:
                # falling edge
                on_samples = current_sample - self.last_rise
                self.process_symbol(on_samples)
            if current_sample - self.last_rise > 3.25e-3 * self.samp_rate:
                self.buffer = []
            self.last_sample = sample
        return len(input_items[0])

    def process_symbol(self, on_samples):
        if on_samples < 0.35e-3 * self.samp_rate:
            self.buffer = []
        elif on_samples < 0.75e-3 * self.samp_rate:
            self.buffer.append(0)
        elif on_samples < 1.25e-3 * self.samp_rate:
            self.buffer.append(1)
        elif on_samples < 1.75e-3 * self.samp_rate:
            self.buffer.append(2)
        else:
            self.buffer = []

        if len(self.buffer) == 21:
            self.process_buffer()
            self.buffer = []

    def process_buffer(self):
        if self.buffer[0] == 0:
            self.pair = self.buffer[1:21]
        elif len(self.pair) == 20 and self.buffer[0] == 2:
            self.pair += self.buffer[1:21]

        if len(self.pair) == 40 and self.pair != self.last_pair:
            rolling, fixed = secplus.decode(self.pair)
            print secplus.pretty(rolling, fixed)
            self.last_pair = self.pair
