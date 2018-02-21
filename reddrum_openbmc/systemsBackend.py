
# Copyright Notice:
#    Copyright 2018 Dell, Inc. All rights reserved.
#    License: BSD License.  For full license text see link: https://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC/LICENSE.txt

from .obmcDbusInterfaces import  RdOpenBmcDbusInterfaces

# systemBackend resources for RedDrum OpenBMC implementation
#
class  RdSystemsBackend():
    # class for backend systems resource APIs
    def __init__(self,rdr):
        self.version=1
        self.rdr=rdr
        self.nonVolatileDataChanged=False
        self.dbus = RdOpenBmcDbusInterfaces(rdr)



    # update resourceDB and volatileDict properties
    def updateResourceDbs(self,systemid, updateStaticProps=False, updateNonVols=True ):
        self.rdr.logMsg("DEBUG","--------BACKEND updateResourceDBs. updateStaticProps={}".format(updateStaticProps))

        resDb=self.rdr.root.systems.systemsDb[systemid]
        resVolDb=self.rdr.root.systems.systemsVolatileDict[systemid]
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

        # update BOot properties
        if ("BootSourceAllowableValues" in resDb) and ("BootSourceVolatileProperties" in resDb):
            bootInfo = self.dbus.getBootSourceOverrideProperties()
            for prop in resDb["BootSourceVolatileProperties"]:
                if prop in bootInfo:
                    resVolDb[prop]=bootInfo[prop]

        rc=0
        updatedResourceDb=False
        return(rc,updatedResourceDb)


    # DO action:   Reset OpenBMC System
    def doSystemReset(self,systemid,resetType):
        self.rdr.logMsg("DEBUG","--------SIM BACKEND systemReset. resetType={}".format(resetType))

        rc=self.dbus.resetObmcSystem(resetType)
        return(rc)




    # DO Patch to System  (IndicatorLED, AssetTag, or boot overrides
    #   the front-end will send an individual call for IndicatorLED and AssetTag or bootProperties
    #   multiple boot properties may be combined in one patch
    def doPatch(self, systemid, patchData):
        # the front-end has already validated that the patchData and systemid is ok
        # so just send the request here
        self.rdr.logMsg("DEBUG","--------BACKEND Patch system data. patchData={}".format(patchData))

        if "IndicatorLED" in patchData:
            rc=self.dbus.setObmcChassisIndicatorLed(patchData["IndicatorLED"])

        elif "AssetTag" in patchData:
            rc=self.dbus.setObmcAssetTag(patchData["AssetTag"])

        elif "Boot" in patchData:
            rc=self.dbus.setObmcBootSourceOverrideProperties(patchData["Boot"])
            pass

        else:
            return(9) # invalid property send to backend to patch

        return(rc)


