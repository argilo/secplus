#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Secplus Rx
# GNU Radio version: 3.10.11.0

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
import threading



class secplus_rx(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Secplus Rx", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Secplus Rx")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "secplus_rx")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.threshold = threshold = 0.10
        self.samp_rate = samp_rate = 2000000
        self.freq = freq = 315150000
        self.decim2 = decim2 = 50
        self.decim1 = decim1 = 2

        ##################################################
        # Blocks
        ##################################################

        self._threshold_range = qtgui.Range(0.01, 1.00, 0.01, 0.10, 200)
        self._threshold_win = qtgui.RangeWidget(self._threshold_range, self.set_threshold, "Detection threshold", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._threshold_win)
        # Create the options list
        self._freq_options = [310150000, 315150000, 390150000, 433920000]
        # Create the labels list
        self._freq_labels = ['310 MHz', '315 MHz', '390 MHz', '433 MHz']
        # Create the combo box
        # Create the radio buttons
        self._freq_group_box = Qt.QGroupBox("Frequency" + ": ")
        self._freq_box = Qt.QHBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._freq_button_group = variable_chooser_button_group()
        self._freq_group_box.setLayout(self._freq_box)
        for i, _label in enumerate(self._freq_labels):
            radio_button = Qt.QRadioButton(_label)
            self._freq_box.addWidget(radio_button)
            self._freq_button_group.addButton(radio_button, i)
        self._freq_callback = lambda i: Qt.QMetaObject.invokeMethod(self._freq_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._freq_options.index(i)))
        self._freq_callback(self.freq)
        self._freq_button_group.buttonClicked[int].connect(
            lambda i: self.set_freq(self._freq_options[i]))
        self.top_layout.addWidget(self._freq_group_box)
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
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            (100000 // decim1 // decim2), #size
            samp_rate // decim1 // decim2, #samp_rate
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(0, 2)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_AUTO, qtgui.TRIG_SLOPE_POS, threshold, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
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
        self.connect((self.blocks_complex_to_mag_0, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.blocks_rotator_cc_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.blocks_rotator_cc_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.secplus_decode, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.secplus_v2_decode, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "secplus_rx")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_AUTO, qtgui.TRIG_SLOPE_POS, self.threshold, 0, 0, "")
        self.secplus_decode.threshold = self.threshold
        self.secplus_v2_decode.threshold = self.threshold

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_rotator_cc_0.set_phase_inc((2 * math.pi * -300e3 / self.samp_rate))
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate // self.decim1 // self.decim2)
        self.secplus_decode.samp_rate = self.samp_rate // self.decim1 // self.decim2
        self.secplus_v2_decode.samp_rate = self.samp_rate // self.decim1 // self.decim2

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self._freq_callback(self.freq)
        self.osmosdr_source_0.set_center_freq((self.freq - 300e3), 0)

    def get_decim2(self):
        return self.decim2

    def set_decim2(self, decim2):
        self.decim2 = decim2
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate // self.decim1 // self.decim2)
        self.rational_resampler_xxx_1.set_taps([1.0/self.decim2]*self.decim2)
        self.secplus_decode.samp_rate = self.samp_rate // self.decim1 // self.decim2
        self.secplus_v2_decode.samp_rate = self.samp_rate // self.decim1 // self.decim2

    def get_decim1(self):
        return self.decim1

    def set_decim1(self, decim1):
        self.decim1 = decim1
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate // self.decim1 // self.decim2)
        self.secplus_decode.samp_rate = self.samp_rate // self.decim1 // self.decim2
        self.secplus_v2_decode.samp_rate = self.samp_rate // self.decim1 // self.decim2




def main(top_block_cls=secplus_rx, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
