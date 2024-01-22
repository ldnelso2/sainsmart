#!/usr/bin/env python3

# This is for a Sainsmart USB 16-channel relay
# SKU: http://wiki.sainsmart.com/index.php/101-70-208
# The wiki link gives serial commands
# SKU: 101-70-208
#
# QinHeng Electronics HL-340 USB-Serial adapter
#
# To run with pyusb debugging:
#
#   PYUSB_DEBUG=debug python relay.py
#
# Grab the vendor and product codes from syslog when plugging in the relay:
#
#  Ex:  idVendor=1a86, idProduct=7523
#
# Adapted from RJ's gitgist https://gist.github.com/RJ/7acba5b06a03c9b521601e08d0327d56
# ... and pyusb tutorial:  https://github.com/pyusb/pyusb

import sys
import time
import usb.core
import usb.util
import argparse


close_relay_cmd = [0xA0, 0x01, 0x01, 0xA2]
open_relay_cmd = [0xA0, 0x01, 0x00, 0xA1]

# Since I'm using this to send a signal to a gate controller, I'm simulating just
# pressing a button to make the circuit for 2 seconds, then releasing:
# Example: 
# ep.write(close_relay_cmd)
# time.sleep(2)
# ep.write(open_relay_cmd)

# Sainsmart 16-channel commands
# NOTE - it looks like the sainsmart likes to receive the commands
# for some reason as a tuple or a list from python.
# dev.reset() reset

################# Initial serial command variables in hex for testing ###############################
op_all = [0x3A, 0x46, 0x45, 0x30, 0x46, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x31, 0x30, 0x30, 0x32, 0x30, 0x30, 0x30, 0x30, 0x45, 0x31, 0x0D, 0x0A]

cl_all = [0x3A, 0x46, 0x45, 0x30, 0x46, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x31, 0x30, 0x30, 0x32, 0x46, 0x46, 0x46, 0x46, 0x45, 0x33, 0x0D, 0x0A]

c6_on=[0x3A, 0x46, 0x45, 0x30, 0x35, 0x30, 0x30, 0x30, 0x35, 0x46, 0x46, 0x30, 0x30, 0x46, 0x39, 0x0D, 0x0A]

c6_off=[0x3A, 0x46, 0x45, 0x30, 0x35, 0x30, 0x30, 0x30, 0x35, 0x30, 0x30, 0x30, 0x30, 0x46, 0x38, 0x0D, 0x0A]

# TODO: dev.reset() resets the driver
# TODO: Should make a function to reset and re-run the init of USB control


#########3 Overall Sainsmart Control Commands List Array ###############
# Decimal format, converted from hex based on sainsmart documentation
# The format for indexing the control serial messages is: 
# Relay Number X 2 = turn on that relay
# Relay Number X 2 + 1 = turn off that relay
# For example, 
# ep.write(ss_cont[12])     # turns off relay number 6
# ep.write(ss_cont[13])     # would turn off relay number 6  
#
# ep.write(ss_cont[34]) turns on ALL relays 
# ep.write(ss_cont[35]) turns off ALL relays


ss_cont = [[58, 70, 69, 48, 49, 48, 48, 48, 48, 48, 48, 49, 48, 70, 49, 13, 10],
 [58, 70, 69, 48, 49, 48, 48, 50, 48, 48, 48, 48, 48, 70, 70, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 48, 70, 70, 48, 48, 70, 69, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 48, 48, 48, 48, 48, 70, 68, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 49, 70, 70, 48, 48, 70, 68, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 49, 48, 48, 48, 48, 70, 67, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 50, 70, 70, 48, 48, 70, 67, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 50, 48, 48, 48, 48, 70, 66, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 51, 70, 70, 48, 48, 70, 66, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 51, 48, 48, 48, 48, 70, 65, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 52, 70, 70, 48, 48, 70, 65, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 52, 48, 48, 48, 48, 70, 57, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 53, 70, 70, 48, 48, 70, 57, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 53, 48, 48, 48, 48, 70, 56, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 54, 70, 70, 48, 48, 70, 56, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 54, 48, 48, 48, 48, 70, 55, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 55, 70, 70, 48, 48, 70, 55, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 55, 48, 48, 48, 48, 70, 54, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 56, 70, 70, 48, 48, 70, 54, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 56, 48, 48, 48, 48, 70, 53, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 57, 70, 70, 48, 48, 70, 53, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 57, 48, 48, 48, 48, 70, 52, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 65, 70, 70, 48, 48, 70, 52, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 65, 48, 48, 48, 48, 70, 51, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 66, 70, 70, 48, 48, 70, 51, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 66, 48, 48, 48, 48, 70, 50, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 67, 70, 70, 48, 48, 70, 50, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 67, 48, 48, 48, 48, 70, 49, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 68, 70, 70, 48, 48, 70, 49, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 68, 48, 48, 48, 48, 70, 48, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 69, 70, 70, 48, 48, 70, 48, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 69, 48, 48, 48, 48, 70, 70, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 70, 70, 70, 48, 48, 70, 70, 13, 10],
 [58, 70, 69, 48, 53, 48, 48, 48, 70, 48, 48, 48, 48, 70, 69, 13, 10],
 [58, 70, 69, 48, 70, 48, 48, 48, 48, 48, 48, 49, 48, 48, 50, 70, 70, 70, 70, 69, 51, 13, 10],
 [58, 70, 69, 48, 70, 48, 48, 48, 48, 48, 48, 49, 48, 48, 50, 48, 48, 48, 48, 69, 49, 13, 10]]


