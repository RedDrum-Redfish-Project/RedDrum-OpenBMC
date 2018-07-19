
# Copyright Notice:
#    Copyright 2018 Dell, Inc. All rights reserved.
#    License: BSD License.  For full license text see link: https://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC/LICENSE.txt

class RdOpenBmcDbusInterfaces():
    def __init__(self,rdr):
        # define static Ids
        self.rdr = rdr
        self.stub = rdr.enableBackendStubs
        #self.stub=False     # stub=False once we have real Dbus code
        #self.stub=True      # comment this line out for real code
        if self.stub is False:
            from .process import ProcessDbus as PDbus
            self.ProcDbus = PDbus()

    # --------------------------------------------------
    # --------------------------------------------------
    # Base Manager  Discovery and update APIs
    # 0.9
    # do DBUS query to get non-volatile discovery-time info for the Base Manager /BMC
    #    returns: None if error
    #    returns: resp={ "FirmwareVersion": "<fwverString>", "UUID": "<uuid>" }  
    #            where <fwverString> is a string indicating the BMC Firmware version
    #            where uuid is in std uuid format: ffffffff-ffff-ffff-ffff-ffffffffffff
    #            (( if uuid is not available in this format, we can convert here ))
    #        IF OpenBMC has a UUID defined for the BMC (different from the system UUID), put it here.   
    #        otherwise, leave it out and higher-level code will use the one generated for the redfish service
    #        resp["UUID"]="ffffffff-ffff-ffff-ffff-fffffffffffx"   # a string in uuid format w/ BMC uuid
    def discoverObmcMgrBaseInfo(self):
        resp=dict()
        # get the properties
        if( self.stub is True):
            resp["FirmwareVersion"]="0.9.9"   # a string indicating the obmc FW version
        else:
            resp["FirmwareVersion"]=self.ProcDbus.get_bmc_fw_ver()   # a string indicating the obmc FW version

        return(resp)


    # get Manager volatile property: Status/Health from Dbus on-demand query for Get Manager API
    #    returns: None if error
    #    returns: resp="<mgrHealthEnum>"   if no error
    #         where <mgrHealthEnum> is a string enum oneOf:  "OK", "Warning", "Critical"
    def getObmcMgrStatusHealth(self):
        if( self.stub is True):
            resp="OK" 
        else:
            resp="OK"  

        return(resp)



    # Reset Manager via Dbus from on-demand POST Manager Reset API
    #    returns: neg number if error,  0 if success
    #    request parameters are: <resetType> which is a string enum oneOf: "ForceRestart", "GracefulRestart" 
    #        implementation must support ForceRestart.   goal is to support the soft reset GracefulRestart also
    def resetObmcMgr(self, resetType):
        if( self.stub is True):
            if resetType == "ForceRestart":
                # do a Hard Reset
                print("Reset BMC: HARD")
                sys.stdout.flush()
            elif resetType == "GracefulRestart":
                # do a graceful shutdown and then restart
                print("Reset BMC: SOFT - Graceful")
                sys.stdout.flush()
            else:
                return(-9) # resetType not supported
        else:
            if resetType == "ForceRestart":
                # do a Hard Reset
                self.ProcDbus.reset_bmc()
            elif resetType == "GracefulRestart":
                # do a graceful shutdown and then restart
                self.ProcDbus.reset_bmc()
            else:
                return(-9) # resetType not supported
        return(0)


    # --------------------------------------------------
    # --------------------------------------------------
    # Base Chassis Discovery and update functions
    #
    # do DBUS query to get non-volatile discovery-time info for the Base Chassis
    # returns: None if error
    # returns: resp={"SerialNumber": "<string" }
    #
    def discoverObmcChassisBaseInfo(self):
        resp=dict()
        if( self.stub is True):
            resp["SerialNumber"]="G33GRW66x"
        else:
            resp["SerialNumber"]=self.ProcDbus.get_chassis_SerialNum()
        return(resp)

    # get chassis volatile property: PowerState from Dbus on-demand query for GET chassis API
    #    returns: None if error
    #    returns: resp="<pwrStateEnumString>" string enum if no error
    #        where <pwrStateEnumString> is oneOf: "On", "Off", "PoweringOn", "PoweringOff" (On and Off required)
    #        implementation should support On, Off.    PoweringOn, PoweringOff is used only in special case
    def getObmcChassisPowerState(self):
        if( self.stub is True):
            resp="On"
        else:
            resp=self.ProcDbus.get_chassis_state()
        return(resp)

    # get chassis property: AssetTag from Dbus on-demand query for GET chassis API
    #    returns: None if error
    #    returns: resp="<assetTag>"  string if no error
    #        where <assetTag> is a string
    def getObmcAssetTag(self):
        if( self.stub is True):
            resp="OCPLab1"
        else:
            resp=self.ProcDbus.get_chassis_asset_tag()
        return(resp)


    # get chassis volatile property: IndicatorLED from Dbus on-demand query for GET chassis API
    #    returns: None if error
    #    returns: resp={"IndicatorLED": "<ledStateEnumString>" }
    #        where <ledStateEnujmString> is oneOf: "Lit", "Off", "Blinking"   
    #        implementation should support Off and can support both or just one of Lit and Blinking
    def getObmcChassisIndicatorLED(self):
        if( self.stub is True):
            resp="Blinking"
        else:
            resp=self.ProcDbus.get_chassis_ID_LED()
        return(resp)


    # 
    # SET the chassis IndicatorLED via Dbus on-demand operation from PATCH chassis API or PATCH system API
    #    returns: neg number if error,  0 if success
    #    request parameters are: <ledStateEnumString> which is a string enum oneOf: "Lit", "Off", "Blinking"   
    #        implementation should support Off and can support both or just one of Lit and Blinking
    def setObmcChassisIndicatorLed(self, ledStateEnum):
        validHwLedStates=["Off","Lit","Blinking"]
        if ledStateEnum not in validHwLedStates:
            return(-9)
        if( self.stub is True):
            print("set chassis LED: {}".format(ledStateEnum))
            sys.stdout.flush()
        else:
            if ledStateEnum == "Off":
                self.ProcDbus.deassert_chassis_ID_LED()
            else:
                self.ProcDbus.assert_chassis_ID_LED()
        return(0)

    # set chassis  AssetTag from Dbus 
    #    returns: neg num if error
    #    returns: 0 if no error
    #    request properties:  <assetTag>   a string
    #        where <assetTag> is a string
    def setObmcAssetTag(self,assetTag):
        if( self.stub is True):
            print("set chassis AssetTag")
            sys.stdout.flush()
        else:
            self.ProcDbus.set_chassis_asset_tag(assetTag)
        return(0)


    # --------------------------------------------------
    # Power Control Discovery and update APIs
    #
    # do DBUS query to get non-volatile discovery-time info for the Chassis Power Control
    #    returns: None if error
    #    returns: resp={ "PowerCapacityWatts": <capacity>  }
    #            where <capacity> is a json number that represents the max power capacity available 
    #                 eg max output power of all PSUs or max budgeted
    def discoverObmcPowerControlInfo(self):
        resp=dict()
        if( self.stub is True):
            resp["PowerCapacityWatts"]=850
        else:
            resp["PowerCapacityWatts"]=850  #xg44 integration not complete
        return(resp)


    # read the current server Power Draw Reading
    # This is equiv to DCMI GetPowerReading.  It is the total server Power draw from wall socket in Watts
    #    returns:  neg number if error
    #    returns:  integer representing the <currentPowerDrawInWatts> if no error
    #        where <currentPowerDrawInWatts> is integer power consumption in watts
    def getObmcPowerReading(self):
        if( self.stub is True):
            resp=409
        else:
            resp=self.ProcDbus.get_chassis_power_reading()
        return(resp)

    # read the settable powerLimit
    #    returns:  neg number if error
    #    returns:  integer representing the <powerLimitInWatts> if no error
    #        where <powerLimitInWatts> is integer in watts
    def getObmcPowerLimit(self):
        if( self.stub is True):
            resp=459
        else:
            resp=self.ProcDbus.get_chassis_power_limit()
        return(resp)


    # read settable power limiting Exception setting
    #    returns: None if error
    #    returns: resp="<exceptionEnumString>" if no error
    #            where <exceptionEnumString> is a string enum OneOf: "NoAction", "LogEventOnly", "HardPowerOff".     
    #                   for obmc, support NoAction or LogEventOnly 
    def getObmcPowerLimitException(self):
        if( self.stub is True):
            resp="LogEventOnly"
        else:
            resp="LogEventOnly"  # xg44 need to complete integration
        return(resp)


    # set chassis PowerLimit via Dbus on-demand query for Patch Chassis Power API
    #    returns: neg number if error,  0 if success
    #    request parameters are: <powerLimit> which is an integer number in watts
    #             if <powerLimit> is set to either None or 0, then powerLimiting is turned off
    def setObmcPowerLimit(self, powerLimit ):
        if( self.stub is True):
            if powerLimit is None or powerLimit == 0:
                # turn-off power limiting *****
                print("set Power Limit OFF")
                sys.stdout.flush()
                return(0)
            else:
                # set the power limit to value <powerLimit> in watts
                print(" setting PowerLimit to {} watts".format(powerLimit))
                sys.stdout.flush()
                return(0)
        else:
            if powerLimit is None:
                powerLimit=0
            #xg55 does 0 turn-off power limiting?
            self.ProcDbus.set_chassis_power_limit(powerLimit)
            return(0)

    # set chassis PowerLimit Exception Action via Dbus on-demand query for Patch Chassis Power API
    #    returns: neg number if error,  0 if success
    #    request parameters are: <powerLimitException> which is a stringEnum
    #           <powerLimitException> values = oneOf:  "NoAction", "LogEventOnly", "HardPowerOff".     
    #               obmc support:    LogEventOnly or NoAction 
    def setObmcPowerLimitException(self, powerLimitException ):
        validPowerLimitExceptionValues=[None,"NoAction", "LogEventOnly", "HardPowerOff" ]
        if powerLimitException not in validPowerLimitExceptionValues:
            return(-9)
        if( self.stub is True):
            if powerLimitException is None:
                print("set Power Limit Exception to default LogEventOnly")
            else:
                print("setting PowerLimitException to {}".format(powerLimitException)) 
            sys.stdout.flush()
        else:
            # xg44 need to complete integration
            if powerLimitException is None:
                print("set Power Limit Exception to default LogEventOnly")
            else:
                print("setting PowerLimitException to {}".format(powerLimitException)) 
            sys.stdout.flush()
        return(0)


    # --------------------------------------------------
    # Power Supply Discovery and update APIs
    #
    # do DBUS query to get non-volatile discovery-time info for the Power Supplies
    #    returns: None if error
    #    returns: resp={ "MaxNumOfPsus": <maxPsus>, 
    #                    "MinNumOfPsus": <minPsus>,     # min # of psus required to work with the current redundancy config
    #                    "Id": {
    #                        "0": {
    #                               "PowerSupplyType": "<type>",   "LineInputVoltageType": "<inputVoltageType>",   
    #                               "PowerCapacityWatts": <capacity>,     "SerialNumber": "<serialnum>", 
    #                               "Status": {"State": "<statusState>", "Health": "<statusHealth>" },
    #                             },
    #                        "1": { 
    #                            ...second supply ... 
    #                             },
    #                        "<psuId-n>": {
    #                             }
    #                   }
    #        where <maxPsus> is an integer representing the number of supported PSUs for the system (typically 2)
    #        where <minPsus> is an integer representing the min number of PSUs to run the system 
    #             (assuming there may be redundancy) (typ 1)
    #
    #        then there is a dictionary entry for each PowerSupply referenced by "Id"[<psuId>]:
    #          where <Id> is a string of form:   "0", "1", "2", ... indicating the Id of the psu
    #          <type>  is a string enum anyOf: "AC", "DC", or "ACorDC"   
    #          <inputVoltageType> is a string enum anyof: AC120V","AC240V","AC277V", "ACandDCWideRange",
    #                    "DCNeg48V","DC380V", "ACWideRange", "DC240V"
    #          <capacity> is an int indicating the faceplate max output power of the PowerSupply
    #          <serialnum> is a string holding the specific powerSupply serial number
    #          <statusState>  is oneOf: "Enabled","Disabled", "Absent", "Updating"  -- return Absent if powerSupply is removed
    #                         if the powerSupply is turned-off, set to "Disabled".   If turned-On, set to "Enabled"
    #                         If one is absent, set to "Absent".     
    #          <statusHealth> is oneOf:  "OK","Warning", "Critical"
    #                         if normal, set to OK.   Warning would indicate an error condition eg input voltage low.
    #                         if powerSupply indicates it has failed, set to Critical here
    #           if a psu is Absent, the properties other than State would be returned = None
    def discoverObmcPowerSuppliesInfo(self):
        resp=dict()
        resp["Id"]={}

        # get the number of PSUs that the chassis/system supports -- usually 2 for a monolythic server
        # and the minumum number of supplies required.
        #    this is used by redfish service to indicate the min number required if redundanct supplies eg N+1 sparing is used
        #    if maxNumOfPsus==2, and redundancy is enabled in the server,  minNumOfPsus=1.
        #    it is possible that some configs might be non-redundant and require 2 supplies--in which case minNumOfPsus=2
        if( self.stub is True):
            psuNums = {"MaxNumOfPSUs": 2, "MinNumOfPSUs": 1,  "PSU0present": True, "PSU1present": True   }
        else:
            psuNums = self.ProcDbus.get_psu_nums()

            # xg44 fix for case where psuNums is not returning PSU1present or PSU2present yet
            # xg44 the below code needs to be replaced with psuNums just including PSU1present and PSU2present properties
            psuNums["PSU0present"]=False
            psuNums["PSU1present"]=False
            if "PSU0present" not in psuNums:
                if ("PresNumOfPSUs" in psuNums) and (psuNums['PresNumOfPSUs'] > 0):
                    psuNums["PSU0present"]=True
            if "PSU1present" not in psuNums:
                if ("PresNumOfPSUs" in psuNums) and (psuNums['PresNumOfPSUs'] > 1):
                    psuNums["PSU1present"]=True

        maxNumOfPsus=psuNums['MaxNumOfPSUs']  
        minNumOfPsus=psuNums['MinNumOfPSUs']  
        psu0present=psuNums['PSU0present']
        psu1present=psuNums['PSU1present']

        # save the max and min PSUs in the response
        resp["MaxNumOfPsus"] = maxNumOfPsus
        resp["MinNumOfPsus"] = minNumOfPsus

        # loop maxNumOfPsus querying dbus to get discovery info about any PSUs present
        #    if a PSU is absent, we state it is absent here, and the other info is python None (which maps to Json null)
        for psuNum in range(0, maxNumOfPsus):    # psu is 0, 1, ... up to maxNumOfPsus-1
            # create an empty dict for this psu and generate the psuId
            psuEntry=dict()   
            psuId = str(psuNum)
            psuEntry["Status"] = {} 

            # check if the psu is present
            if psuNum==0:
                psuIsPresent=psu0present 
            elif psuNum==1:
                psuIsPresent=psu1present 

            # if the powerSupply is PRESENT, then get the details and create the dict entry
            #     get the data from dbus
            if psuIsPresent is True:
                # if present, psuEntry["Status"]["State"]="Enabled"
                psuEntry["Status"]["State"] = "Enabled"   
                psuEntry["Status"]["Health"] = None

                # read supplyType, voltageType, capacity, serialnumber from dbus and fillin
                if( self.stub is True):
                    psuEntry["PowerSupplyType"] =  "AC"             # *** from dbus, read powerSupplyType
                    psuEntry["LineInputVoltageType"] =  "AC120V"    # *** from dbus, read powerSupplyVoltageType
                    psuEntry["PowerCapacityWatts"] =  850           # *** from dbus, read powerSupply capacity
                    psuEntry["SerialNumber"] =  "ADC1202017-1130BX" # *** from dbus, read powerSupply serial num
                else:
                    psuEntry["PowerSupplyType"] =  "AC"             # xg44 need to finish integration
                    psuEntry["LineInputVoltageType"] =  "AC120V"    # xg44 need to finish integration
                    psuEntry["PowerCapacityWatts"] =  850           # xg44 need to finish integration
                    psuEntry["SerialNumber"] =  "ADC1202017-1130BX" # xg44 need to finish integration

            else:  # psuIspresent is False:   the PSU is ABSENT
                # just set the status/state to absent in this case-upper level code handles the rest.
                psuEntry["Status"]["State"] = "Absent"

            # save the entry dict for "this psu" in the response
            resp["Id"][psuId]=psuEntry

        # end:  for psuNum in range(0, maxNumOfPsus):    # psu is 0, 1, ... up to maxNumOfPsus-1
        return(resp)



    # read the  dynamic property readings for a Specific PowerSupply
    #    request properties are <psuId> -- the powerSupply "Id" which is a string of form: "0", "1", ...
    #    returns: integers: rc, currentInputVoltage, lastOutputPower
    #        where rc is negative if error,   rc=0 if no error
    #        currentInputVoltage is the line input voltage --in watts   returned as an integer
    #        lastOutputPower is the output power --in watts   returned as an integer
    #    if either currentInputVoltage or lastOutputPower are unknown, None is returned
    def getObmcPowerSupplyReading(self, psuId):
        # note: this is getting the psu readings for psu Id "psuId"
        currentInputVoltage=None
        lastOutputPower=None

        if( self.stub is True):
            currentInputVoltage=199
            lastOutputPower=399
        else:
            # get the data from dbus
            currentInputVoltage=199  #xg44 need to complete integration
            lastOutputPower=399      #xg44 need to complete integration

        rc=0
        return( rc, currentInputVoltage, lastOutputPower )

    # get PowerSupply volatile: Status: State(present/absent) and Health from Dbus 
    #    request properties are <psuId> -- the powerSupply "Id" which is a string of form: "0", "1", ...
    #    returns: None if error
    #    returns: resp={"Status": "<state>", "Health": "<HealthEnum>"   if no error
    #         where <state> is string enum oneOf:   "Enabled" (present-on), "Disabled"(present-off), "Absent"(absent)
    #         where <HealthEnum> is a string enum oneOf:  "OK", "Warning", "Critical"
    #            OK= AC_OK, and Output_OK.
    #            Warning= AC not ok, but Output_OK
    #            Critical= Output is not ok
    def getObmcPowerSupplyStatus(self,psuId):
        resp=dict()
        resp["Status"]={}

        # check if the psu is present
        if( self.stub is True):
            psuIsPresent=True   # *******from dbus, find out if the psu[psuNum] is present
        else:
            psuIsPresent=True   # xg44 need to finish integrating. but if we know about the Id it must be present

        # if the powerSupply is PRESENT, then get the details and create the dict entry
        #     get the data from dbus
        if psuIsPresent is True:
            # if present, psuEntry["Status"]["State"]="Enabled"
            resp["Status"]["State"] = "Enabled"

            # read current powerSupply health info and get current health--usually there is on OK bit
            if( self.stub is True):
                psu_AC_OK=True     #  ********from dbus, read AC OK bit
                psu_Output_OK=True #  ********from dbus, read Output OK bit
            else:
                psu_AC_OK=True     #  xg44 need to finish integrating
                psu_Output_OK=True #  xg44 need to finish integrating

            if (psu_Output_OK is True):
                    if   (psu_AC_OK is True):
                        resp["Status"]["Health"] = "OK"
            elif (psu_AC_OK is False):
                        resp["Status"]["Health"] = "Warning"
            else:   # (psu_Output_OK is False
                        resp["Status"]["Health"] = "Critical"
        else:  # psuIspresent is False:   the PSU is ABSENT
            # just set the status/state to absent in this case-upper level code handles the rest.
            resp["Status"]["State"] = "Absent"

        return(resp)



    # --------------------------------------------------
    # Base System Discovery and update APIs
    #
    # do DBUS query to get non-volatile discovery-time info for the Base System entry
    #    returns: resp={
    def discoverObmcSysBaseInfo(self):
        resp=dict()
        if( self.stub is True):
            resp["BiosVersion"]="X04x"
            resp["ProcessorSummary"]={"Count": 2, "Model": "Power9" }
            resp["MemorySummary"]={"TotalSystemMemoryGiB": 16 }
            # if system UUID is known, enter it here, otherwise higher-level code will use the ServiceEntry UUID
            # so don't return UUID here if it is not known
            #resp["UUID"]="ffffffff-ffff-ffff-ffff-fffffffffffx"   # the SYSTEM UUID in this format 
        else:
            cpuNums = self.ProcDbus.get_cpu_nums()
            resp["BiosVersion"]=self.ProcDbus.get_bios_fw_ver()

            resp["ProcessorSummary"]={"Count": cpuNums['PresNumOfCPUs'], "Model": "Power9" }
            resp["MemorySummary"]={"TotalSystemMemoryGiB": 16 }
            # if system UUID is known, enter it here, otherwise higher-level code will use the ServiceEntry UUID
            # so don't return UUID here if it is not known
            #resp["UUID"]="ffffffff-ffff-ffff-ffff-fffffffffffx"   # the SYSTEM UUID in this format 
        return(resp)


    # return the Boot Source Override config settings:
    # returns a dict with the following four properties:  set to None if HW doesn't know
    #     BootSoruceOverrideEnabled:  anyOf:  "Disabled", "Once", "Continuous"
    #     BootSourceOverrideTarget :  anyOf:  "None","Pxe","Floppy","Cd","Usb","Hdd",BiosSetup",'Utilities","Diags",
    #                                           "UefiShell,"UefiTarget","SDCard",UefiHttp",RemoteDrive","UefiBootNext"
    #     BootSourceOverrideMode:     anyOf:  "UEFI", "Legacy"
    #     UefiTargetBootSourceOverride = string uefi path
    def getBootSourceOverrideProperties(self):
        resp=dict()
        if( self.stub is True):
            resp["BootSourceOverrideEnabled"]    = "Once"
            resp["BootSourceOverrideTarget"]     = "Pxe"
            resp["BootSourceOverrideMode"]       = "Legacy"
            resp["UefiTargetBootSourceOverride"] = ""
        else:
            resp["BootSourceOverrideEnabled"]    = "Once"     # xg44 need to finish integrating
            resp["BootSourceOverrideTarget"]     = "Pxe"      # xg44 need to finish integrating
            resp["BootSourceOverrideMode"]       = "Legacy"   # xg44 need to finish integrating
            resp["UefiTargetBootSourceOverride"] = ""         # xg44 need to finish integrating
        return(resp)

    # set System Boot Properties
    #    returns: neg num if error
    #    returns: 0 if no error
    #    request properties:  a dict with writable boot properties:
    #        bootProps={ "BootSourceOverrideEnabled": <value>, "BootSourceOverrideTarget": <value> }
    #        where <values> are specified above for these properties in getBootSourceOverrideProperties() method
    def setObmcBootSourceOverrideProperties(self,bootPropertiesDict):
        if( self.stub is True):
            if "BootSourceOverrideEnabled" in bootPropertiesDict:
                print("set System Boot Prop: {}".format(bootPropertiesDict["BootSourceOverrideEnabled"]))
            if "BootSourceOverrideTarget" in bootPropertiesDict:
                print("set System Boot Prop: {}".format(bootPropertiesDict["BootSourceOverrideTarget"]))
            sys.stdout.flush()
        else:
            #xg44 need to finish integrating
            if "BootSourceOverrideEnabled" in bootPropertiesDict:
                print("set System Boot Prop: {}".format(bootPropertiesDict["BootSourceOverrideEnabled"]))
            if "BootSourceOverrideTarget" in bootPropertiesDict:
                print("set System Boot Prop: {}".format(bootPropertiesDict["BootSourceOverrideTarget"]))
            sys.stdout.flush()
        return(0)


    # Reset System via Dbus from on-demand POST System Reset API
    #    returns: neg number if error,  0 if success
    #    request parameters are: <resetType> which is a string enum oneOf: "On","ForceOff", "ForceRestart" 
    #        implementation must support ForceRestart.   goal is to support the soft reset GracefulRestart also
    def resetObmcSystem(self, resetType):
        if( self.stub is True):
            if resetType == "On":
                # do a Hard Reset
                print("Reset BMC: On")
                sys.stdout.flush()
            elif resetType == "ForceRestart":
                # do a Hard Reset
                print("Reset BMC: HARD")
                sys.stdout.flush()
            elif resetType == "GracefulRestart":
                # do a graceful shutdown and then restart
                print("Reset BMC: SOFT - Graceful")
                sys.stdout.flush()
            else:
                return(-9) # resetType not supported
        else:
            pass # getFromDbus
            if resetType == "On":
                self.ProcDbus.set_host_state_On()
            elif resetType == "ForceOff":
                self.ProcDbus.set_chassis_state_Off()
            elif resetType == "ForceRestart":
                self.ProcDbus.set_chassis_state_Off()
                time.sleep(10)
                self.ProcDbus.set_host_state_On()
            elif resetType == "GracefulRestart":
                self.ProcDbus.set_host_state_Reboot()
            else:
                return(-9) # resetType not supported

        return(0)

    # --------------------------------------------------
    # Fans  Discovery and update APIs
    #
    # do DBUS query to get non-volatile discovery-time info for the Fans
    #    returns:  None if error
    #    returns: resp={ "MaxNumOfFans": <maxFans>,
    #                    "MinNumOfFans": <minFans>,  # min num of Fans required to work w/ current redundancy config
    #                    "Id": {
    #                        "0": {
    #                             "MinReadingRange": 0, "MaxReadingRange": 4000, LowerThresholdCritical": 16]
    #                             },
    #                        "1": { ... second fan ...  },
    #                        "<fanId-n>": { ... last fan ... }
    #                  } }
    #        where <maxFans> is an integer representing the num of supported fans for the system (eg 6)
    #        where <minFans> is an integer representing the min number of fans to run the system (eg 5 if N+1 sparing)
    #        there is a dictionary entry for each Fan referenced by "Id"[<fanId>]:  with properties:
    def discoverObmcFansInfo(self):
        resp=dict()
        resp["Id"]={}
        stub =  self.stub
        stub = True # xg44   return all stub data for now

        # get the number of Fans that the chassis/system supports -- eg 6 for a monolythic server
        # and the minumum number of supplies required -- eg 6-1 = 5
        #    this is used by redfish service to indicate the min number required if redundanct supplies eg N+1 sparing is used
        #    if maxNumOfFans==6, and redundancy is enabled in the server,  minNumOfFans=5.
        #    it is possible that some configs might be non-redundant and require 6 supplies--in which case minNumOfFans=6
        if( stub is True):
            maxNumOfFans=6   # ***from dbus--typical is 6 for monolythic
            minNumOfFans=5   # ***from dbus--typical is 5 for monolythic 
            readingUnits="RPM" # ***from dbus--typical is 5 for monolythic  
        else:
            pass # getFromDbus -- maxNumOfFans=6   # ***from dbus--typical is 2 for monolythic
                 # getFromDbus -- minNumOfFans=5   # ***from dbus--typical is 1 for monolythic 

        # save the max and min Fans in the response
        resp["MaxNumOfFans"] = maxNumOfFans
        resp["MinNumOfFans"] = minNumOfFans

        # loop maxNumOfFans querying dbus to get discovery info about any Pans present
        #    if a PSU is absent, we state it is absent here, and the other info is python None (which maps to Json null)
        for fanNum in range(0, maxNumOfFans):    # fan is 0, 1, ... up to maxNumOfFans-1
            # create an empty dict for this fan and generate the fanId
            fanEntry=dict()   
            fanId = str(fanNum)
            fanEntry["Status"] = {"State": "Absent", "Health": None}

            # this is SDR data - the HWMon should know what these are regardless of if fan is present
            if( stub is True):
                fanEntry["MinReadingRange"]=0
                fanEntry["MaxReadingRange"]=2500
                fanEntry["LowerThresholdCritical"]=16
                fanEntry["ReadingUnits"]="RPM"
            else:
                pass # getFromDbus  HwMon-- MinReadingRange, MaxReadingRange, LowerThresholdCritical


            # save the entry dict for "this fan" in the response
            resp["Id"][fanId]=fanEntry

        # end:  for fanNum in range(0, maxNumOfFans):    # fan is 0, 1, ... up to maxNumOfFans-1
        return(resp)


    # read the  dynamic property readings for a Specific Fan
    #    request properties are <fanId> -- the fan "Id" which is a string of form: "0", "1", ...
    #    returns: integers: rc, fanReadingRpms, fanReadingDutyCycle
    #        where rc is negative if error,   rc=0 if no error
    #        fanReadingRpms should be returned and calculated from duty cycle if necessary
    #        fanReadingDutyCycle can be null 
    #    if either fanReading is unknown, return None
    def getObmcFanReading(self, fanId):
        # note: this is getting the psu readings for psu Id "fanId"
        fanReadingRpms=None
        fanReadingDutyCycle=None

        if( self.stub is True):
            fanReadingRpms=2233
        else:
            # get the data from dbus
            fanReadingRpms=2233   #xg44 need to finish integrating

        rc=0
        return( rc, fanReadingRpms, fanReadingDutyCycle )

    # get fan volatile: Status: State(present/absent) and Health from Dbus ***if it exists***
    #    request properties are:
    #             <fanId> -- the powerSupply "Id" which is a string of form: "0", "1", ...
    #  **If Hardware Monitor does NOT know the status, python None is returned
    #         If None is returned, upper layer code will derive Status from the fan reading value
    #  **If Hardware Monitor does know the fan status, statis dict is returned:
    #      resp={"State": "<state>", "Health": "<HealthEnum>"  }
    #         where <state> is string enum oneOf:   "Enabled" (present-on), "Disabled"(present-off), "Absent"(absent)
    #         where <HealthEnum> is a string enum oneOf:  "OK", "Warning", "Critical"
    #            State and Health is calculated from the ReadingRpm value passed in unless the HW otherwise has health info
    def getObmcFanStatus(self,fanId ):
        resp=dict()

        # check if the fan is present
        if( self.stub is True):
            resp["State"] = "Enabled"   # return  "Absent" if fan is absent and hw has a presence detector
            resp["Health"] = "OK"       # dont include Health property if absent
            # or return None if HardwareMonitor won't know it and we want upper layer SW to handle based on fan speed
        else:
            #xg44 need to finish integrating
            resp["State"] = "Enabled"   # return  "Absent" if fan is absent and hw has a presence detector
            resp["Health"] = "OK"       # dont include Health property if absent

        return(resp)


    # --------------------------------------------------
    # Temperature Sensors  Discovery and update APIs
    # returns a dict with 3 or 4 sensors depending on the number of CPUs:
    # tempSensorInfo= { "Id": {
    #    "Intake": { ...sensor properties...},    # the inlet temp
    #    "Board":  { ... sensor properties...},   # the board temp - a sensor on the main system board
    #    "CPU1":   { ...sensor propoerties...},   # CPU1 temp
    #    "CPU2":   { ...sensor propoerties...}    # CPU2 temp - if there are 2 cpus
    #   } }
    #  {...sensor properties...} = {"SensorNumber": <num>, "UpperThresholdNonCritical": <utnc>, "LowerThresholdNonCritical": <ltnc>,
    #                               "UpperThresholdCritical": <utc>, "LowerThresholdCritical": <ltc>, 
    #                               "MinReadingRange": <minRange>, "MaxReadingRange": <maxRange> } 
    #
    def discoverObmcTempSensorsInfo(self):
        resp=dict()
        resp["Id"]={}

        stub = self.stub
        stub = True   # xg44 need to return stub data until we integrate

        if( stub is True):
            resp["Id"]["Intake"] = {
                "SensorNumber": 41,
                "UpperThresholdNonCritical": 37,
                "LowerThresholdNonCritical": 10,
                "UpperThresholdCritical": 39,
                "LowerThresholdCritical": 5,
                "MinReadingRange": 0,
                "MaxReadingRange": 100,
                "Status": {"State": "Enabled", "Health": "OK" }
            }
            resp["Id"]["Board"] = {
                "SensorNumber": 42,
                "UpperThresholdNonCritical": 60,
                "LowerThresholdNonCritical": 10,
                "UpperThresholdCritical": 70,
                "MinReadingRange": 0,
                "MaxReadingRange": 200,
                "Status": {"State": "Enabled", "Health": "OK" },
            }
            resp["Id"]["CPU1"] = {
                "SensorNumber": 43,
                "UpperThresholdNonCritical": 100,
                "LowerThresholdNonCritical": 10,
                "UpperThresholdCritical": 105,
                "MinReadingRange": 0,
                "MaxReadingRange": 200,
                "Status": {"State": "Enabled", "Health": "OK" },
            }
            resp["Id"]["CPU2"] = {
                "SensorNumber": 44,
                "UpperThresholdNonCritical": 100,
                "LowerThresholdNonCritical": 10,
                "UpperThresholdCritical": 105,
                "MinReadingRange": 0,
                "MaxReadingRange": 200,
                "Status": {"State": "Enabled", "Health": "OK" },
            }

        else:
            pass # getFromDbus

        return(resp)

    # get Temperature sensor reading
    #    request properties:  tempSensorId
    #    returns: None if error
    #    returns: resp=<reading> int if no error where reading is degrees celcius
    def getObmcTempSensorReading(self,tempSensorId):
        stub = self.stub
        stub = True   # xg44 need to return stub data until we integrate

        if( stub is True):
            if tempSensorId=="Intake":
                resp=20
            elif tempSensorId=="Board":
                resp=32
            elif tempSensorId=="CPU1":
                resp=51
            elif tempSensorId=="CPU2":
                resp=52
            else:
                resp=None
        else:
            pass # getFromDbus
        return(resp)

    # --------------------------------------------------
    # Voltage Sensors  Discovery and update APIs
    #
    # do DBUS query to get non-volatile discovery-time info for the Voltage Sensors
    #    returns: resp={}  empty dict
    def discoverObmcVoltageSensorsInfo(self):
        resp=None
        if( self.stub is True):
            resp=None
        else:
            resp=None
        return(resp)



    # get Voltage sensor reading
    #    request properties:  voltSensorId
    #    returns: None if error
    #    returns: resp=<reading> int if no error where reading is volts
    def getObmcVoltSensorReading(self,voltSensorId):
        if( self.stub is True):
            resp=None # no volt sensors
        else:
            resp=None # no volt sensors
        return(resp)

    # --------------------------------------------------
    # *************************************************************************************
    # *************************************************************************************
    # *************************************************************************************
    # *************************************************************************************

