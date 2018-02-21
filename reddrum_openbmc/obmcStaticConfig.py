
# Copyright Notice:
#    Copyright 2018 Dell, Inc. All rights reserved.
#    License: BSD License.  For full license text see link: https://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC/LICENSE.txt

import os
import json

# put any static config data for OpenBMC here
class RdOpenBmcStaticConfig():
    def __init__(self):
        self.mgrId    =    "obmc"
        self.mgrModel =    "OpenBMC"
        self.sysId    =    "1"
        self.chasId   =    "1"
        self.sysManufacturer = "Contoso-X"
        self.sysModel        = "Rackmount-R2018-X"
        self.sysPartNumber   = "PN123456"

        # list all supported serial interfaces anyOf: "SSH", "IPMI"
        self.serialConsoleConnectTypesSupported  =  ["SSH","IPMI"]     
        self.serialConsoleEnabled  =  True

        # list of supported cmd shell protocols: "SSH", "Telnet" ?
        self.commandShellConnectTypesSupported  =  ["SSH"]  
        self.commandShellEnabled  =  True


    def getStaticConfigInfo(self):
        pass
        return(0)


    # --------------------------------------------------
    # --------------------------------------------------