# Not really necessary, but just to be safe, here is the control index, and now we have it in github
ss_control_list = ['Status',
 'Status-Return',
 '1-CH ON',
 '1-CH OFF',
 '2-CH ON',
 '2-CH OFF',
 '3-CH ON',
 '3-CH OFF',
 '4-CH ON',
 '4-CH OFF',
 '5-CH ON',
 '5-CH OFF',
 '6-CH ON',
 '6-CH OFF',
 '7-CH ON',
 '7-CH OFF',
 '8-CH ON',
 '8-CH OFF',
 '9-CH ON',
 '9-CH OFF',
 '10-CH ON',
 '10-CH OFF',
 '11-CH ON',
 '11-CH OFF',
 '12-CH ON',
 '12-CH OFF',
 '13-CH ON',
 '13-CH OFF',
 '14-CH ON',
 '14-CH OFF',
 '15-CH ON',
 '15-CH OFF',
 '16-CH ON',
 '16-CH OFF',
 'All ON',
 'All OFF']


class RelayDevice(object):
    """Sainsmart 16 Channel Relay Device"""

    ep_dev = None
    verbose = False

    def __init__(self, find_all=False):
        dev = usb.core.find(idVendor=0x1a86, idProduct=0x7523, find_all=find_all)

        if dev is None:
            raise ValueError("Device not found")

        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)

        cfg = dev.get_active_configuration()
        intf = cfg[(0,0)]

        ep = usb.util.find_descriptor(
            intf,
            # match the first OUT endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_OUT)

        assert ep is not None
        self.ep_dev = ep

    def get_relay_command_index(self, relay_number, state="on"):
        relay_val = ss_cont[-1] # All off

        if relay_number <= 16 and relay_number > 0:
            if state == "on":
                relay_val = (relay_number * 2)
            elif state == "off":
                relay_val = (relay_number * 2) + 1
            else:
                print(f"Warning, invalid state: {state}")
        else:
            print(f"Warning, relay value out of range [1-16]: {relay_number}")

        return relay_val

    def all_channels_on(self):
        if self.verbose:
            print("Enabling all relays.")
        self.ep_dev.write(ss_cont[-2])
        time.sleep(0.1)

    def all_channels_off(self):
        if self.verbose:
            print("Disabling all relays.")
        self.ep_dev.write(ss_cont[-1])
        time.sleep(0.1)

    def on(self, relay_number):
        relay_index = self.get_relay_command_index(int(relay_number), "on")
        if relay_index == ss_cont[-1]:
            print("Can not execute command.")
            return

        if self.verbose:
            print(f"Enabling relay #:  {relay_number}")

        self.ep_dev.write(ss_cont[relay_index])

    def off(self, relay_number):
        relay_index = self.get_relay_command_index(int(relay_number), "off")
        if relay_index == ss_cont[-1]:
            print("Can not execute command.")
            return

        if self.verbose:
            print(f"Disabling relay #: {relay_number}")

        self.ep_dev.write(ss_cont[relay_index])

    def test_pattern(self, cycles=3):
        cycle_count=0

        self.all_channels_off()
        while(cycle_count < cycles):
            for idx in range(1,17):
                self.on(idx)
                time.sleep(0.1)
            for idx in range(0,16):
                self.off(16-idx)
                time.sleep(0.1)
            cycle_count += 1


def main(args):
    relay_dev = RelayDevice()
    if relay_dev.ep_dev is None:
        print("Failed to initialize relay board.")
        exit(2)

    if args.verbose:
        relay_dev.verbose = True

    if args.test_pattern:
        relay_dev.test_pattern()
        exit(0)

    if args.all_off:
        relay_dev.all_channels_off()
        exit(0)

    if args.all_on:
        relay_dev.all_channels_on()
        exit(0)

    if args.on is not None:
        for relay in args.on:
            if args.verbose:
                print(f"Relay: {relay}")
            relay_dev.on(relay)

    if args.off is not None:
        for relay in args.off:
            if args.verbose:
                print(f"Relay: {relay}")
            relay_dev.off(relay)

    exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple CLI program to control Sainsmart 16 Channel relay boards.")
    parser.add_argument("--on", nargs="+", required=False, help="Relay number to enable. Can be presented as a list (--on 6 9 11).")
    parser.add_argument("--off", nargs="+", required=False, help="Relay number to disable. Can be presented as a list (--off 4 2 10).")
    parser.add_argument("--all_on", action="store_true", required=False, help="Enable all relays.")
    parser.add_argument("--all_off", action="store_true", required=False, help="Disable all relays.")
    parser.add_argument("-t", "--test_pattern", action="store_true", required=False, help="Runs wheel test pattern on relays.")
    parser.add_argument("-v", "--verbose", action="store_true", required=False, help="Enable verbose outputs.")

    # No args given
    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit(1)

    args = parser.parse_args()

    if args.verbose:
        print(args)

    main(args)
