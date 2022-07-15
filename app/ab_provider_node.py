# MIT License
#
# Copyright (c) 2021, Bosch Rexroth AG
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

import json
import os
from datalayer import variant
import datalayer.clib
import datalayer
from datalayer.provider_node import ProviderNodeCallbacks, NodeCallback
from datalayer.variant import Result, Variant, VariantType

import flatbuffers
from comm.datalayer import Metadata
from comm.datalayer import AllowedOperations
from comm.datalayer import Reference

#import app.utils

class ABnode:

    #def __init__(self,provider : datalayer.provider, address : str , initialValue: Variant, abTagValues : list, listIndex : int, datatype : str ):
    def __init__(self, provider : datalayer.provider, address : str, abTagValues : list, listIndex : int, datatype : str ):
        
        self.cbs = ProviderNodeCallbacks(
            self.__on_create,
            self.__on_remove,
            self.__on_browse,
            self.__on_read,
            self.__on_write,
            self.__on_metadata
        )

        self.provider = provider
        self.data = Variant()
        #self.data = initialValue
        self.address = "AB/" + address
        self.abTagValues = abTagValues
        self.listIndex = listIndex
        self.type = datatype    
        self.metadata = Variant()
        self.providerNode = datalayer.provider_node.ProviderNode(self.cbs)
        
        #copies the data from the list to the active data when initialized
        self.updateVariantValue()
        print("metadata:",self.metadata)

    def register_node(self):
      self.provider.register_node(self.address, self.providerNode)

    def set_value(self,value: Variant):
        self.data = value

    def __on_create(self, userdata: datalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        print("__on_create()", "address:", address, "userdata:", userdata)
        cb(Result.OK, data)

    def __on_remove(self, userdata: datalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        print("__on_remove()", "address:", address, "userdata:", userdata)
        cb(Result.UNSUPPORTED, None)

    def __on_browse(self, userdata: datalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        print("__on_browse()", "address:", address, "userdata:", userdata)
        new_data = Variant()
        new_data.set_array_string([])
        cb(Result.OK, new_data)

    def __on_read(self, userdata: datalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        #print("__on_read()", "address:", address, "data:", self.data, "userdata:", userdata)
        
        #self.data = data.clone()
        #_value = self.abTagValues[self.listIndex]
        #self.updateVariantValue()
        #utils.setVariantValue(self.data, _value, self.type)
        new_data = self.data
        cb(Result.OK, self.data)

    def __on_write(self, userdata: datalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        _data = data
        #self.setVariantValue(data.get_int16())
        #self.abTagValues[self.listIndex] = data.get_int16()
        #print(data.get_int16())
        cb(Result.OK, self.data)

    def __on_metadata(self, userdata: datalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        print("__on_metadata()", "address:", address,"metadata:",self.metadata, "userdata:", userdata)
        cb(Result.OK, self.metadata)

    def setVariantValue(self, data : object) -> Result:
        try:
            if self.type == "BOOL":
                return self.data.set_bool8(data)
            elif self.type == "SINT":
                return self.data.set_int8(data)
            elif self.type == "INT":
                return self.data.set_int16(data)    
            elif self.type == "DINT":
                return self.data.set_int32(data)    
            elif self.type == "LINT":
                return self.data.set_int64(data)    
            elif self.type == "USINT":
                return self.data.set_uint8(data)    
            elif self.type == "UINT":
                return self.data.set_uint16(data)    
            elif self.type == "UDINT":
                return self.data.set_uint32(data)    
            elif self.type == "LWORD":
                return self.data.set_uint64(data)    
            elif self.type == "REAL":
                return self.data.set_float32(data)    
            elif self.type == "LREAL":
                return self.data.set_float64(data)    
            elif self.type == "DWORD":
                return self.data.set_uint32(data)
            elif self.type == "STRING":
                return self.data.set_string(data)
        except Exception as e:
            print(e)

    def getVariantValue(self):
        try:
            if self.type == "BOOL":
                return self.data.get_bool8()
            elif self.type == "SINT":
                return self.data.get_int8()
            elif self.type == "INT":
                return self.data.get_int16()    
            elif self.type == "DINT":
                return self.data.get_int32()    
            elif self.type == "LINT":
                return self.data.get_int64()    
            elif self.type == "USINT":
                return self.data.get_uint8()    
            elif self.type == "UINT":
                return self.data.get_uint16()    
            elif self.type == "UDINT":
                return self.data.get_uint32()    
            elif self.type == "LWORD":
                return self.data.get_uint64()    
            elif self.type == "REAL":
                return self.data.get_float32()    
            elif self.type == "LREAL":
                return self.data.get_float64()    
            elif self.type == "DWORD":
                return self.data.get_uint32()
            elif self.type == "STRING":
                return self.data.get_string()
        except Exception as e:
            print(e)

    def updateVariantValue(self) -> Result:
        return self.setVariantValue(self.abTagValues[self.listIndex])

