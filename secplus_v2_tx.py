#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Secplus V2 Tx
# GNU Radio version: 3.10.5.0

from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import osmosdr
import time
import secplus




class secplus_v2_tx(gr.top_block):

    def __init__(self, data=(-1), fixed=1234567890, freq=315000000, rolling=123456789):
        gr.top_block.__init__(self, "Secplus V2 Tx", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.data = data
        self.fixed = fixed
        self.freq = freq
        self.rolling = rolling

        ##################################################
        # Variables
        ##################################################
        self.seq = seq = [0]*200 + secplus.encode_v2_manchester(rolling, fixed, None if data == -1 else data)*3 + [0]*200
        self.samp_rate = samp_rate = 2e6

        ##################################################
        # Blocks
        ##################################################
        self.single_pole_iir_filter_xx_0 = filter.single_pole_iir_filter_cc(0.2, 1)
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + ''
        )
        self.osmosdr_sink_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq((freq - 300e3), 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(0, 0)
        self.osmosdr_sink_0.set_if_gain(47, 0)
        self.osmosdr_sink_0.set_bb_gain(0, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(seq, False, 1, [])
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_gr_complex*1, 500)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 300e3, 0.9, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_multiply_xx_0, 0), (self.osmosdr_sink_0, 0))
        self.connect((self.blocks_repeat_0, 0), (self.single_pole_iir_filter_xx_0, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_repeat_0, 0))
        self.connect((self.single_pole_iir_filter_xx_0, 0), (self.blocks_multiply_xx_0, 0))


    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data
        self.set_seq([0]*200 + secplus.encode_v2_manchester(self.rolling, self.fixed, None if self.data == -1 else self.data)*3 + [0]*200)

    def get_fixed(self):
        return self.fixed

    def set_fixed(self, fixed):
        self.fixed = fixed
        self.set_seq([0]*200 + secplus.encode_v2_manchester(self.rolling, self.fixed, None if self.data == -1 else self.data)*3 + [0]*200)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_sink_0.set_center_freq((self.freq - 300e3), 0)

    def get_rolling(self):
        return self.rolling

    def set_rolling(self, rolling):
        self.rolling = rolling
        self.set_seq([0]*200 + secplus.encode_v2_manchester(self.rolling, self.fixed, None if self.data == -1 else self.data)*3 + [0]*200)

    def get_seq(self):
        return self.seq

    def set_seq(self, seq):
        self.seq = seq
        self.blocks_vector_source_x_0.set_data(self.seq, [])

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--data", dest="data", type=intx, default=(-1),
        help="Set Data [default=%(default)r]")
    parser.add_argument(
        "--fixed", dest="fixed", type=intx, default=1234567890,
        help="Set Fixed code [default=%(default)r]")
    parser.add_argument(
        "-f", "--freq", dest="freq", type=intx, default=315000000,
        help="Set Frequency [default=%(default)r]")
    parser.add_argument(
        "--rolling", dest="rolling", type=intx, default=123456789,
        help="Set Rolling code [default=%(default)r]")
    return parser


def main(top_block_cls=secplus_v2_tx, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(data=options.data, fixed=options.fixed, freq=options.freq, rolling=options.rolling)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()


if __name__ == '__main__':
    main()
