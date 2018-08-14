
# Copyright Notice:
#    Copyright 2018 Dell, Inc. All rights reserved.
#    License: BSD License.  For full license text see link: https://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC/LICENSE.txt

# Backend root class for OpenBMC
import os
import json
import inspect
from .chassisBackend   import RdChassisBackend
from .managersBackend  import RdManagersBackend
from .systemsBackend   import RdSystemsBackend

from .obmcDiscovery    import RdOpenBmcDiscovery
from .oemFrontendUtils import FrontendOemUtils


class RdBackendRoot():
    def __init__(self,rdr):
        # initialize data
        self.version = "0.9"
        self.backendStatus=0
        self.discoveryState = 0
        self.oemUtils=FrontendOemUtils(rdr)
        self.rdBeIdConstructionRule = "Monolythic"
        #   valid rdBeIdConstructionRule values are:  "Monolythic", "Dss9000", "Aggregator"

        self.rdr = rdr

        # create backend sub-classes
        self.createSubObjects(rdr)

        # run startup tasks
        self.startup(rdr)

    def createSubObjects(self,rdr):
        #create subObjects that implement backend APIs
        self.chassis=RdChassisBackend(rdr)
        self.managers=RdManagersBackend(rdr)
        self.systems=RdSystemsBackend(rdr)
        self.backendStatus=1
        return(0)


    def startup(self,rdr):
        # set the data paths for OpenBMC 
        rdSvcPath=os.getcwd()

        #rdr.baseDataPath=os.path.join(rdSvcPath, "reddrum_frontend", "Data")
        # note:  rdr.frontEndDirPath is the path to  reddrum_frontend
        rdr.baseDataPath=os.path.join(rdr.frontEndPkgPath,"Data")
        print("EEEEEEEE: baseDataPath: {}".format(rdr.baseDataPath))

        # xg44 FIX final paths for OpenBMC /var and /etc...
        rdr.varDataPath=os.path.join("/var", "www", "rf")
        print("EEEEEEEE: varDataPath: {}".format(rdr.varDataPath))

        # if we have a RedDrum.conf file in etc/ use it. otherwise use the default
        #rdr.RedDrumConfPath=os.path.join(rdSvcPath, "RedDrum.conf" )
        redDrumConfPathEtc=os.path.join("/etc",  "RedDrum.conf" )
        redDrumConfPathFrontend=os.path.join(rdr.frontEndPkgPath, "RedDrum.conf")
        if os.path.isfile(redDrumConfPathEtc):
            rdr.RedDrumConfPath=redDrumConfPathEtc
        else:
            rdr.RedDrumConfPath=redDrumConfPathFrontend
        print("EEEEEEEE: RedDrumConfPath: {}".format(rdr.RedDrumConfPath))

        # set path to schemas -- not used now
        rdr.schemasPath = os.path.join(rdSvcPath, "schemas") #not used now

        # set path to bash scripts to run to get data from Linux
        #self.obmcScriptsPath = os.path.join(rdSvcPath, "reddrum_openbmc" )
        self.obmcScriptsPath = os.path.dirname( inspect.getfile(RdBackendRoot))
        print("EEEEEEEE: obmcScriptsPath: {}".format(self.obmcScriptsPath))

        # not that syslog logging is enabled on OpenBMC by default unless -L (isLocal) option was specified
        # turn-on console messages also however
        # xg44 FIX turnoff console msg 
        rdr.printLogMsgs=True

        # OpenBMC uses dynamic discovery and no persistent cache database files
        # rdr.rdProfile may point to different configs supported during dynamic discovery
        rdr.useCachedDiscoveryDb=False
        rdr.useStaticResourceDiscovery=False

        self.backendStatus=2
        return(0)


    # runStartupDiscovery is called from RedDrumMain once both the backend and frontend resources have been initialized
    #   it will discover resources and then kick-off any hardware monitors in separate threads
    def runStartupDiscovery(self, rdr):
        # For OpenBMC, Discovery calls a customizable discovery based on the rdr.rdProfile setting
        rdr.logMsg("INFO"," ....Launching Startup Discovery based on Config Profile: {}".format(rdr.rdProfile))

        discvr=RdOpenBmcDiscovery(rdr)

        # Do Phase-1 Discovery -- add Managers, Chassis, and Systems Resources
        rc=discvr.discoverResourcesPhase1(rdr)
        if( rc != 0):
            self.discoveryState = 1001 # failed trying to discover resources
            rdr.logMsg("ERROR"," ..ERROR: Resource Discovery Phase-1 Failed rc={}. Aborting discovery".format(rc))
            return(rc)

        self.discoveryState = 1
        rdr.logMsg("INFO"," ....Resource Discovery Phase-1 Complete. Starting Phase-2 Discovery")

        # Do Phase-2 Discovery -- start HwMonitors if running any in background
        # phase2 discovery just returns 0 if there are no monitors running
        rc=discvr.discoverResourcesPhase2(rdr)
        if( rc != 0):
            self.discoveryState = 1002 # failed trying to discover resources
            rdr.logMsg("ERROR"," ..ERROR: Resource Discovery Phase-2 Failed rc={}. Aborting discovery".format(rc))
            return(rc)

        rdr.logMsg("INFO"," ....Resource Discovery Phase-2 Complete. ")

        return(rc)




    # Backend APIs  
    # POST to Backend
    def postBackendApi(self, request, apiId, rdata):
        # handle backend auth based on headers in request
        # handle specific post request based on apiId and rdata
        rc=0
        statusCode=204
        return(rc,statusCode,"","",{})

    # GET from  Backend
    def getBackendApi(self, request, apiId):
        # handle backend auth based on headers in request
        # handle specific post request based on apiId and rdata
        rc=0
        resp={}
        jsonResp=(json.dumps(resp,indent=4))
        statusCode=200
        return(rc,statusCode,"",jsonResp,{})




