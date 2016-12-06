#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Secplus Tx
# Generated: Mon Dec  5 20:40:54 2016
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import osmosdr
import secplus
import time


class secplus_tx(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Secplus Tx")

        ##################################################
        # Variables
        ##################################################
        self.rolling = rolling = 1234567890
        self.fixed = fixed = 1234567890
        self.seq = seq = [0]*100 + secplus.ook(rolling, fixed, fast=False)*4 + [0]*100
        self.samp_rate = samp_rate = 2e6
        self.freq = freq = 315.15e6

        ##################################################
        # Blocks
        ##################################################
        self.single_pole_iir_filter_xx_0 = filter.single_pole_iir_filter_cc(0.1, 1)
        self.osmosdr_sink_0 = osmosdr.sink( args="numchan=" + str(1) + " " + '' )
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(freq - 300e3, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(0, 0)
        self.osmosdr_sink_0.set_if_gain(47, 0)
        self.osmosdr_sink_0.set_bb_gain(0, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
          
        self.blocks_vector_source_x_0 = blocks.vector_source_c(seq, False, 1, [])
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_gr_complex*1, 1000)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 300e3, 0.9, 0)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 0))    
        self.connect((self.blocks_multiply_xx_0, 0), (self.osmosdr_sink_0, 0))    
        self.connect((self.blocks_repeat_0, 0), (self.single_pole_iir_filter_xx_0, 0))    
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_repeat_0, 0))    
        self.connect((self.single_pole_iir_filter_xx_0, 0), (self.blocks_multiply_xx_0, 1))    

    def get_rolling(self):
        return self.rolling

    def set_rolling(self, rolling):
        self.rolling = rolling
        self.set_seq([0]*100 + secplus.ook(self.rolling, self.fixed, fast=False)*4 + [0]*100)

    def get_fixed(self):
        return self.fixed

    def set_fixed(self, fixed):
        self.fixed = fixed
        self.set_seq([0]*100 + secplus.ook(self.rolling, self.fixed, fast=False)*4 + [0]*100)

    def get_seq(self):
        return self.seq

    def set_seq(self, seq):
        self.seq = seq
        self.blocks_vector_source_x_0.set_data(self.seq, [])

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_sink_0.set_center_freq(self.freq - 300e3, 0)


def main(top_block_cls=secplus_tx, options=None):

    tb = top_block_cls()
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
