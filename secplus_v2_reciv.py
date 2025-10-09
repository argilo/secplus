#!/usr/bin/env python3
import sys
import argparse
import datetime
import signal
# import traceback
import rflib
import secplus

# pylint: disable=W0614,unused-import


DRATE = 4000
DEFAULT_FREQ = 315000000
chan_bw = 540000 # 240000 # 93750  # 640000
dataWhitening = 0
pktLen = 90
verbose = 0
print_time = 0

def parse_args():
    parser = argparse.ArgumentParser(
        description='receive security+ V2 packets')

    parser.add_argument("-f", "-F", "--freq", dest="freq", type=int,
                        default=DEFAULT_FREQ,
                        help="Set Frequency [default=%(default)r]")

    parser.add_argument('-t', '--time', dest="time",
                        help='Log time',
                        action='store_true', default=False)

    parser.add_argument('-v', '--verbose',
                        help='Increase debug verbosity', action='count')

    return parser.parse_args()


def configure_RfCat(freq):

    rf = rflib.RfCat(debug=False)
    # rf.setMdmChanBW(chan_bw)

    rf.setMdmDRate(DRATE)
    #- rf.setBSLimit(BSCFG_BS_LIMIT_6)  # 0 3 6 12

    rf.setEnableMdmManchester(False)

    # rf.makePktFLEN(pktLen)

    #-rf.setEnablePktDataWhitening(dataWhitening)
    # rf.setEnableMdmFEC(1)



    # 00011110 -> 1010100101010110
    syncword = 0b1010101010101010  #10101010 # 1010101010101010101 0xAAAA
    # syncword_b = f"{syncword:016b}"
    rf.setMdmSyncWord(syncword)

    #- rf.setMdmChanBW(chan_bw)

    rf.setFreq(freq)
    rf.setMdmModulation(rflib.MOD_ASK_OOK)

    # rf.setMdmSyncMode(rflib.SYNCM_CARRIER_15_of_16)
    rf.setMdmSyncMode(rflib.SYNCM_CARRIER)

    # SYNCM_NONE: None
    # SYNCM_15_of_16: 15 of 16 bits must match
    # SYNCM_16_of_16: 16 of 16 bits must match
    # SYNCM_30_of_32: 30 of 32 sync bits must match
    # SYNCM_CARRIER: Carrier Detect
    # SYNCM_CARRIER_15_of_16: Carrier Detect and 15 of 16 sync bits must match
    # SYNCM_CARRIER_16_of_16: Carrier Detect and 16 of 16 sync bits must match
    # SYNCM_CARRIER_30_of_32: Carrier Detect and 30 of 32 sync bits must match


    if verbose:
        # rf.printRadioConfig()
        print( "\n== Frequency Configuration ==")
        print( rf.reprFreqConfig())
        print( "\n== Modem Configuration ==")
        print( rf.reprModemConfig())
        print( "\n== Packet Configuration ==")
        print( rf.reprPacketConfig())
        sys.stdout.flush()

    return rf


def demanchester(st):
    x = 1
    b = []
    slen = len(st)

    # Note that since 1 starts as "1"
    # we are testing the 2nd bit for '1' or '0'
    while x < slen:
        if st[x] == st[x-1] :
            break
            # x += 1
            # continue
        if st[x] == "1":
            b.append("1")
        else:
            b.append("0")
        x = x + 2

    return "".join(b)

def keystop(delay=0):
    return len(rflib.select.select([sys.stdin], [], [], delay)[0])

if __name__ == "__main__":
    args = parse_args()

    use_freq = args.freq

    verbose = args.verbose
    print_time = args.time
    d = None

    def sig_handler(sig=None, _frame=None):
        if d:
            d.setModeIDLE()
        if sig:
            print(f"Sig = {sig}")
        sys.exit(0)

    signal.signal(signal.SIGABRT, sig_handler)
    signal.signal(signal.SIGSEGV, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    d = configure_RfCat(freq=use_freq)


    pat =  "000011110"

    # 00011110 => 1010100101010110
    # 000000011110
    patm =    "101010101010100101010110"
    patm_len = len(patm)

    z = 0
    o = 0
    pkt_1 = pkt_2 = ""
    prev_data = ""
    while not keystop():
        try:
            y, t = d.RFrecv(timeout=2000)
            s = ''
            idx = 0
            s = prev_data[-32:] + ''.join(f"{x:08b}" for x in bytearray(y))

            prev_data = s[:32]


            idx = 0
            if patm in s:
                while patm in s[idx:]:
                    idx = s.find(patm, idx)

                    pkt = demanchester(s[idx:idx + 120])

                    if len(pkt) < 40:
                        idx += patm_len
                        continue

                    i = pkt.find(pat)
                    pkt = pkt[i + 8: i + 50]  # skip preamble and trim

                    idx += patm_len

                    if pkt[0] != "0" or pkt[2:4] != "00":
                        print("SKIP bit check", pkt[:4], "\n\n")
                        continue

                    if pkt[:2] == "00" and len(pkt) > 40:
                        pkt_1 = pkt[2:]

                    elif pkt[:2] == "01" and len(pkt) > 40:
                        pkt_2 = pkt[2:]

                    else:
                        continue

                    if pkt_1 and pkt_2:
                        try:
                            full_pkt = pkt_1[:40] + pkt_2[:40]
                            full_pkt_list = list(map(int, list(full_pkt)))

                            rolling_out, fixed_out, _data = secplus.decode_v2(full_pkt_list)

                            pretty_out = secplus.pretty_v2(rolling_out, fixed_out)
                            if print_time:
                                print(f"{datetime.datetime.now()}")
                            print(f"{pretty_out}\n")
                            pkt_1 = pkt_2 = ""
                        except ValueError as _e:
                            # print("ValueError", _e)
                            continue

        except rflib.ChipconUsbTimeoutException:
            o = 0
            if verbose:
                print(".", end="")
            sys.stdout.flush()

        except KeyboardInterrupt:
            print("Please press <enter> to stop")

        except IndexError as _e:
            #print("Index fail: ", str(_e))
            pass


    # sys.stdin.read(1)

    d.setModeIDLE()
    d = None
