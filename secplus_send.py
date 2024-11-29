#!/usr/bin/env python3

"""
    Send Security+ v1
"""

# pylint: disable=invalid-name

from __future__ import print_function

import sys
# from rflib import *
import argparse
import rflib
import secplus
# import pprint

__author__ = "Peter Shipley"

verbose = 0
noop = 0


# bit len = 500
# 500 * 10^-6 = .00050
# 1/.00050  = 2000
DRATE = 2000
CMD_REPEAT = 1
DEFAULT_RF_FREQ = 315000000


def bitstring_to_bytes8(s):
    return int(s, 2).to_bytes(len(s) // 8, byteorder='big')


def init_RfCat(data_len=60, freq=None, chan_bw=240000, tx_power=96, dat_rate=DRATE):
    """
        create RfCat obj
    """
    # Start up RfCat
    rfc = rflib.RfCat()

    # Set Modulation. We using On-Off Keying here
    rfc.setMdmModulation(rflib.MOD_ASK_OOK)

    # Configure the radio
    rfc.makePktFLEN(data_len) # Set the RFData packet length
    rfc.setMdmDRate(dat_rate)         # Set the Baud Rate
    rfc.setMdmSyncMode(0)         # Disable preamble
    rfc.setFreq(freq)        # Set the frequency
    rfc.setEnableMdmManchester(False)

    # d.setMaxPower()
    if tx_power:
        rfc.setPower(tx_power)

    if chan_bw:
        rfc.setMdmChanBW(chan_bw)

    if verbose:
        dr = rfc.getMdmDRate()
        bw = rfc.getMdmChanBW()
        f1 = rfc.getFreq()
        print("DRate:", dr, "ChanBW", bw)
        print("Freq:", f1[0])
        rfc.printRadioConfig()
        #print("# Freq delta {:0.5f}".format(fq - fr), file=sys.stderr)

    return rfc

def send_secplus_v1(fixed_dat=1234567890, freq=315000000, roll_dat=123456789, cmd_repeat=1):

    # Join the prefix and the data for the full pwm key, must repeat 3 time
    pkt_seq = [0]*100 + secplus.encode_ook(roll_dat, fixed_dat, fast=False)*4 + [0]*100

    bit_seq = "".join(map(str, pkt_seq))
    bit_seq += "0" * (len(bit_seq) % 8)    # pad to bits

    if verbose:
        print("bit_seq", len(bit_seq), bit_seq)

    # Convert the data to bin
    rf_data = bitstring_to_bytes8(bit_seq)

    if noop:
        return 0

    d = init_RfCat(freq=freq, data_len=len(bit_seq))

    if d is None:
        print("rflib Error")
        sys.exit(0)
        # return -1

    if verbose:
        print("Repeat:", cmd_repeat)

    with open("rf_data.dat", "wb") as fd:
        fd.write(rf_data)

    d.RFxmit(rf_data, repeat=cmd_repeat)

    d.setModeIDLE()

    d = None
    return 0

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-F", "--Freq", "--freq", dest="freq", type=int,
                        default=DEFAULT_RF_FREQ,
                        help="Set Frequency [default=%(default)r]")

    parser.add_argument('-r', "--rolling", dest="rolling", type=int,
                        default=123456789,
                        help="Set Rolling code [default=%(default)r]")

    parser.add_argument("-f", "--fixed", metavar='fixed_code', dest="fixed",
                           type=int, default=1234567890,
                           help="Set Fixed code [default=%(default)r]")

    parser.add_argument("-n", "--noop", dest="noop", action='store_true',
                           help="No op/Do not transmit")

    # fixed_grp = parser.add_mutually_exclusive_group()

    parser.add_argument('-v', '--verbose', dest="verb",
                            default=0,
                            help='Increase debug verbosity', action='count')

    return parser.parse_args()

if __name__ == "__main__":

    args = get_args()

    noop = args.noop

    if args.verb:
        verbose = args.verb

    if args.rolling >= 4294967296:
        raise ValueError("Rolling code must be less than 2^32")
    if args.fixed >= 3486784401:
        raise ValueError("Fixed code must be less than 3^20")

    send_secplus_v1(fixed_dat=args.fixed, freq=args.freq, roll_dat=args.rolling)

    sys.exit(0)
