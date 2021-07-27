#!/usr/bin/env python
#
# :author: Fabio "BlackLight" Manganiello <info@fabiomanganiello.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Some of the functionalities of the bluetooth LE stack (like
# device scanning) require special user privileges. Solutions:
#
# - Run this script as root
# - Set `cap_net` capabilities on your Python interpreter:
#     `[sudo] setcap 'cap_net_raw,cap_net_admin+eip' /path/to/python
#
# Note however that the latter option will set the privileges for any
# script that runs on that Python interpreter. If it's a security concern,
# then you might want to set the capabilities on a Python venv executable
# made specifically for Switchbot instead.

import sys
import time
from contextlib import contextmanager

import bluetooth
from bluetooth.ble import DiscoveryService, GATTRequester


@contextmanager
def connect(device: str, bt_interface: str, timeout: float):
    if bt_interface:
        req = GATTRequester(device, False, bt_interface)
    else:
        req = GATTRequester(device, False)

    req.connect(False, 'random')
    connect_start_time = time.time()

    while not req.is_connected():
        if time.time() - connect_start_time >= timeout:
            raise ConnectionError('Connection to {} timed out after {} seconds'.
                                  format(device, timeout))
        time.sleep(0.1)

    yield req

    if req.is_connected():
        req.disconnect()

class Driver(object):
    handles = {
        'press': 0x16,
        'on': 0x16,
        'off': 0x16,
        'open': 0x0D,
        'close': 0x0D,
        'pause': 0x0D,
    }
    commands = {
        'press': b'\x57\x01\x00',
        'on': b'\x57\x01\x01',
        'off': b'\x57\x01\x02',
        'open': b'\x57\x0F\x45\x01\x05\xFF\x00',
        'close': b'\x57\x0F\x45\x01\x05\xFF\x64',
        'pause': b'\x57\x0F\x45\x01\x00\xFF',
    }

    def __init__(self, device, bt_interface=None, timeout_secs=None):
        self.device = device
        self.bt_interface = bt_interface
        self.timeout_secs = timeout_secs if timeout_secs else 5

    def run_command(self, command):
        with connect(self.device, self.bt_interface, self.timeout_secs) as req:
            print('Connected!')
            return req.write_by_handle(self.handles[command], self.commands[command])


def press_switch(macAddr):
    sw_interface = "hci0"
    sw_timeout_sec = 5
    driver = Driver(device=macAddr, bt_interface=sw_interface, timeout_secs=sw_timeout_sec)
    driver.run_command("press")
    print('Command execution successful')    

# vim:sw=4:ts=4:et: