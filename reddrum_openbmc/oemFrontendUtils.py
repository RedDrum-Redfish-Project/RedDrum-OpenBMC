
# Copyright Notice:
#    Copyright 2018 Dell, Inc. All rights reserved.
#    License: BSD License.  For full license text see link: https://github.com/RedDrum-Redfish-Project/RedDrum-Frontend/LICENSE.txt

# OEM-specific ID construction and interpretation utilities
# NOTE:
#  in Redfish, it is generally not safe for a client to construct of assume construction of a URI
#  However, the RedDrum fronend interprets some IDs loaded during discovery for some response construction.
#  These OEM utilities contain any special rules re interpreting IDs 

import re

class FrontendOemUtils():
    def __init__(self,rdr):
        self.rdr=rdr
        self.dellEsiUtils=self.DellESI_FrontendOemUtils(rdr)
        # enter other company/group oem utilities here


    class DellESI_FrontendOemUtils():
        def __init__(self,rdr):
            self.rdr=rdr

        def rsdLocation(self, chassid):
            idRule = self.rdr.backend.rdBeIdConstructionRule
            #   valid rdBeIdConstructionRule values are:  "Monolythic", "Dss9000", "Aggregator"
            chas=None
            rid=None
            if(idRule=="Dss9000"):
                pass
            elif (idRule=="Monolythic"):
                rid=chassid
                parent=None
            elif (idRule=="Aggregator"):
                rid=chassid
                parent=None
                if chassid in self.rdr.root.chassis.chassisDb:
                    if "ContainedBy" in self.rdr.root.chassis.chassisDb[chassid]:
                        parent = self.rdr.root.chassis.chassisDb[chassid]["ContainedBy"]
            return( rid, parent)

    # create class for other oem utils here

