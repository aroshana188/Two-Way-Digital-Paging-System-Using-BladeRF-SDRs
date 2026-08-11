#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: pkt_8
# Author: Barry Duggan
# Description: packet transmit
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import blocks
from gnuradio import channels
from gnuradio.filter import firdes
from gnuradio import digital
from gnuradio import filter
from gnuradio import fec
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import gr, pdu
from gnuradio import zeromq
import pkt_8_epy_block_0 as epy_block_0  # embedded python block
import pkt_8_epy_block_0_1 as epy_block_0_1  # embedded python block
import pkt_8_epy_block_1 as epy_block_1  # embedded python block
import pkt_8_epy_block_10 as epy_block_10  # embedded python block
import pkt_8_epy_block_11 as epy_block_11  # embedded python block
import pkt_8_epy_block_11_1 as epy_block_11_1  # embedded python block
import pkt_8_epy_block_12 as epy_block_12  # embedded python block
import pkt_8_epy_block_12_0 as epy_block_12_0  # embedded python block
import pkt_8_epy_block_13 as epy_block_13  # embedded python block
import pkt_8_epy_block_1_0 as epy_block_1_0  # embedded python block
import pkt_8_epy_block_2 as epy_block_2  # embedded python block
import pkt_8_epy_block_2_2 as epy_block_2_2  # embedded python block
import pkt_8_epy_block_3 as epy_block_3  # embedded python block
import pkt_8_epy_block_3_0 as epy_block_3_0  # embedded python block
import pkt_8_epy_block_3_1 as epy_block_3_1  # embedded python block
import pkt_8_epy_block_4 as epy_block_4  # embedded python block
import pkt_8_epy_block_4_0 as epy_block_4_0  # embedded python block
import pkt_8_epy_block_5 as epy_block_5  # embedded python block
import pkt_8_epy_block_5_0 as epy_block_5_0  # embedded python block
import pkt_8_epy_block_6 as epy_block_6  # embedded python block
import pkt_8_epy_block_6_0 as epy_block_6_0  # embedded python block
import pkt_8_epy_block_7 as epy_block_7  # embedded python block
import pkt_8_epy_block_7_0 as epy_block_7_0  # embedded python block
import pkt_8_epy_block_7_1_0 as epy_block_7_1_0  # embedded python block
import pkt_8_epy_block_7_1_0_0 as epy_block_7_1_0_0  # embedded python block
import pkt_8_epy_block_8 as epy_block_8  # embedded python block
import pkt_8_epy_block_8_0 as epy_block_8_0  # embedded python block
import pkt_8_epy_block_9 as epy_block_9  # embedded python block
import pkt_8_epy_block_9_0 as epy_block_9_0  # embedded python block
import sip
import threading



