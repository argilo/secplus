#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Secplus Rx
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import math
import osmosdr
import time
import secplus_rx_secplus_decode as secplus_decode  # embedded python block
import secplus_rx_secplus_v2_decode as secplus_v2_decode  # embedded python block
import sip
import sys


class secplus_rx(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Secplus Rx", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.threshold = threshold = 0.10
        self.samp_rate = samp_rate = 2000000
        self.freq = freq = 390150000
        self.decim2 = decim2 = 50
        self.decim1 = decim1 = 2

        ##################################################
        # Blocks
        ##################################################
        self.secplus_v2_decode = secplus_v2_decode.blk(samp_rate=samp_rate // decim1 // decim2, threshold=threshold)
        self.secplus_decode = secplus_decode.blk(samp_rate=samp_rate // decim1 // decim2, threshold=threshold)
        self.rational_resampler_xxx_1 = filter.rational_resampler_fff(
                interpolation=1,
                decimation=decim2,
                taps=[1.0/decim2]*decim2,
                fractional_bw=0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=1,
                decimation=decim1,
                taps=[],
                fractional_bw=0)

        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ''
        )
        self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq((freq - 300e3), 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(30, 0)
        self.osmosdr_source_0.set_if_gain(32, 0)
        self.osmosdr_source_0.set_bb_gain(32, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(1e6, 0)
        self.blocks_rotator_cc_0 = blocks.rotator_cc((2 * math.pi * -300e3 / samp_rate), False)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.osmosdr_source_0, 0), (self.blocks_rotator_cc_0, 0))
        self.connect((self.blocks_rotator_cc_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.secplus_decode, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.secplus_v2_decode, 0))


def main(top_block_cls=secplus_rx, options=None):

    tb = top_block_cls()

    tb.start()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sys.exit(1)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    time.sleep(60)


if __name__ == '__main__':
    main()
