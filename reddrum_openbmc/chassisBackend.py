
# Copyright Notice:
#    Copyright 2018 Dell, Inc. All rights reserved.
#    License: BSD License.  For full license text see link: https://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC/LICENSE.txt

from .obmcDbusInterfaces import RdOpenBmcDbusInterfaces

# BullRed-RackManager chassisBackend resources
#
class  RdChassisBackend():
    # class for backend chassis resource APIs
    def __init__(self,rdr):
        self.version=0.9
        self.rdr=rdr
        self.dbus=RdOpenBmcDbusInterfaces(rdr)


    # update resourceDB and volatileDict properties for a base Chassis GET
    def updateResourceDbs(self,chassisid, updateStaticProps=False, updateNonVols=True ):
        self.rdr.logMsg("DEBUG","--------BACKEND updateResourceDBs. updateStaticProps={}".format(updateStaticProps))
        resDb=self.rdr.root.chassis.chassisDb[chassisid]
        resVolDb=self.rdr.root.chassis.chassisVolatileDict[chassisid]
        updatedResourceDb=False

        # update volatile properties
        prop="IndicatorLED"
        if "Volatile" in resDb and prop in resDb["Volatile"]:
            # get the led value from dbus HW interface
            hwLedState=self.dbus.getObmcChassisIndicatorLED()
            if hwLedState is not None:
                resVolDb[prop]=hwLedState

        prop="PowerState"
        if "Volatile" in resDb and prop in resDb["Volatile"]:
            # get the powerState from hw
            hwPowerState=self.dbus.getObmcChassisPowerState()
            if hwPowerState is not None:
                resVolDb["PowerState"]=hwPowerState

        # update non-volatile properties
        if updateNonVols is True:
            prop="AssetTag"
            if prop in resDb:
                #read assetTag from HW
                hwAssetTag=self.dbus.getObmcAssetTag()
                if hwAssetTag is not None:
                    if resDb[prop] != hwAssetTag:
                        resDb[prop]=hwAssetTag
                        updatedResourceDb=True

        # for obmc, we will not support update of static props for chassis

        rc=0     # 0=ok
        return(rc,updatedResourceDb)

    def doChassisReset(self, chassisid, resetType):
        self.rdr.logMsg("DEBUG","--------BACKEND got POST for Chassis Reset--NOT SUPPORTED FOR OBMC")
        rc = self.dbus.resetObmcSystem(resetType)
        return(rc)

    def doChassisOemReseat(self, chassisid ):
        self.rdr.logMsg("DEBUG","--------BACKEND got POST for Chassis OemReseat--NOT SUPPORTED FOR OBMC")
        #not supported on open bmc monolythic
        return(9)


    #PATCH Chassis
    # patchData is a dict of form: { <patchProperty>: <patchValue> }
    #    the front-end will send an individual call for IndicatorLED and AssetTag 
    # DO Patch to chassis  (IndicatorLED, AssetTag) 
    # the front-end will send an individual call for IndicatorLED and AssetTag 
    def doPatch(self, chassisid, patchData):
        # the front-end has already validated that the patchData and chassisid is ok
        # so just send the request here
        self.rdr.logMsg("DEBUG","--------BACKEND Patch chassis data. patchData={}".format(patchData))
        # just call the dbus call to set indicatorLED
        if "IndicatorLED" in patchData:
            ledStateVal=patchData["IndicatorLED"]
            rc = self.dbus.setObmcChassisIndicatorLed( ledStateVal )
        elif "AssetTag" in patchData:
            assetTagVal=patchData["AssetTag"]
            rc = self.dbus.setObmcChassisIndicatorLed( assetTagVal )
        else:
            rc=-9
    
        return(rc)


    # update Temperatures resourceDB and volatileDict properties
    def updateTemperaturesResourceDbs(self, chassisid, updateStaticProps=False, updateNonVols=True ):
        self.rdr.logMsg("DEBUG","--------BE updateTemperaturesResourceDBs. updateStaticProps={}".format(updateStaticProps))
        resDb=self.rdr.root.chassis.tempSensorsDb[chassisid]
        resVolDb=self.rdr.root.chassis.tempSensorsVolatileDict[chassisid]
        if "Id" not in resVolDb:
            resVolDb["Id"]={}

        for sensorId in resDb["Id"]:
            tempReading = self.dbus.getObmcTempSensorReading(sensorId)
            if sensorId not in resVolDb["Id"]:
                resVolDb["Id"][sensorId]={}
            if tempReading is not None:
                resVolDb["Id"][sensorId]["ReadingCelsius"]=tempReading
        return (0,False)


    # update Fans resourceDB and volatileDict properties
    # returns: rc, updatedResourceDb(T/F).  rc=0 if no error
    def updateFansResourceDbs(self, chassisid, updateStaticProps=False, updateNonVols=True ):
        self.rdr.logMsg("DEBUG","--------BE updateFansResourceDBs. updateStaticProps={}".format(updateStaticProps))

        if chassisid in self.rdr.root.chassis.fansDb and "Id" in self.rdr.root.chassis.fansDb[chassisid]:
            resDb=self.rdr.root.chassis.fansDb[chassisid]
            resVolDb=self.rdr.root.chassis.fansVolatileDict[chassisid]
            if "Id" not in resVolDb:
                resVolDb["Id"]={}
            for fanId in resDb["Id"]:
                if fanId not in resVolDb["Id"]:
                    resVolDb["Id"][fanId]={}
                rc,fanReadingRpms,fanReadingDutyCycle=self.dbus.getObmcFanReading(fanId)
                status=self.dbus.getObmcFanStatus(fanId)
                if status is None:   # hw cant determine status.  we need to calculate from fanspeed
                    if( fanReadingRpms == 0):
                        resVolDb["Id"][fanId]["Status"] = { "State": "Absent" }
                    elif (fanReadingRpms <  resDb["Id"][fanId]["LowerThresholdCritical"]): 
                        resVolDb["Id"][fanId]["Status"] = {"State": "Enabled", "Health": "Critical"}
                    else:
                        resVolDb["Id"][fanId]["Status"] = {"State": "Enabled", "Health": "OK"}
                else:
                    resVolDb["Id"][fanId]["Status"] = status

                resVolDb["Id"][fanId]["Reading"] = fanReadingRpms

        # Defensive check for temporary time. We are returning False, because the below logic
        # is not completed and gives failures.
        return (0,False)

    # update Voltages resourceDB and volatileDict properties
    # returns: rc, updatedResourceDb(T/F).  rc=0 if no error
    def updateVoltagesResourceDbs(self, chassisid, updateStaticProps=False, updateNonVols=True ):
        self.rdr.logMsg("DEBUG","--------BE updateVoltagesResourceDBs. updateStaticProps={}".format(updateStaticProps))
        resDb=self.rdr.root.chassis.voltageSensorsDb[chassisid]
        resVolDb=self.rdr.root.chassis.voltageSensorsVolatileDict[chassisid]
        if "Id" not in resVolDb:
            resVolDb["Id"]={}

        for sensorId in resDb["Id"]:
            voltReading = self.dbus.getObmcVoltSensorReading(sensorId)
            if sensorId not in resVolDb["Id"]:
                resVolDb["Id"][sensorId]={}
            if voltReading is not None:
                resVolDb["Id"][sensorId]["ReadingVolts"]=voltReading
        return (0,False)


    # update PowerControl resourceDB and volatileDict properties
    # returns: rc, updatedResourceDb(T/F).  rc=0 if no error
    def updatePowerControlResourceDbs(self, chassisid, updateStaticProps=False, updateNonVols=True ):
        self.rdr.logMsg("DEBUG","--------BE updatePowerControlResourceDBs. ")
        resDb=self.rdr.root.chassis.powerControlDb[chassisid]
        resVolDb=self.rdr.root.chassis.powerControlVolatileDict[chassisid]
        updatedResourceDb=False
        pwrcntlid="0"

        if pwrcntlid not in resDb["Id"]:
            return(0,False)
        if "Id" not in resVolDb:
            resVolDb["Id"]={}
        if pwrcntlid not in resVolDb["Id"]:
            resVolDb["Id"][pwrcntlid]={}

        prop="PowerConsumedWatts"
        if "Volatile" in resDb["Id"][pwrcntlid] and prop in resDb["Id"][pwrcntlid]["Volatile"]:
            # get the powerState from hw
            hwPowerConsumedWatts=self.dbus.getObmcPowerReading()
            if hwPowerConsumedWatts is not None:
                resVolDb["Id"][pwrcntlid][prop]=hwPowerConsumedWatts

        # update PowerLimit non-volatile properties
        if updateNonVols is True:
            prop="LimitInWatts"
            if prop in resDb["Id"][pwrcntlid]:
                #read property from HW
                hwPowerLimit=self.dbus.getObmcPowerLimit()
                if hwPowerLimit is not None:
                    if resDb["Id"][pwrcntlid][prop] != hwPowerLimit:
                        resDb["Id"][pwrcntlid][prop]=hwPowerLimit
                        updatedResourceDb=True

            prop="LimitException"
            if prop in resDb["Id"][pwrcntlid]:
                #read property from HW
                hwPowerLimitException=self.dbus.getObmcPowerLimitException()
                if hwPowerLimitException is not None:
                    if resDb["Id"][pwrcntlid][prop] != hwPowerLimitException:
                        resDb["Id"][pwrcntlid][prop]=hwPowerLimitException
                        updatedResourceDb=True

        rc=0     # 0=ok
        return(rc,updatedResourceDb)


    # DO Patch to chassis  PowerControl (PowerLimit, PowerLimitException)
    # the front-end will send an individual call for each property
    def patchPowerControl(self, chassisid, patchData):
        self.rdr.logMsg("DEBUG","--------BACKEND Patch chassis PowerControl data. patchData={}".format(patchData))
        # just call the dbus call to set the prop
        if "LimitInWatts" in patchData:
            powerLimit=patchData["LimitInWatts"]
            rc=self.dbus.setObmcPowerLimit(powerLimit)
        elif "LimitException" in patchData:
            powerLimitException=patchData["LimitException"]
            rc=self.dbus.setObmcPowerLimitException(powerLimitException)
        else:
            rc=-9
        return(rc)


    # update PowerSupplies resourceDB and volatileDict properties
    #   updated volatiles:  LineInputVoltage, LastPowerOutputWatts, Status
    # returns: rc, updatedResourceDb(T/F).  rc=0 if no error
    def updatePowerSuppliesResourceDbs(self, chassisid, updateStaticProps=False, updateNonVols=True ):
        self.rdr.logMsg("DEBUG","--------BE updatePowerSuppliesResourceDBs. updateStaticProps={}".format(updateStaticProps))
        resDb=self.rdr.root.chassis.powerSuppliesDb[chassisid]
        resVolDb=self.rdr.root.chassis.powerSuppliesVolatileDict[chassisid]
        updatedResourceDb=False
        psuIsAbsent=False

        for psuId in resDb["Id"]: # where psuId is a string like "0", "1".
            # get psu status
            psuStatus = self.dbus.getObmcPowerSupplyStatus(psuId)
            if psuStatus is None:
                self.rdr.logMsg("ERROR","--------BE updatePowerSuppliesResourceDBs. Error getting powerSupply status")
            else:
                if "Id" not in resVolDb:
                    resVolDb["Id"]={}
                if psuId not in resVolDb["Id"]:
                    resVolDb["Id"][psuId]={}
                if "Status" not in resVolDb["Id"][psuId]:
                    resVolDb["Id"][psuId]["Status"]={}
                if "State" in resVolDb["Id"][psuId]["Status"]:
                    currentStatusState=resVolDb["Id"][psuId]["Status"]["State"]
                elif "Status" in resDb["Id"][psuId] and "State" in resDb["Id"][psuId]["Status"]:
                    currentStatusState=resDb["Id"][psuId]["Status"]["State"]
                else:
                    currentStatusState=None
                if "Status" in psuStatus:
                    resVolDb["Id"][psuId]["Status"]=psuStatus["Status"]
                if "State" in psuStatus["Status"]:
                    newStatusState = psuStatus["Status"]["State"]
                else:
                    newStatusState = None
                if newStatusState == "Absent":
                    psuIsAbsent=True
                if newStatusState != currentStatusState:
                    #re-discover power supplies:
                    # xg99
                    self.rdr.logMsg("WARNING","--------BE updatePowerSuppliesResourceDBs. powerSupply Hotplut--not supported yet")

            # get psu readings
            if psuIsAbsent is True:
                resVolDb["Id"][psuId]["LineInputVoltage"]=None
                resVolDb["Id"][psuId]["LastPowerOutputWatts"]=None
            else:
                rc, currentInputVoltage, lastOutputPower = self.dbus.getObmcPowerSupplyReading(psuId)
                if rc!=0:
                    self.rdr.logMsg("ERROR","--------BE updatePowerSuppliesResourceDBs. Error getting powerSupply Readings")
                else:
                    #update the dbs:   LineInputVoltage and LastPowerOutputWatts are volatiles
                    if currentInputVoltage is not None:
                        resVolDb["Id"][psuId]["LineInputVoltage"]=currentInputVoltage
                    if lastOutputPower is not None:
                        resVolDb["Id"][psuId]["LastPowerOutputWatts"]=lastOutputPower
        return (0,False)


