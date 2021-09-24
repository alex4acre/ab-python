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
import sys
import os
import time
import json
import pylogix
from pylogix import PLC

import datalayer
from datalayer.variant import Variant

from app.ab_provider_node import ABnode

bPLCPresent = False

testJson = """{"tag":
    [
        {"name":"SinCounter","type":"REAL"},
        {"name":"Line1_OEE","type":"REAL"},
        {"name":"mySINReflection_x10","type":"REAL"},
        {"name":"myLINT","type":"LINT"},
        {"name":"MyString","type":"STRING"},
        {"name":"MyControllerBOOL","type":"BOOL"},
        {"name":"MyControllerBOOL1","type":"BOOL"},
        {"name":"MyControllerBOOL2","type":"REAL"},
        {"name":"MyControllerBOOL3","type":"REAL"},
        {"name":"MyControllerBOOL4","type":"REAL"},
        {"name":"MyControllerBOOL5","type":"REAL"},
        {"name":"MyControllerBOOL6","type":"REAL"}
    ]
}"""
#        {"name":"MyControllerReal","type":"REAL"}
#{"name":"MyControllerBOOL","type":"BOOL"}
def main():
    sys.settrace
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
        connectionProvider = "tcp://boschrexroth:boschrexroth@192.168.1.11:2070"

        if 'SNAP' in os.environ:
            connectionProvider = "ipc://"

        
        if bPLCPresent: 
            print("PLC is present")
            #Load the json from file
        else:
            print("PLC is not present")
            jsonData = json.loads(testJson)
        

        #the list that contains all of the read data
        my_list = []

        print("Connecting", connectionProvider)
        with datalayer_system.factory().create_provider(connectionProvider) as provider:
            result = provider.start()
            if result is not datalayer.variant.Result.OK:
                print("ERROR Starting Data Layer Provider failed with:", result)
                return

            myVariantList = []
            myTaglist = []
            #parse the tag list
            tagList = jsonData['tag']
            for idx, tag in enumerate(tagList):
                print(idx)
                print(tag['name'])
                if bPLCPresent:
                    with PLC("192.168.1.9") as comm:
                        ret = comm.Read(tag['name'])
                        my_list.append(ret.Value)
                else:
                    data = "testData"        
                    if tag['type'] == "BOOL":
                        data = True       
                    elif tag['type'] == "SINT":
                        data = -1
                    elif tag['type'] == "INT":
                        data = -100
                    elif tag['type'] == "DINT":
                        data = -1000
                    elif tag['type'] == "LINT":
                        data = -10000
                    elif tag['type'] == "USINT":
                        data = 1
                    elif tag['type'] == "UINT":
                        data = 10
                    elif tag['type'] == "UDINT":
                        data = 100
                    elif tag['type'] == "LWORD":
                        data = 1000
                    elif tag['type'] == "REAL":
                        data = 1.2345
                    elif tag['type'] == "LREAL":
                        data = 123456789.0123
                    elif tag['type'] == "DWORD":
                        data = 1000
                    elif tag['type'] == "STRING":
                        data = "test data"
                    print("appended data: " + str(data) + ", Type :" + str(type(data)))
                    my_list.append(data)      
                #segmentation faults occur if there are not distinct nodes     
                myTaglist.append(ABnode(provider, tag['name'], my_list, idx, tag['type']))
                myTaglist[idx].register_node()            

            #print("Start provider")
            #provider.start()
            print("Running endless loop...")
            counter = 0
            while provider.is_connected() and counter < 6:
                time.sleep(1.0)  # Seconds
                counter = counter + 1

            print("ERROR Data Layer Provider is disconnected")

            print("Stopping Data Layer Provider: ", end=" ")
            result = provider.stop()
            print(result)

            for idx, tag in enumerate(tagList):
                print("Unregister provider Node", tag['name'], end=" ")
                result = provider.unregister_node("AB/" +  tag['name'])
                print(result)

        datalayer_system.stop(True)

def provide_string(provider: datalayer.provider, name: str, abTagValues : list, listIndex : int, datatype : str):
    # Create and register simple string provider node
    print("Creating string  provider node")
    variantString = Variant()
    variantString.set_string("Enter SQL script here. Use ';' as the last character to suppress result")
    provider_node_str = ABnode(provider, name, variantString, abTagValues, listIndex, datatype)
    provider_node_str.register_node()
    return provider_node_str


if __name__ == '__main__':
    main()
