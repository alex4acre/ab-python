#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2021 Bosch Rexroth AG
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import time
import json
import pylogix
from pylogix import PLC

import datalayer
from datalayer.variant import Variant

from app.ab_provider_node import ABnode

value_address_str_1 = "SQLite/terminal-1"

def main():

    with datalayer.system.System("") as datalayer_system:
        datalayer_system.start(False)

        # This is the connection string for TCP in the format: tcp://USER:PASSWORD@IP_ADDRESS:PORT
        # Please check and change according your environment:
        # - USER:       Enter your user name here - default is boschrexroth
        # - PASSWORD:   Enter your password here - default is boschrexroth
        # - IP_ADDRESS: 127.0.0.1   If you develop in WSL and you want to connect to a ctrlX CORE virtual with port forwarding
        #               10.0.2.2    If you develop in a VM (Virtual Box, QEMU,...) and you want to connect to a ctrlX virtual with port forwarding
        #               192.168.1.1 If you are using a ctrlX CORE or ctrlX CORE virtual with TAP adpater

        #connectionProvider = "tcp://boschrexroth:boschrexroth@127.0.0.1:2070"
        connectionProvider = "tcp://boschrexroth:boschrexroth@192.168.1.1:2070"

        if 'SNAP' in os.environ:
            connectionProvider = "ipc://"

        print("Connecting", connectionProvider)
        with datalayer_system.factory().create_provider(connectionProvider) as provider:
            result = provider.start()
            if result is not datalayer.variant.Result.OK:
                print("ERROR Starting Data Layer Provider failed with:", result)
                return

            provider_node_str_1 = provide_string(provider, value_address_str_1)

            print("Start provider")
            provider.start()
            print("Running endless loop...")
            while provider.is_connected():
                time.sleep(1.0)  # Seconds

            print("ERROR Data Layer Provider is disconnected")

            print("Stopping Data Layer Provider: ", end=" ")
            result = provider.stop()
            print(result)

            print("Unregister provider Node", value_address_str_1, end=" ")
            result = provider.unregister_node(value_address_str_1)
            print(result)

            del provider_node_str_1

        datalayer_system.stop(True)

def provide_string(provider: datalayer.provider, name):
    # Create and register simple string provider node
    print("Creating string  provider node")
    variantString = Variant()
    variantString.set_string("Enter SQL script here. Use ';' as the last character to suppress result")
    provider_node_str = ABnode(provider, name, variantString)
    provider_node_str.register_node()
    return provider_node_str


if __name__ == '__main__':
    main()
