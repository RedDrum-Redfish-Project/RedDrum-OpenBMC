
# Copyright Notice:
#    Copyright 2018 Dell, Inc. All rights reserved.
#    License: BSD License.  For full license text see link: https://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC/LICENSE.txt

from .obmcDbusInterfaces import  RdOpenBmcDbusInterfaces
from .obmcStaticConfig   import  RdOpenBmcStaticConfig

class RdOpenBmcDiscovery():
    def __init__(self,rdr):
        # got static Config Resource handle with the static IDs and config values 
        self.staticCfg=RdOpenBmcStaticConfig()

        # get instance of DbusInterfaces APIs
        self.dbus = RdOpenBmcDbusInterfaces(rdr)

        # initialize discovery dicts
        self.chassisDict={}
        self.managersDict={}
        self.systemsDict={}
        self.fansDict={}
        self.temperatureSensorsDict={}
        self.powerSuppliesDict={}
        self.voltageSensorsDict={}
        self.powerControlDict={}
        self.mgrNetworkProtocolDict={}
        self.mgrEthernetDict={}

    # --------------------------------------------------

    def discoverResourcesPhase1(self, rdr):
        #PHASE-1a:  
        rdr.logMsg("INFO","....discovery: running phase-1a.   adding Base Manager (BMC) resource")
        # Get BMC Manager info and create a Base Manager Entry for the BMC
        mgrBaseInfo = self.dbus.discoverObmcMgrBaseInfo()
        mgrEntry    = self.makeMgrBaseEntry(self.staticCfg.mgrId, mgrBaseInfo )
        if mgrEntry is not None:
            self.managersDict[self.staticCfg.mgrId] = mgrEntry

        #PHASE-1b:  
        rdr.logMsg("INFO","....discovery: running phase-1b.   adding Base Chassis resource")
        # Get Chassis info and create a Base Chassis Entry
        chasBaseInfo = self.dbus.discoverObmcChassisBaseInfo()
        chasEntry    = self.makeChassisBaseEntry(self.staticCfg.chasId, chasBaseInfo)
        if chasEntry is not None:
            self.chassisDict[self.staticCfg.chasId] = chasEntry

        
        #PHASE-1c:  
        rdr.logMsg("INFO","....discovery: running phase-1c.   adding Base System resource")
        # Get System info and create a Base System Entry 
        sysBaseInfo = self.dbus.discoverObmcSysBaseInfo()
        sysEntry    = self.makeSysBaseEntry(self.staticCfg.sysId, sysBaseInfo, chasBaseInfo)
        if sysEntry is not None:
            self.systemsDict[self.staticCfg.sysId] = sysEntry

        #PHASE-1d:  
        rdr.logMsg("INFO","....discovery: running phase-1d.   adding TempSensor resources")
        # Get TempSensor info and create  TempSensor entries for the chassisId
        tempSensorInfo  = self.dbus.discoverObmcTempSensorsInfo()
        tempSensorEntry = self.makeTempSensorsEntry(self.staticCfg.chasId, tempSensorInfo)
        if tempSensorEntry is not None:
            self.temperatureSensorsDict[self.staticCfg.chasId] = tempSensorEntry

        #PHASE-1e:  
        rdr.logMsg("INFO","....discovery: running phase-1e.   adding Fan resources")
        # Get Fans info and create Fan entries for the chassisId
        fanInfo   = self.dbus.discoverObmcFansInfo()
        fansEntry = self.makeFansEntry(self.staticCfg.chasId, fanInfo)
        if fansEntry is not None:
            self.fansDict[self.staticCfg.chasId] = fansEntry

        #PHASE-1f:  
        rdr.logMsg("INFO","....discovery: running phase-1f.   adding VoltageSensor resources")
        # Get VoltageSensor info and create  VoltageSensor entries for the chassisId
        voltageSensorInfo  = self.dbus.discoverObmcVoltageSensorsInfo()
        voltageSensorEntry = self.makeVoltageSensorsEntry(self.staticCfg.chasId, voltageSensorInfo)
        if voltageSensorEntry is not None:
            self.voltageSensorsDict[self.staticCfg.chasId] = voltageSensorEntry 

        #PHASE-1g:  
        rdr.logMsg("INFO","....discovery: running phase-1g.   adding PowerSupply resources")
        # Get PowerSupply info and create PowerSupply entries for the chassisId
        powerSuppliesInfo  = self.dbus.discoverObmcPowerSuppliesInfo()
        powerSuppliesEntry = self.makePowerSuppliesEntry(self.staticCfg.chasId, powerSuppliesInfo)
        if powerSuppliesEntry is not None:
            self.powerSuppliesDict[self.staticCfg.chasId] = powerSuppliesEntry
  
        #PHASE-1h:  
        rdr.logMsg("INFO","....discovery: running phase-1h.   adding PowerControl resources")
        # Get Power Control info and create PowerControl  entries for the chassisId
        powerControlInfo  = self.dbus.discoverObmcPowerControlInfo()
        powerControlEntry = self.makePowerControlEntry(self.staticCfg.chasId, powerControlInfo)
        if powerControlEntry is not None:
            self.powerControlDict[self.staticCfg.chasId] = powerControlEntry



        #PHASE-1i:  
        rdr.logMsg("INFO","....discovery: running phase-1k.   moving resources to the front-end cache databases")
        # now set the front-end databases to what we have discovered here in the backend
        # but note that at this point we are not saving these to the HDD cache
        # initialize the chassis databases

        #   --point the front-end chassis databases at the backend dicts we just generated
        rdr.logMsg("INFO","............discovery: setting chassis databases")
        rdr.root.chassis.chassisDb=self.chassisDict
        rdr.root.chassis.fansDb=self.fansDict
        rdr.root.chassis.tempSensorsDb=self.temperatureSensorsDict
        rdr.root.chassis.powerSuppliesDb=self.powerSuppliesDict
        rdr.root.chassis.voltageSensorsDb=self.voltageSensorsDict
        rdr.root.chassis.powerControlDb=self.powerControlDict

        #   --point the front-end managers databases at the backend dicts we just generated
        rdr.logMsg("INFO","............discovery: setting managers database")
        rdr.root.managers.managersDb=self.managersDict

        #   --point the front-end systems databases at the backend dicts we just generated
        rdr.logMsg("INFO","............discovery: setting systems database")
        rdr.root.systems.systemsDb=self.systemsDict


        #PHASE-1j:  
        rdr.logMsg("INFO","....discovery: running phase-1..   initialize volatile Dicts")

        #   --initialize the Chassis volatileDicts
        rdr.logMsg("INFO","............discovery: initializing Chassis VolatileDicts")
        rdr.root.chassis.initializeChassisVolatileDict(rdr)

        #   --initialize the Managers volatileDicts
        rdr.logMsg("INFO","............discovery: initializing Managers VolatileDicts")
        rdr.root.managers.initializeManagersVolatileDict(rdr)

        #   --initialize the Systems volatileDict
        rdr.logMsg("INFO","........system discovery: initializing Systems VolatileDict")
        rdr.root.systems.initializeSystemsVolatileDict(rdr)

        #PHASE-1k:  
        rdr.logMsg("INFO","....discovery: Phase1 complete")
        return(0)


    # Phase-2 discovery -- runs after Phase-1 discovery if  no errors
    #   Generally this is used to startup hw-monitors on separate threads
    #   For initial OpenBMC integration, nothing to do here
    def discoverResourcesPhase2(self, rdr):
        # nothing to do in phasae2
        return(0)


    # --------------------------------------------------
    # --------------------------------------------------
    # helper function used by makeXXXEntry() methods below
    #   if info=None, then we set all properties to None (json null)
    def loadPropsFromHwDiscovery(self, resp, props, info ):
        if info is None:
            info={}
        if (props is None) or (resp is None):
            return(9)
        for prop in props:
            if prop in info:
                resp[prop] = info[prop]
            else:
                resp[prop] = None
        return(0)

    # --------------------------------------------------
    # --------------------------------------------------
    # Create Base Chassis Db Entry for RedDrum OpenBMC
    def makeChassisBaseEntry(self, chasId, chasBaseInfo):
        resp=dict()
        resp["Name"]="Base Server Chassis"
        resp["ChassisType"]="RackMount"
        resp["Description"]="Base Chassis Enclosure for RackMount Server"
        resp["BaseNavigationProperties"]=["Thermal", "Power"]
        resp["ComputerSystems"]=[self.staticCfg.sysId]  
        resp["Manufacturer"]=self.staticCfg.sysManufacturer
        resp["Model"]=self.staticCfg.sysModel
        resp["PartNumber"]=self.staticCfg.sysPartNumber
        resp["ManagedBy"]=[self.staticCfg.mgrId]
        #resp["ContainedBy"]=    # not in baseServerProfile
        resp["CooledBy"]=[self.staticCfg.chasId]   # not in baseServerProfile
        resp["PoweredBy"]=[self.staticCfg.chasId]  # not in baseServerProfile
        #resp["Oem"]={}
        resp["Status"]={"State": "Enabled", "Health": "OK" }  # set Status as static value--it never changes
        resp["Volatile"]=["PowerState", "IndicatorLED"]     # properties we update from dbus on each get.
                                                            # PowerState is required, IndicatorLED recommended in BaseSvrProfile
        resp["Patchable"]=["IndicatorLED","AssetTag"]       # properties that can be written.   Recommended in BaseServerProfile
        resp["AssetTag"]=""                                 # init discoverytime asset tag to an empty string
        # properties to get from Dbus interface during discovery
        #    FYI-baseServerProfile requires we include EITHER:  PartNumber or SKU  here-currently RedDrum uses PartNumber
        propsFromHwDiscovery=["SerialNumber" ]
        self.loadPropsFromHwDiscovery(resp, propsFromHwDiscovery, chasBaseInfo )
        return(resp)

    # --------------------------------------------------
    # Create Base Manager Db Entry for RedDrum OpenBMC
    def makeMgrBaseEntry(self, mgrId, mgrBaseInfo ):
        resp=dict()
        resp["Name"]="OpenBMC"
        resp["Description"]="OpenBMC Baseboard Management Controller"
        resp["ManagerType"]="BMC"

        resp["Model"]=self.staticCfg.mgrModel
        resp["ManagerInChassis"]=self.staticCfg.chasId    # note: not required in BaseServerProfile
        resp["ManagerForChassis"]=[self.staticCfg.chasId]
        resp["ManagerForServers"]=[self.staticCfg.sysId]
        resp["Status"]={"State": "Enabled", "Health": "OK" }

        resp["SerialConsole"]= {"ServiceEnabled": self.staticCfg.serialConsoleEnabled, 
                                "ConnectTypesSupported": self.staticCfg.serialConsoleConnectTypesSupported }
        resp["CommandShell"] = {"ServiceEnabled": self.staticCfg.commandShellEnabled, 
                                "ConnectTypesSupported": self.staticCfg.commandShellConnectTypesSupported }

        resp["ActionsResetAllowableValues"]=["GracefulRestart","ForceRestart"]
        #resp["BaseNavigationProperties"]=["NetworkProtocol","EthernetInterfaces","LogServices"] # required in BaseServerProfile
        resp["BaseNavigationProperties"]=["NetworkProtocol","EthernetInterfaces"] # required in BaseServerProfile

        resp["GetDateTimeFromOS"]=True
        resp["GetServiceEntryPointUuidFrom"]="ServiceRoot"   # ServiceRoot | UUID 

        # properties that can be written.   
        resp["Patchable"]=["DateTime", "DateTimeLocalOffset"]   # Recommended in BaseServerProfile


        # get these properties from Dbus discovery
        propsFromHwDiscovery=["FirmwareVersion","UUID" ] # 
        self.loadPropsFromHwDiscovery(resp, propsFromHwDiscovery, mgrBaseInfo )
        if ("UUID" not in resp) or (resp["UUID"] is None):
            #if we couldnt get UUID from dbus, use the one from serviceRoot
            resp["GetUuidFromServiceRoot"]=True  # we will try to read BMC UUID from dbus
            if "UUID" in resp:
                del resp["UUID"]

        # ***ManagerNetworkProtocols
        managerNetworkProtocols = {
            "Name":  "OpenBMC Network Protocols",
            "HTTP":  {"Port": 80, "ProtocolEnabled": True},
            "HTTPS": {"Port": 443,"ProtocolEnabled": True },
            "SSH":   {"Port": 22, "ProtocolEnabled": True },
            #"NTP":   {},   # no NTP in BaseServer Profile
            "HostName": "",
            "FQDN": "",
            "Status": {"State": "Enabled", "Health": "OK"}
        }
        resp["NetworkProtocols"]= managerNetworkProtocols

        # *** EthernetInterfaces
        ipv4info=[{"Address": None, "SubnetMask": None, "Gateway": None, "AddressOrigin": None}]
        ethDeviceInfo = {
                "Name": "", "SpeedMbps": None, "HostName": "", "FQDN": "", "LinkStatus": None,
                "InterfaceEnabled": None, "FullDuplex": True, "AutoNeg": True,
                "MACAddress": None, "PermanentMACAddress": None, "IPv4Addresses": ipv4info
        }
        resp["EthernetInterfaces"] = { "eth1": ethDeviceInfo }

        return(resp)



    # --------------------------------------------------
    # Create System Db Entry for RedDrum OpenBMC
    def makeSysBaseEntry(self, sysId, sysBaseInfo, chasBaseInfo):
        resp=dict()
        resp["Name"]="Computer System"
        resp["Description"]="Computer System Base Resource"
        resp["SystemType"]="Physical"
        resp["Manufacturer"]=self.staticCfg.sysManufacturer
        resp["Model"]=self.staticCfg.sysModel
        resp["PartNumber"]=self.staticCfg.sysPartNumber
        resp["AssetTag"]=""                                 # init discoverytime asset tag to an empty string
        resp["Volatile"]=["PowerState", "IndicatorLED"]
        resp["ActionsResetAllowableValues"]=["On","ForceOff", "ForceRestart" ]
        resp["Patchable"]=["IndicatorLED", "AssetTag" ]

        resp["MemorySummary"]={"TotalSystemMemoryGiB": None }
        resp["ProcessorSummary"]={"Count": None,"Model": None }
        resp["Status"]={"State": "Enabled", "Health": "OK" }  # set Status as static value--it never changes
        resp["BootSourceVolatileProperties"]=["BootSourceOverrideEnabled","BootSourceOverrideTarget",
                                              "BootSourceOverrideMode", "UefiTargetBootSourceOverride" ]
        # Note: BootSourceOverrideMode is read recommended (not write)
        resp["BootSourceAllowableValues"]=["None","Pxe","Hdd","BiosSetup"] #xg555
        resp["Chassis"]=self.staticCfg.chasId
        resp["ManagedBy"]=[ self.staticCfg.mgrId ]
 
        # LogServices    ReadRequirement Recc

        # use the processor summary from discovered system Info
        if "ProcessorSummary" in sysBaseInfo and "ProcessorSummary" in resp:
            propsFromSysDiscovery=["Count", "Model"]
            self.loadPropsFromHwDiscovery(resp["ProcessorSummary"], propsFromSysDiscovery, 
                                       sysBaseInfo["ProcessorSummary"] )

        # use the Memory summary from discovered system Info
        if "MemorySummary" in sysBaseInfo and "MemorySummary" in resp:
            propsFromSysDiscovery=["TotalSystemMemoryGiB" ]
            self.loadPropsFromHwDiscovery(resp["MemorySummary"], propsFromSysDiscovery, 
                                       sysBaseInfo["MemorySummary"] )

        # use the SerialNumber discovered via Chassis Info 
        propsFromChasDiscovery=["SerialNumber"]
        self.loadPropsFromHwDiscovery(resp, propsFromChasDiscovery, chasBaseInfo )

        # add other System Properties 
        propsFromSysDiscovery=["BiosVersion", "UUID"]
        self.loadPropsFromHwDiscovery(resp, propsFromSysDiscovery, sysBaseInfo )

        if ("UUID" not in resp) or (resp["UUID"] is None):
            #if we couldnt get UUID from dbus via discoverObmcSysBaseInfo(), so use the one from serviceRoot
            resp["GetUuidFromServiceRoot"]=True  # RedDrum will use the self-generated RedDrum UUID for the system UUID
            if "UUID" in resp:
                del resp["UUID"]

        return(resp)

    # --------------------------------------------------
    # Create Temp Sensor Db Entries for RedDrum OpenBMC
    # where discoverObmcTempSensorsInfo() returned a dict of temp sensors
    #   tempSensorInfo = { "Id": 
    #        { "<tempSensorId0>": { "Name": <name>,"SensorNumber": <sn>,"PhysicalContext": <pc>,"Status": <status>,
    #                                  "MinReadingRange": <minrr>, "MaxReadingRange": <maxrr>,"AddRelatedItems": <related> } }
    #        { "<tempSensorId1>": { ... }
    #     }
    def makeTempSensorsEntry(self, chasId, tempSensorInfo):
        sensorPropsFromHw=["SensorNumber", "UpperThresholdNonCritical", "LowerThresholdNonCritical", "UpperThresholdCritical",
                                "LowerThresholdCritical", "MinReadingRange", "MaxReadingRange" ]
        resp=dict()
        if "Id" not in tempSensorInfo:
            return(resp)
        resp["Id"]={}

        # create Intake/Inlet sensor
        if "Intake" in tempSensorInfo["Id"]:
            resp["Id"]["Intake"]={}
            resp["Id"]["Intake"]["Name"] = "Intake Temp"
            resp["Id"]["Intake"]["PhysicalContext"] = "Intake"
            resp["Id"]["Intake"]["Volatile"] = [ "ReadingCelsius" ]
            resp["Id"]["Intake"]["AddRelatedItems"] = ["System","Chassis"]
            resp["Id"]["Intake"]["Status"] =  {"State": "Enabled", "Health": "OK" }

            self.loadPropsFromHwDiscovery(resp["Id"]["Intake"], sensorPropsFromHw, tempSensorInfo["Id"]["Intake"] )
            resp["Id"]["Intake"]["Volatile"]=["ReadingCelsius"]

        # create Board Temp sensor
        if "Board" in tempSensorInfo["Id"]:
            resp["Id"]["Board"]={}
            resp["Id"]["Board"]["Name"] = "Board Temp"
            resp["Id"]["Board"]["PhysicalContext"] = "SystemBoard"
            resp["Id"]["Board"]["Volatile"] = [ "ReadingCelsius" ]
            resp["Id"]["Board"]["AddRelatedItems"] = ["System","Chassis"]
            resp["Id"]["Intake"]["Status"] =  {"State": "Enabled", "Health": "OK" }

            self.loadPropsFromHwDiscovery(resp["Id"]["Board"], sensorPropsFromHw, tempSensorInfo["Id"]["Board"] )
            resp["Id"]["Board"]["Volatile"]=["ReadingCelsius"]

        # create CPU1 Temp sensor
        if "CPU1" in tempSensorInfo["Id"]:
            resp["Id"]["CPU1"]={}
            resp["Id"]["CPU1"]["Name"] = "CPU1 Temp"
            resp["Id"]["CPU1"]["PhysicalContext"] = "CPU"
            resp["Id"]["CPU1"]["Volatile"] = [ "ReadingCelsius" ]
            resp["Id"]["CPU1"]["AddRelatedItems"] = ["System", "Processor" ]
            resp["Id"]["Intake"]["Status"] =  {"State": "Enabled", "Health": "OK" }

            self.loadPropsFromHwDiscovery(resp["Id"]["CPU1"], sensorPropsFromHw, tempSensorInfo["Id"]["CPU1"] )
            resp["Id"]["CPU1"]["Volatile"]=["ReadingCelsius"]

        # create CPU2 Temp sensor
        if "CPU2" in tempSensorInfo["Id"]:
            resp["Id"]["CPU2"]={}
            resp["Id"]["CPU2"]["Name"] = "CPU2 Temp"
            resp["Id"]["CPU2"]["PhysicalContext"] = "CPU"
            resp["Id"]["CPU2"]["Volatile"] = [ "ReadingCelsius" ]
            resp["Id"]["CPU2"]["AddRelatedItems"] = ["System", "Processor" ]
            resp["Id"]["Intake"]["Status"] =  {"State": "Enabled", "Health": "OK" }

            self.loadPropsFromHwDiscovery(resp["Id"]["CPU2"], sensorPropsFromHw, tempSensorInfo["Id"]["CPU2"] )
            resp["Id"]["CPU2"]["Volatile"]=["ReadingCelsius"]

        return(resp)


    # --------------------------------------------------
    # Create Fan Db Entries for RedDrum OpenBMC
    # fansInfo={"MaxNumOfFans": <max>, "MinNumOfFans": <min>,  
    #           "Id":  "<fanId0>":  # where "<fanId0>" is "0", "<fanId1>" is "1", etc
    #                  { "ReadingUnits": "RPM", "MinReadingRange": 0, "MaxReadingRange": 4000, LowerThresholdCritical": 16 }
    #                  "<vanId1>": { ... }
    #           "ReduncancyGroup": "0": {...}
    def makeFansEntry(self, chasId, fanInfo):
        resp=dict()

        if fanInfo is None:
            fanInfo={}
        resp=dict()
        resp["Id"]={}
        resp["RedundancyGroup"]={}
        if "Id" in fanInfo:
            # first fill-in the array of all Fans as absent
            for fanId in fanInfo["Id"]:
                entryData={}
                entryData["Volatile"]=["Reading" ]
                entryData["ReadingUnits"]="RPM"
                entryData["MinReadingRange"]=None
                entryData["MaxReadingRange"]=None
                entryData["LowerThresholdCritical"]=None
                entryData["RedundancyGroup"]="0"
                entryData["Name"]="Fan"+fanId
                entryData["PhysicalContext"]="Backplane"
                entryData["Status"]={"State": "Absent", "Health": None }
                resp["Id"][fanId]=entryData

            # iterate through the array of fan entries returned, 
            #    and update entry w/ data returned from dbus
            fanPropertyList=["MinReadingRange","MaxReadingRange","LowerThresholdCritical",]
            for psuId in fanInfo["Id"]:
                if "Status" in fanInfo["Id"][psuId]:
                    resp["Id"][fanId]["Status"]=fanInfo["Id"][fanId]["Status"]    

                for prop in fanPropertyList:
                    if prop in fanInfo["Id"][fanId]:
                        resp["Id"][fanId][prop]=fanInfo["Id"][fanId][prop]

            # set all fans in same redundancy group "0"
            # xg later if redundancy on/off is supported this will change
            if True:
                redundancyGroupId="0"
                entryData={}
                entryData["Name"]="Shared Chassis Fans"
                entryData["Mode"]="N+m"
                entryData["Status"]={"State": "Enabled", "Health": "OK" }
                if "MinNumOfFans" in fanInfo:
                    entryData["MinNumNeeded"]=fanInfo["MinNumOfFans"]
                else:
                    entryData["MinNumNeeded"]=None
                if "MaxNumOfFans" in fanInfo:
                    entryData["MaxNumSupported"]= fanInfo["MaxNumOfFans"]
                else:
                    entryData["MaxNumSupported"]=None

                resp["RedundancyGroup"][redundancyGroupId]=entryData
        return(resp)


    # --------------------------------------------------
    # Create Voltage Sensor Db Entry for RedDrum OpenBMC
    # where discoverObmcVoltageSensorsInfo() returned a dict of voltage sensors
    #   voltageSensorInfo = { "Id": 
    #        { "<voltageSensorId0>": { "Name": <name>,"SensorNumber": <sn>,"PhysicalContext": <pc>,"Status": <status>,
    #                                  "MinReadingRange": <minrr>, "MaxReadingRange": <maxrr>,"AddRelatedItems": <related> } }
    #        { "<voltageSensorId1>": { ... }
    #     }
    def makeVoltageSensorsEntry(self, chasId, voltageSensorInfo):
        if voltageSensorInfo is None:
            return(None)
        resp=dict()
        propsFromHwDiscovery=["Name","SensorNumber","PhysicalContext","Status","MinReadingRange", "MaxReadingRange","AddRelatedItems"]
        resp["Id"]={}
        if "Id" in voltageSensorInfo:
            for voltageSensorId in voltageSensorInfo["Id"]:
                resp["Id"][voltageSensorId]={}
                self.loadPropsFromHwDiscovery(resp["Id"][voltageSensorId], propsFromHwDiscovery, voltageSensorInfo["Id"][voltageSensorId] )
                resp["Id"][voltageSensorId]["Volatile"]=["ReadingVolts"]
        return(resp)

    # --------------------------------------------------
    # Create PowerSupply Db Entries for RedDrum OpenBMC
    # powerSuppliesInfo={ "MaxNumOfPsus": <max>, "MinNumOfPsus": <min>,  
    #                     "Id": "<psuId0>": 
    #                           { "PsuNum": <psunum>, "PowerSupplyType": "<type>", "LineInputVoltageType": "<livt>", 
    #                             "PowerCapacityWatts": <watts>, "SerialNumber": "<sn>",  
    #                             "Status": {"State": "<status>", "Health": <health> }  
    #                           }, 
    #                           <psuId1>: { ... }
    #                     "RedundancyGroup": "0": { ... }
    #                   }
    def makePowerSuppliesEntry(self, chasId, powerSuppliesInfo):
        if powerSuppliesInfo is None:
            powerSuppliesInfo={}
        resp=dict()
        resp["Id"]={}
        resp["RedundancyGroup"]={}
        if "Id" in powerSuppliesInfo:
            # first fill-in the array of all PowerSupplies as absent
            for psuId in powerSuppliesInfo["Id"]:
                entryData={}
                entryData["Volatile"]=["LineInputVoltage", "LastPowerOutputWatts"]
                entryData["RedundancyGroup"]="0"
                entryData["Name"]="Psu"+psuId
                entryData["PowerSupplyType"]=None
                entryData["LineInputVoltageType"]=None
                entryData["PowerCapacityWatts"]=None
                entryData["SerialNumber"]=None
                entryData["Status"]={"State": "Absent", "Health": None }
                resp["Id"][psuId]=entryData

            # iterate through the array of powerSupply entries returned, 
            #    and update entry w/ data returned from dbus
            psuPropertyList=["PowerSupplyType", "LineInputVoltageType", "PowerCapacityWatts", "SerialNumber"]
            for psuId in powerSuppliesInfo["Id"]:
                if "Status" in powerSuppliesInfo["Id"][psuId]:
                    resp["Id"][psuId]["Status"]=powerSuppliesInfo["Id"][psuId]["Status"]    

                for prop in psuPropertyList:
                    if prop in powerSuppliesInfo["Id"][psuId]:
                        resp["Id"][psuId][prop]=powerSuppliesInfo["Id"][psuId][prop]

            # set all powersupplies in same redundancy group "0"
            # xg later if redundancy on/off is supported this will change
            if True:
                redundancyGroupId="0"
                entryData={}
                entryData["Name"]="Shared PowerSupplies"
                entryData["Mode"]="N+m"
                entryData["Status"]={"State": "Enabled", "Health": "OK" }
                if "MinNumOfPsus" in powerSuppliesInfo:
                    entryData["MinNumNeeded"]=powerSuppliesInfo["MinNumOfPsus"]
                else:
                    entryData["MinNumNeeded"]=None
                if "MaxNumOfPsus" in powerSuppliesInfo:
                    entryData["MaxNumSupported"]= powerSuppliesInfo["MaxNumOfPsus"]
                else:
                    entryData["MaxNumSupported"]=None

                resp["RedundancyGroup"][redundancyGroupId]=entryData
        return(resp)

    # --------------------------------------------------
    # Create PowerControl Db Entries for RedDrum OpenBMC
    def makePowerControlEntry(self, chasId, powerControlInfo):
        # create the base MemberId-0 PowerControl Entry -- the MAIN server power control resource
        resp=dict()
        resp["Id"]={}
        resp0=dict()
        resp0["Name"]="Chassis_Power_Control"
        resp0["PhysicalContext"]="Chassis"
        resp0["Patchable"]=["LimitInWatts","LimitException"]
        resp0["Volatile"]=["PowerConsumedWatts"]
        resp0["LimitInWatts"]=None
        resp0["LimitException"]=None

        # set Base nonVol resources read from dBus
        propsFromHwDiscovery=["PowerCapacityWatts" ] 
        self.loadPropsFromHwDiscovery(resp0, propsFromHwDiscovery, powerControlInfo )

        # load the main power control resource into PowerControl Db as index "0"
        resp["Id"]["0"] = resp0
        return(resp)

        
    # --------------------------------------------------

