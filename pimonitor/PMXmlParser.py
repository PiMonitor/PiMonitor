'''
Created on 29-03-2013

@author: citan
'''

import xml.sax
import os.path

from pimonitor.PM import PM
from pimonitor.PMParameter import PMParameter

# TODO: dependencies
# TODO: ecuparams

class PMXmlParser(xml.sax.ContentHandler):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        xml.sax.ContentHandler.__init__(self)
        
    def parse(self, file_name):
        self._parameters = set()
        self._parameter = None
        self._element_no = 0
        
        self._message = "Parsing XML data"
        self._log_id = PM.log(self._message)
        source = open(os.path.join("data", file_name))
        xml.sax.parse(source, self)
        PM.log(self._message + " [DONE]", self._log_id)
        
        return self._parameters

    def startElement(self, name, attrs):
        if name == "parameter":
            # set optional arguments
            byte_index = "none"
            bit_index = "none"

            for (k,v) in attrs.items():
                if k == "id":
                    pid = v
                if k == "name":
                    name = v
                if k == "desc":
                    desc = v
                if k == "ecubyteindex":
                    byte_index = int(v)
                if k == "ecubit":
                    bit_index = int(v)
                if k == "target":
                    target = int(v)

            self._parameter = PMParameter(pid, name, desc, byte_index, bit_index, target)
                          
        if name == "address":
            self._addrlen = 1
            for (k,v) in attrs.items():
                if k == "length":
                    self._addrlen = int(v)
                    
        if name == "depends":
            self._addrlen = 0

        if name == "ref":
            for (k,v) in attrs.items():
                if k == "parameter":
                    self._parameter.add_dependency(v)
            
        if name == "conversion" and self._parameter != None:
            for (k,v) in attrs.items():
                if k == "units":
                    units = v
                if k == "expr":
                    expr = v
                if k == "format":
                    value_format = v
                    
            if self._parameter != None:
                self._parameter.add_conversion([units, expr, value_format])
        
        self._name = name

    def characters(self, content):
        if len(content.strip()) > 0 and self._name == "address" and self._parameter != None:
            self._parameter.set_address(int(content, 16), self._addrlen)
        
    def endElement(self, name):
        if name == "parameter":
            self._parameters.add(self._parameter)
            self._parameter = None
            self._addrlen = None
             
        if name == "address":
            self._addrlen = 0

        if name == "depends":
            pass

        self._name = ""
        
        self._element_no += 1
        
        if self._element_no % 1000 == 0:
            PM.log(self._message + " " + str(self._element_no) + " elements", self._log_id)