class pkt_8(gr.top_block, Qt.QWidget):

    def __init__(self, MTU=1500):
        gr.top_block.__init__(self, "pkt_8", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("pkt_8")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "pkt_8")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Parameters
        ##################################################
        self.MTU = MTU

        ##################################################
        # Variables
        ##################################################
        self.sps = sps = 4
        self.qpsk = qpsk = digital.constellation_rect([0.707+0.707j, -0.707+0.707j, -0.707-0.707j, 0.707-0.707j], [0, 1, 2, 3],
        4, 2, 2, 1, 1).base()
        self.polys = polys = [109, 79]
        self.nfilts = nfilts = 32
        self.k = k = 7
        self.access_key = access_key = '11100001010110101110100010010011'
        self.variable_adaptive_algorithm_0 = variable_adaptive_algorithm_0 = digital.adaptive_algorithm_cma( qpsk, .0001, 4).base()
        self.tuning_offset = tuning_offset = -21e3
        self.time_offset = time_offset = 1.000
        self.thresh = thresh = 1
        self.sample_rate_blade = sample_rate_blade = 1.2e6
        self.samp_rate = samp_rate = 600e3
        self.rrc_taps = rrc_taps = firdes.root_raised_cosine(nfilts, nfilts, 1.0/float(sps), 0.35, 11*sps*nfilts)
        self.phase_bw = phase_bw = 6.28/100.0
        self.num_duplicates = num_duplicates = 8
        self.noise_volt = noise_volt = 00
        self.hdr_format = hdr_format = digital.header_format_default(access_key, 0)
        self.freq_offset = freq_offset = 0
        self.freq = freq = 2.4e9
        self.extra_bytes = extra_bytes = 3200
        self.excess_bw = excess_bw = 0.35
        self.delay = delay = 42
        self.cc_enc = cc_enc = fec.cc_encoder_make((MTU*8),k, 2, polys, 0, fec.CC_TAILBITING, True)
        self.access_key_0 = access_key_0 = '11100001010110101110100010010011'

        ##################################################
        # Blocks
        ##################################################

        self._time_offset_range = qtgui.Range(0.999, 1.001, 0.0001, 1.000, 200)
        self._time_offset_win = qtgui.RangeWidget(self._time_offset_range, self.set_time_offset, "Channel: Timing Offset", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._time_offset_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._noise_volt_range = qtgui.Range(0, 1, 0.01, 00, 200)
        self._noise_volt_win = qtgui.RangeWidget(self._noise_volt_range, self.set_noise_volt, "Channel: Noise Voltage", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._noise_volt_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._freq_offset_range = qtgui.Range(-0.1, 0.1, 0.001, 0, 200)
        self._freq_offset_win = qtgui.RangeWidget(self._freq_offset_range, self.set_freq_offset, "Channel: Frequency Offset", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._freq_offset_win, 0, 2, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._delay_range = qtgui.Range(0, 200, 1, 42, 200)
        self._delay_win = qtgui.RangeWidget(self._delay_range, self.set_delay, "Delay", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._delay_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.zeromq_push_msg_sink_0_0 = zeromq.push_msg_sink('tcp://127.0.0.1:5557', 100, False)
        self.zeromq_push_msg_sink_0 = zeromq.push_msg_sink('tcp://127.0.0.1:6667', 100, False)
        self.zeromq_pull_msg_source_0_0 = zeromq.pull_msg_source('tcp://127.0.0.1:6666', 100, False)
        self.zeromq_pull_msg_source_0 = zeromq.pull_msg_source('tcp://127.0.0.1:5555', 100, False)
        self._tuning_offset_range = qtgui.Range(-70e3, 70e3, 50, -21e3, 200)
        self._tuning_offset_win = qtgui.RangeWidget(self._tuning_offset_range, self.set_tuning_offset, "Frequency Tuning", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._tuning_offset_win)
        self.qtgui_freq_sink_x_1_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_1_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_1_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_1_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_1_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_1_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_1_0.enable_grid(False)
        self.qtgui_freq_sink_x_1_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_1_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_1_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_1_0.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_1_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_1_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_1_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_1_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_1_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_1_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_1_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_1_0_win)
        self.qtgui_freq_sink_x_1 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_1.set_update_time(0.10)
        self.qtgui_freq_sink_x_1.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_1.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_1.enable_autoscale(False)
        self.qtgui_freq_sink_x_1.enable_grid(False)
        self.qtgui_freq_sink_x_1.set_fft_average(1.0)
        self.qtgui_freq_sink_x_1.enable_axis_labels(True)
        self.qtgui_freq_sink_x_1.enable_control_panel(False)
        self.qtgui_freq_sink_x_1.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_1.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_1_win = sip.wrapinstance(self.qtgui_freq_sink_x_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_1_win)
        self.pdu_tagged_stream_to_pdu_0_0_0_0 = pdu.tagged_stream_to_pdu(gr.types.byte_t, 'packet_len')
        self.pdu_tagged_stream_to_pdu_0_0_0 = pdu.tagged_stream_to_pdu(gr.types.byte_t, 'packet_len')
        self.pdu_pdu_to_tagged_stream_0_2 = pdu.pdu_to_tagged_stream(gr.types.byte_t, 'packet_len')
        self.pdu_pdu_to_tagged_stream_0_0_1 = pdu.pdu_to_tagged_stream(gr.types.byte_t, 'packet_len')
        self.pdu_pdu_to_tagged_stream_0_0 = pdu.pdu_to_tagged_stream(gr.types.byte_t, 'packet_len')
        self.pdu_pdu_to_tagged_stream_0 = pdu.pdu_to_tagged_stream(gr.types.byte_t, 'packet_len')
        self._freq_range = qtgui.Range(2e9, 6e9, 100e3, 2.4e9, 200)
        self._freq_win = qtgui.RangeWidget(self._freq_range, self.set_freq, "'freq'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._freq_win)
        self.epy_block_9_0 = epy_block_9_0.selective_aes_encrypt(key_str="1234567890123456")
        self.epy_block_9 = epy_block_9.selective_aes_encrypt(key_str="1234567890123456")
        self.epy_block_8_0 = epy_block_8_0.ack_generator()
        self.epy_block_8 = epy_block_8.ack_generator()
        self.epy_block_7_1_0_0 = epy_block_7_1_0_0.addr_type_filter(my_ip="192.168.1.10")
        self.epy_block_7_1_0 = epy_block_7_1_0.addr_type_filter(my_ip="192.168.1.11")
        self.epy_block_7_0 = epy_block_7_0.sequence_decoder()
        self.epy_block_7 = epy_block_7.sequence_decoder()
        self.epy_block_6_0 = epy_block_6_0.ack_filter(timeout=1)
        self.epy_block_6 = epy_block_6.ack_filter(timeout=0.01)
        self.epy_block_5_0 = epy_block_5_0.PDUQueueStorage(timeout=1, max_retries=20)
        self.epy_block_5 = epy_block_5.PDUQueueStorage(timeout=1, max_retries=20)
        self.epy_block_4_0 = epy_block_4_0.AdvancedPacketizer(payload_len=32, delay=0.1)
        self.epy_block_4 = epy_block_4.AdvancedPacketizer(payload_len=32, delay=0.1)
        self.epy_block_3_1 = epy_block_3_1.ack_logger()
        self.epy_block_3_0 = epy_block_3_0.pdu_splitter(num_duplicates=num_duplicates)
        self.epy_block_3 = epy_block_3.ack_logger()
        self.epy_block_2_2 = epy_block_2_2.pdu_duplicator(num_duplicates=num_duplicates)
        self.epy_block_2 = epy_block_2.pdu_duplicator(num_duplicates=num_duplicates)
        self.epy_block_1_0 = epy_block_1_0.crc_fail_logger()
        self.epy_block_13 = epy_block_13.msg_logger()
        self.epy_block_12_0 = epy_block_12_0.priority_mux()
        self.epy_block_12 = epy_block_12.priority_mux()
        self.epy_block_11_1 = epy_block_11_1.selective_aes_decrypt(key_str="1234567890123456")
        self.epy_block_11 = epy_block_11.selective_aes_decrypt(key_str="1234567890123456")
        self.epy_block_10 = epy_block_10.pdu_splitter(num_duplicates=num_duplicates)
        self.epy_block_1 = epy_block_1.crc_fail_logger()
        self.epy_block_0_1 = epy_block_0_1.ack_repeater(num_repeats=20, delay=1)
        self.epy_block_0 = epy_block_0.ack_repeater(num_repeats=20, delay=1)
        self.digital_symbol_sync_xx_0_0_0 = digital.symbol_sync_cc(
            digital.TED_SIGNAL_TIMES_SLOPE_ML,
            sps,
            phase_bw,
            1.0,
            1.0,
            1.5,
            2,
            digital.constellation_bpsk().base(),
            digital.IR_PFB_MF,
            32,
            rrc_taps)
        self.digital_symbol_sync_xx_0_0 = digital.symbol_sync_cc(
            digital.TED_SIGNAL_TIMES_SLOPE_ML,
            sps,
            phase_bw,
            1.0,
            1.0,
            1.5,
            2,
            digital.constellation_bpsk().base(),
            digital.IR_PFB_MF,
            32,
            rrc_taps)
        self.digital_protocol_formatter_async_0_1 = digital.protocol_formatter_async(hdr_format)
        self.digital_protocol_formatter_async_0 = digital.protocol_formatter_async(hdr_format)
        self.digital_map_bb_0_0_0 = digital.map_bb([0,1,2,3])
        self.digital_map_bb_0_0 = digital.map_bb([0,1,2,3])
        self.digital_linear_equalizer_0_0_0 = digital.linear_equalizer(4, 2, variable_adaptive_algorithm_0, True, [ ], 'corr_est')
        self.digital_linear_equalizer_0_0 = digital.linear_equalizer(4, 2, variable_adaptive_algorithm_0, True, [ ], 'corr_est')
        self.digital_diff_decoder_bb_0_0_0 = digital.diff_decoder_bb(4, digital.DIFF_DIFFERENTIAL)
        self.digital_diff_decoder_bb_0_0 = digital.diff_decoder_bb(4, digital.DIFF_DIFFERENTIAL)
        self.digital_crc_check_0_0_0 = digital.crc_check(32, 0x4C11DB7, 0xFFFFFFFF, 0xFFFFFFFF, True, True, False, True, 0)
        self.digital_crc_check_0_0 = digital.crc_check(32, 0x4C11DB7, 0xFFFFFFFF, 0xFFFFFFFF, True, True, False, True, 0)
        self.digital_crc_append_0_0_0_0 = digital.crc_append(32, 0x4C11DB7, 0xFFFFFFFF, 0xFFFFFFFF, True, True, False, 0)
        self.digital_crc_append_0_0_0 = digital.crc_append(32, 0x4C11DB7, 0xFFFFFFFF, 0xFFFFFFFF, True, True, False, 0)
        self.digital_crc_append_0_0 = digital.crc_append(32, 0x4C11DB7, 0xFFFFFFFF, 0xFFFFFFFF, True, True, False, 0)
        self.digital_crc_append_0 = digital.crc_append(32, 0x4C11DB7, 0xFFFFFFFF, 0xFFFFFFFF, True, True, False, 0)
        self.digital_costas_loop_cc_0_0_0_0 = digital.costas_loop_cc(phase_bw, 4, False)
        self.digital_costas_loop_cc_0_0_0 = digital.costas_loop_cc(phase_bw, 4, False)
        self.digital_correlate_access_code_xx_ts_0_0_0 = digital.correlate_access_code_bb_ts("11100001010110101110100010010011",
          thresh, 'packet_len')
        self.digital_correlate_access_code_xx_ts_0_0 = digital.correlate_access_code_bb_ts("11100001010110101110100010010011",
          thresh, 'packet_len')
        self.digital_constellation_modulator_0_1 = digital.generic_mod(
            constellation=qpsk,
            differential=True,
            samples_per_symbol=sps,
            pre_diff_code=True,
            excess_bw=excess_bw,
            verbose=False,
            log=False,
            truncate=False)
        self.digital_constellation_modulator_0 = digital.generic_mod(
            constellation=qpsk,
            differential=True,
            samples_per_symbol=sps,
            pre_diff_code=True,
            excess_bw=excess_bw,
            verbose=False,
            log=False,
            truncate=False)
        self.digital_constellation_decoder_cb_0_0_0 = digital.constellation_decoder_cb(qpsk)
        self.digital_constellation_decoder_cb_0_0 = digital.constellation_decoder_cb(qpsk)
        self.channels_channel_model_0_1 = channels.channel_model(
            noise_voltage=noise_volt,
            frequency_offset=freq_offset,
            epsilon=time_offset,
            taps=[1],
            noise_seed=0,
            block_tags=False)
        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=noise_volt,
            frequency_offset=freq_offset,
            epsilon=time_offset,
            taps=[1],
            noise_seed=0,
            block_tags=False)
        self.blocks_unpack_k_bits_bb_0_0_0 = blocks.unpack_k_bits_bb(2)
        self.blocks_unpack_k_bits_bb_0_0 = blocks.unpack_k_bits_bb(2)
        self.blocks_throttle2_0_2 = blocks.throttle( gr.sizeof_char*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_throttle2_0_1_1 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_throttle2_0_1 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_char*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_tagged_stream_mux_0_1 = blocks.tagged_stream_mux(gr.sizeof_char*1, 'packet_len', 0)
        self.blocks_tagged_stream_mux_0 = blocks.tagged_stream_mux(gr.sizeof_char*1, 'packet_len', 0)
        self.blocks_repack_bits_bb_1_0_2 = blocks.repack_bits_bb(8, 1, "packet_len", False, gr.GR_MSB_FIRST)
        self.blocks_repack_bits_bb_1_0_0_0_0 = blocks.repack_bits_bb(1, 8, "packet_len", False, gr.GR_MSB_FIRST)
        self.blocks_repack_bits_bb_1_0_0_0 = blocks.repack_bits_bb(1, 8, "packet_len", False, gr.GR_MSB_FIRST)
        self.blocks_repack_bits_bb_1_0 = blocks.repack_bits_bb(8, 1, "packet_len", False, gr.GR_MSB_FIRST)
        self.blocks_pack_k_bits_bb_0_0_0 = blocks.pack_k_bits_bb(8)
        self.blocks_pack_k_bits_bb_0_0 = blocks.pack_k_bits_bb(8)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.digital_crc_append_0, 'out'), (self.epy_block_12, 'data_in'))
        self.msg_connect((self.digital_crc_append_0_0, 'out'), (self.epy_block_12_0, 'data_in'))
        self.msg_connect((self.digital_crc_append_0_0_0, 'out'), (self.epy_block_12, 'ack_in'))
        self.msg_connect((self.digital_crc_append_0_0_0_0, 'out'), (self.epy_block_12_0, 'ack_in'))
        self.msg_connect((self.digital_crc_check_0_0, 'fail'), (self.epy_block_1, 'in'))
        self.msg_connect((self.digital_crc_check_0_0, 'ok'), (self.epy_block_7_1_0_0, 'pdu_in'))
        self.msg_connect((self.digital_crc_check_0_0_0, 'fail'), (self.epy_block_1_0, 'in'))
        self.msg_connect((self.digital_crc_check_0_0_0, 'ok'), (self.epy_block_7_1_0, 'pdu_in'))
        self.msg_connect((self.digital_protocol_formatter_async_0, 'header'), (self.pdu_pdu_to_tagged_stream_0, 'pdus'))
        self.msg_connect((self.digital_protocol_formatter_async_0, 'payload'), (self.pdu_pdu_to_tagged_stream_0_0, 'pdus'))
        self.msg_connect((self.digital_protocol_formatter_async_0_1, 'payload'), (self.pdu_pdu_to_tagged_stream_0_0_1, 'pdus'))
        self.msg_connect((self.digital_protocol_formatter_async_0_1, 'header'), (self.pdu_pdu_to_tagged_stream_0_2, 'pdus'))
        self.msg_connect((self.epy_block_0, 'out'), (self.digital_crc_append_0_0_0_0, 'in'))
        self.msg_connect((self.epy_block_0_1, 'out'), (self.digital_crc_append_0_0_0, 'in'))
        self.msg_connect((self.epy_block_10, 'pdu_out'), (self.digital_crc_check_0_0_0, 'in'))
        self.msg_connect((self.epy_block_11, 'out'), (self.epy_block_7_0, 'pdu_in'))
        self.msg_connect((self.epy_block_11_1, 'out'), (self.epy_block_13, 'in'))
        self.msg_connect((self.epy_block_11_1, 'out'), (self.epy_block_7, 'pdu_in'))
        self.msg_connect((self.epy_block_12, 'pdu_out'), (self.epy_block_2, 'pdu_in'))
        self.msg_connect((self.epy_block_12_0, 'pdu_out'), (self.epy_block_2_2, 'pdu_in'))
        self.msg_connect((self.epy_block_2, 'pdu_out'), (self.digital_protocol_formatter_async_0, 'in'))
        self.msg_connect((self.epy_block_2_2, 'pdu_out'), (self.digital_protocol_formatter_async_0_1, 'in'))
        self.msg_connect((self.epy_block_3_0, 'pdu_out'), (self.digital_crc_check_0_0, 'in'))
        self.msg_connect((self.epy_block_4, 'out'), (self.epy_block_9, 'in'))
        self.msg_connect((self.epy_block_4_0, 'out'), (self.epy_block_9_0, 'in'))
        self.msg_connect((self.epy_block_5, 'pdu_out'), (self.digital_crc_append_0, 'in'))
        self.msg_connect((self.epy_block_5_0, 'pdu_out'), (self.digital_crc_append_0_0, 'in'))
        self.msg_connect((self.epy_block_6, 'pdu_out'), (self.epy_block_5, 'rn_in'))
        self.msg_connect((self.epy_block_6_0, 'pdu_out'), (self.epy_block_5_0, 'rn_in'))
        self.msg_connect((self.epy_block_7, 'to_ack'), (self.epy_block_8, 'pdu_in'))
        self.msg_connect((self.epy_block_7, 'to_app'), (self.zeromq_push_msg_sink_0, 'in'))
        self.msg_connect((self.epy_block_7_0, 'to_ack'), (self.epy_block_8_0, 'pdu_in'))
        self.msg_connect((self.epy_block_7_0, 'to_app'), (self.zeromq_push_msg_sink_0_0, 'in'))
        self.msg_connect((self.epy_block_7_1_0, 'pdu_out'), (self.epy_block_11_1, 'in'))
        self.msg_connect((self.epy_block_7_1_0, 'ack_out'), (self.epy_block_3_1, 'in'))
        self.msg_connect((self.epy_block_7_1_0, 'ack_out'), (self.epy_block_6_0, 'pdu_in'))
        self.msg_connect((self.epy_block_7_1_0_0, 'pdu_out'), (self.epy_block_11, 'in'))
        self.msg_connect((self.epy_block_7_1_0_0, 'ack_out'), (self.epy_block_3, 'in'))
        self.msg_connect((self.epy_block_7_1_0_0, 'ack_out'), (self.epy_block_6, 'pdu_in'))
        self.msg_connect((self.epy_block_8, 'pdu_out'), (self.epy_block_0, 'in'))
        self.msg_connect((self.epy_block_8_0, 'pdu_out'), (self.epy_block_0_1, 'in'))
        self.msg_connect((self.epy_block_9, 'out'), (self.epy_block_5, 'pdu_in'))
        self.msg_connect((self.epy_block_9_0, 'out'), (self.epy_block_5_0, 'pdu_in'))
        self.msg_connect((self.pdu_tagged_stream_to_pdu_0_0_0, 'pdus'), (self.epy_block_3_0, 'pdu_in'))
        self.msg_connect((self.pdu_tagged_stream_to_pdu_0_0_0_0, 'pdus'), (self.epy_block_10, 'pdu_in'))
        self.msg_connect((self.zeromq_pull_msg_source_0, 'out'), (self.epy_block_4, 'in'))
        self.msg_connect((self.zeromq_pull_msg_source_0_0, 'out'), (self.epy_block_4_0, 'in'))
        self.connect((self.blocks_pack_k_bits_bb_0_0, 0), (self.digital_correlate_access_code_xx_ts_0_0, 0))
        self.connect((self.blocks_pack_k_bits_bb_0_0_0, 0), (self.digital_correlate_access_code_xx_ts_0_0_0, 0))
        self.connect((self.blocks_repack_bits_bb_1_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.blocks_repack_bits_bb_1_0_0_0, 0), (self.pdu_tagged_stream_to_pdu_0_0_0, 0))
        self.connect((self.blocks_repack_bits_bb_1_0_0_0_0, 0), (self.pdu_tagged_stream_to_pdu_0_0_0_0, 0))
        self.connect((self.blocks_repack_bits_bb_1_0_2, 0), (self.blocks_throttle2_0_2, 0))
        self.connect((self.blocks_tagged_stream_mux_0, 0), (self.blocks_repack_bits_bb_1_0, 0))
        self.connect((self.blocks_tagged_stream_mux_0_1, 0), (self.blocks_repack_bits_bb_1_0_2, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.digital_constellation_modulator_0, 0))
        self.connect((self.blocks_throttle2_0_1, 0), (self.channels_channel_model_0, 0))
        self.connect((self.blocks_throttle2_0_1_1, 0), (self.channels_channel_model_0_1, 0))
        self.connect((self.blocks_throttle2_0_2, 0), (self.digital_constellation_modulator_0_1, 0))
        self.connect((self.blocks_unpack_k_bits_bb_0_0, 0), (self.blocks_pack_k_bits_bb_0_0, 0))
        self.connect((self.blocks_unpack_k_bits_bb_0_0_0, 0), (self.blocks_pack_k_bits_bb_0_0_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.digital_symbol_sync_xx_0_0_0, 0))
        self.connect((self.channels_channel_model_0_1, 0), (self.digital_symbol_sync_xx_0_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0_0, 0), (self.digital_diff_decoder_bb_0_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0_0_0, 0), (self.digital_diff_decoder_bb_0_0_0, 0))
        self.connect((self.digital_constellation_modulator_0, 0), (self.blocks_throttle2_0_1, 0))
        self.connect((self.digital_constellation_modulator_0, 0), (self.qtgui_freq_sink_x_1, 0))
        self.connect((self.digital_constellation_modulator_0_1, 0), (self.blocks_throttle2_0_1_1, 0))
        self.connect((self.digital_constellation_modulator_0_1, 0), (self.qtgui_freq_sink_x_1_0, 0))
        self.connect((self.digital_correlate_access_code_xx_ts_0_0, 0), (self.blocks_repack_bits_bb_1_0_0_0, 0))
        self.connect((self.digital_correlate_access_code_xx_ts_0_0_0, 0), (self.blocks_repack_bits_bb_1_0_0_0_0, 0))
        self.connect((self.digital_costas_loop_cc_0_0_0, 0), (self.digital_constellation_decoder_cb_0_0, 0))
        self.connect((self.digital_costas_loop_cc_0_0_0_0, 0), (self.digital_constellation_decoder_cb_0_0_0, 0))
        self.connect((self.digital_diff_decoder_bb_0_0, 0), (self.digital_map_bb_0_0, 0))
        self.connect((self.digital_diff_decoder_bb_0_0_0, 0), (self.digital_map_bb_0_0_0, 0))
        self.connect((self.digital_linear_equalizer_0_0, 0), (self.digital_costas_loop_cc_0_0_0, 0))
        self.connect((self.digital_linear_equalizer_0_0_0, 0), (self.digital_costas_loop_cc_0_0_0_0, 0))
        self.connect((self.digital_map_bb_0_0, 0), (self.blocks_unpack_k_bits_bb_0_0, 0))
        self.connect((self.digital_map_bb_0_0_0, 0), (self.blocks_unpack_k_bits_bb_0_0_0, 0))
        self.connect((self.digital_symbol_sync_xx_0_0, 0), (self.digital_linear_equalizer_0_0, 0))
        self.connect((self.digital_symbol_sync_xx_0_0_0, 0), (self.digital_linear_equalizer_0_0_0, 0))
        self.connect((self.pdu_pdu_to_tagged_stream_0, 0), (self.blocks_tagged_stream_mux_0, 0))
        self.connect((self.pdu_pdu_to_tagged_stream_0_0, 0), (self.blocks_tagged_stream_mux_0, 1))
        self.connect((self.pdu_pdu_to_tagged_stream_0_0_1, 0), (self.blocks_tagged_stream_mux_0_1, 1))
        self.connect((self.pdu_pdu_to_tagged_stream_0_2, 0), (self.blocks_tagged_stream_mux_0_1, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "pkt_8")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_MTU(self):
        return self.MTU

    def set_MTU(self, MTU):
        self.MTU = MTU

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_rrc_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts, 1.0/float(self.sps), 0.35, 11*self.sps*self.nfilts))
        self.digital_symbol_sync_xx_0_0.set_sps(self.sps)
        self.digital_symbol_sync_xx_0_0_0.set_sps(self.sps)

    def get_qpsk(self):
        return self.qpsk

    def set_qpsk(self, qpsk):
        self.qpsk = qpsk
        self.digital_constellation_decoder_cb_0_0.set_constellation(self.qpsk)
        self.digital_constellation_decoder_cb_0_0_0.set_constellation(self.qpsk)

    def get_polys(self):
        return self.polys

    def set_polys(self, polys):
        self.polys = polys

    def get_nfilts(self):
        return self.nfilts

    def set_nfilts(self, nfilts):
        self.nfilts = nfilts
        self.set_rrc_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts, 1.0/float(self.sps), 0.35, 11*self.sps*self.nfilts))

    def get_k(self):
        return self.k

    def set_k(self, k):
        self.k = k

    def get_access_key(self):
        return self.access_key

    def set_access_key(self, access_key):
        self.access_key = access_key
        self.set_hdr_format(digital.header_format_default(self.access_key, 0))

    def get_variable_adaptive_algorithm_0(self):
        return self.variable_adaptive_algorithm_0

    def set_variable_adaptive_algorithm_0(self, variable_adaptive_algorithm_0):
        self.variable_adaptive_algorithm_0 = variable_adaptive_algorithm_0

    def get_tuning_offset(self):
        return self.tuning_offset

    def set_tuning_offset(self, tuning_offset):
        self.tuning_offset = tuning_offset

    def get_time_offset(self):
        return self.time_offset

    def set_time_offset(self, time_offset):
        self.time_offset = time_offset
        self.channels_channel_model_0.set_timing_offset(self.time_offset)
        self.channels_channel_model_0_1.set_timing_offset(self.time_offset)

    def get_thresh(self):
        return self.thresh

    def set_thresh(self, thresh):
        self.thresh = thresh

    def get_sample_rate_blade(self):
        return self.sample_rate_blade

    def set_sample_rate_blade(self, sample_rate_blade):
        self.sample_rate_blade = sample_rate_blade

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle2_0_1.set_sample_rate(self.samp_rate)
        self.blocks_throttle2_0_1_1.set_sample_rate(self.samp_rate)
        self.blocks_throttle2_0_2.set_sample_rate(self.samp_rate)
        self.qtgui_freq_sink_x_1.set_frequency_range(0, self.samp_rate)
        self.qtgui_freq_sink_x_1_0.set_frequency_range(0, self.samp_rate)

    def get_rrc_taps(self):
        return self.rrc_taps

    def set_rrc_taps(self, rrc_taps):
        self.rrc_taps = rrc_taps

    def get_phase_bw(self):
        return self.phase_bw

    def set_phase_bw(self, phase_bw):
        self.phase_bw = phase_bw
        self.digital_costas_loop_cc_0_0_0.set_loop_bandwidth(self.phase_bw)
        self.digital_costas_loop_cc_0_0_0_0.set_loop_bandwidth(self.phase_bw)
        self.digital_symbol_sync_xx_0_0.set_loop_bandwidth(self.phase_bw)
        self.digital_symbol_sync_xx_0_0_0.set_loop_bandwidth(self.phase_bw)

    def get_num_duplicates(self):
        return self.num_duplicates

    def set_num_duplicates(self, num_duplicates):
        self.num_duplicates = num_duplicates

    def get_noise_volt(self):
        return self.noise_volt

    def set_noise_volt(self, noise_volt):
        self.noise_volt = noise_volt
        self.channels_channel_model_0.set_noise_voltage(self.noise_volt)
        self.channels_channel_model_0_1.set_noise_voltage(self.noise_volt)

    def get_hdr_format(self):
        return self.hdr_format

    def set_hdr_format(self, hdr_format):
        self.hdr_format = hdr_format

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.channels_channel_model_0.set_frequency_offset(self.freq_offset)
        self.channels_channel_model_0_1.set_frequency_offset(self.freq_offset)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq

    def get_extra_bytes(self):
        return self.extra_bytes

    def set_extra_bytes(self, extra_bytes):
        self.extra_bytes = extra_bytes

    def get_excess_bw(self):
        return self.excess_bw

    def set_excess_bw(self, excess_bw):
        self.excess_bw = excess_bw

    def get_delay(self):
        return self.delay

    def set_delay(self, delay):
        self.delay = delay

    def get_cc_enc(self):
        return self.cc_enc

    def set_cc_enc(self, cc_enc):
        self.cc_enc = cc_enc

    def get_access_key_0(self):
        return self.access_key_0

    def set_access_key_0(self, access_key_0):
        self.access_key_0 = access_key_0



def argument_parser():
    description = 'packet transmit'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "--MTU", dest="MTU", type=intx, default=1500,
        help="Set MTU [default=%(default)r]")
    return parser


def main(top_block_cls=pkt_8, options=None):
    if options is None:
        options = argument_parser().parse_args()

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(MTU=options.MTU)

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
