#!/bin/bash

# This is a handy wrapper to set the variables necessary to run secplus "headless" as just a CLI

LD_LIBRARY_PATH=/usr/local/lib:/lib:/usr/lib QT_QPA_PLATFORM="offscreen" ~/code/secplus/secplus_rx.py
