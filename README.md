secplus
=======

This project is a software implementation of the Security+ and Security+ 2.0 rolling code systems used in garage door openers made by Chamberlain, LiftMaster, Craftsman and others.

Encoding and decoding functionality is implemented in a MicroPython-compatible Python module (`secplus.py`) as well as an Arduino-compatible C library (`secplus.c` & `secplus.h`).

Sample GNU Radio flowgraphs for receiving and transmitting codes are also provided.

## Requirements

The following components are required to run the sample GNU Radio flowgraphs:

* GNU Radio 3.8 or later
* gr-osmosdr
* SDR hardware supported by gr-osmosdr (e.g. RTL-SDR, HackRF)

## Usage

### Receiving:
```
$ ./secplus_rx.py

Security+:  rolling=2320616982  fixed=876029923  (id1=2 id0=0 switch=1 remote_id=32445552 button=left)
Security+:  rolling=3869428094  fixed=876029922  (id1=2 id0=0 switch=0 remote_id=32445552 button=middle)
Security+:  rolling=2731817112  fixed=876029924  (id1=2 id0=0 switch=2 remote_id=32445552 button=right)
Security+:  rolling=2731817116  fixed=876029924  (id1=2 id0=0 switch=2 remote_id=32445552 button=right)
Security+:  rolling=2615434900  fixed=72906373  (id1=0 id0=0 switch=1 pad_id=1478 pin=1234)
Security+:  rolling=2615434904  fixed=595608121  (id1=0 id0=0 switch=1 pad_id=1478 pin=enter)
Security+ 2.0:  rolling=240124680  fixed=70678577664  (button=16 remote_id=1959100928)
Security+ 2.0:  rolling=240124681  fixed=70678577664  (button=16 remote_id=1959100928)
Security+ 2.0:  rolling=240124682  fixed=62088643072  (button=14 remote_id=1959100928)
Security+ 2.0:  rolling=240124683  fixed=66383610368  (button=15 remote_id=1959100928)
Security+ 2.0:  rolling=240124684  fixed=74973544960  (button=17 remote_id=1959100928)
```

### Transmitting Security+:

```
$ ./secplus_tx.py --freq 315150000 --rolling 2731817118 --fixed 876029924
```
The rolling code should be at least 2 higher than the previously transmitted rolling code.

### Transmitting Security+ 2.0:

With rolling and fixed codes only:
```
$ ./secplus_v2_tx.py --freq 315000000 --rolling 0xe50030d --fixed 0x1074c58200
```
With optional supplemental data (e.g. PIN):
```
$ ./secplus_v2_tx.py --freq 315000000 --rolling 0xe50030d --fixed 0x1074c58200 --data 0xd204b000
```
The rolling code should be at least 1 higher than the previously transmitted rolling code.

### secplus.py

This Python module encodes and decodes the rolling and fixed codes, provides utility functions to prepare on-off keying sequences for transmission, and pretty-print the codes. It can be used to build stand-alone applications. It uses a limited subset of Python so that it can be executed in MicroPython.

### secplus.c & secplus.h

This C library implements encoding & decoding of Security+ & Security+ 2.0 messages (both wireless & wireline). It it suitable for use in Arduino and other microcontrollers.

# Protocol details

### Security+

Much of the Security+ system is described in [US patent 6,980,655](https://patents.google.com/patent/US6980655B2/); the remaining details were determined by analyzing the data transmitted by Security+ remotes.

Transmissions use on-off keying, with an alphabet of three symbols (0, 1, 2) corresponding to three different pulse widths:
* 0: 1.5ms off, 0.5ms on
* 1: 1ms off, 1ms on
* 2: 0.5ms off, 1.5ms on

The payload consists of 40 symbols, which are transmitted in two frames of 20 symbols each. A single synchronization symbol is prepended to each frame: 0 for the first frame, and 2 for the second. 58ms of silence occurs after each frame, but the receiver I tested with accepts as little as 20ms. Remotes repeat the frame pair a minimum of four times, or continuously for as long as the button is held down.

The payload consists of a rolling code and a fixed code, each approximately 32 bits long. These values are combined and encoded into 40 ternary symbols for transmission. Despite being described as such in patents, the encoding is not encryption as there is no key.

The rolling code is incremented by three each time the remote button is pressed, and the fixed code remains the same. PIN pads use half of the fixed code symbols to transmit the four-digit PIN that was entered. Receivers accept codes so long as the fixed code corresponds to a programmed remote, and the current rolling code is less than 3072 above the last rolling code. Receivers will also accept any two consecutive rolling codes (and adjust the stored rolling code accordingly) so long as the two codes are not within 1024 below the last rolling code.

### Security+ 2.0

Security+ 2.0 is an updated (and incompatible) version released around 2011. Many of the details are described in
[US patent application US20110317835A1](https://patents.google.com/patent/US20110317835A1/), and the remainder was determined by analyzing packets transmitted by Security+ 2.0 remotes and wireline devices.

The payload consists of 80 or 128 bits, which are split into two 40- or 64-bit halves transmitted in separate packets. Each packet consists of a 20-bit preamble, a two-bit frame ID (which is 00 for the first packet, and 01 for the second), and 40 or 64 payload bits. Each packet is Manchester encoded (with a falling edge representing 0, and a rising edge representing 1).

The fixed code is 40 bits long, and the rolling code is 28 bits. The longer 64-bit packets also carry 32 supplemental data bits; PIN pads use these bits to convey the PIN entered by the user. The rolling code is "encrypted" by reversing its binary bits, then converting the resulting number to base 3. Each base-3 digit is converted to 2 binary bits. The fixed code and encrypted rolling code are then interleaved. Finally, the bits are permuted and inverted, with the permutation and inversion pattern depending on the values of particular base-3 digits of the encrypted rolling code.

The rolling code increases by one with each button press, and is sometimes shared across all buttons on a given remote.

## Basic Setup on Raspberry Pi

The following instructions work great for using a HackRF One.  If you patch the `xtrx.c` for a few kernel API changes, you can get xtrx-dkms to build and install, but it's not stricly necessary.  Removing it is simpler.

```bash
curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list
sudo apt-get update
sudo apt-get install tailscale && sudo tailscale up --ssh
sudo apt-get install -y vim git python3-pyqt5 gr-osmosdr
sudo apt purge xtrx-dkms
sudo apt autoremove
sudo QT_QPA_PLATFORM="headless" ./secplus_rx.py
```

To use the (cheap) RTL-SDR Blog v4, you need to install their drivers and make sure they're loaded.  Instructions [here](https://www.rtl-sdr.com/tag/install-guide/), which amount to:

```bash
sudo apt-get install libusb-1.0-0-dev git cmake pkg-config build-essential
git clone https://github.com/rtlsdrblog/rtl-sdr-blog
cd rtl-sdr-blog/
mkdir build
cd build
cmake ../ -DINSTALL_UDEV_RULES=ON
make
sudo make install
sudo cp ../rtl-sdr.rules /etc/udev/rules.d/
sudo ldconfig
echo 'blacklist dvb_usb_rtl28xxu' | sudo tee --append /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf
```

You then need to launch applications with `LD_LIBRARY_PATH=/usr/local/lib:/lib:/usr/lib` so that these libraries are preferred to the system ones installed above, or force that in `/etc/ld.so.conf`.
