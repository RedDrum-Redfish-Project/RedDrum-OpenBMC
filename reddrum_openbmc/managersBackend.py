
# Copyright Notice:
#    Copyright 2018 Dell, Inc. All rights reserved.
#    License: BSD License.  For full license text see link: https://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC/LICENSE.txt

from .obmcDbusInterfaces  import RdOpenBmcDbusInterfaces
from .obmcLinuxInterfaces import RdOpenBmcLinuxInterfaces

# BullRed-RackManager managersBackend resources
#
class  RdManagersBackend():
    # class for backend managers resource APIs
    def __init__(self,rdr):
        self.rdr=rdr
        self.version=1
        self.dbus=RdOpenBmcDbusInterfaces(rdr)
        self.linuxApis=RdOpenBmcLinuxInterfaces(rdr)


    # update resourceDB and volatileDict properties
    def updateResourceDbs(self,managerid, updateStaticProps=False, updateNonVols=True ):
        self.rdr.logMsg("DEBUG","--------BACKEND updateResourceDBs. updateStaticProps={}".format(updateStaticProps))
        resVolDb=self.rdr.root.managers.managersVolatileDict[managerid]
        resDb=self.rdr.root.managers.managersDb[managerid]

        # if Status was defined in discovered db, then if not yet in volatileDIct, copy dflt to volatile
        # then query dbus looking for StatusHealth, and update if it is returned
        if "Status" in resDb and "Status" not in resVolDb:
            resVolDb["Status"]=resDb["Status"]
            if "Health" in resVolDb["Status"]:
                statusHealth=self.dbus.getObmcMgrStatusHealth()
                if statusHealth is not None:
                    resVolDb["Status"]["Health"] = statusHealth
        rc=0     # 0=ok
        updatedResourceDb=False    # only the volatile db was updated
        return(rc,updatedResourceDb)


    # DO action:  "Reset", "Hard,
    def doManagerReset(self,managerid,resetType):
        self.rdr.logMsg("DEBUG","--------BACKEND managerReset. resetType={}".format(resetType))
        rc=self.dbus.resetObmcMgr(resetType)
        return(rc)


    # DO Patch to Manager  (DateTime, DateTimeOffset)
    def doPatch(self, managerid, patchData):
        # the front-end has already validated that the patchData and managerid is ok
        # so just send the request here
        self.rdr.logMsg("DEBUG","--------BACKEND Patch manager: {} data. patchData={}".format(managerid,patchData))

        # for OpenBMC, there are no base manager patches that go to the backend.
        #              DateTime and DateTimeOffset are handled in the frontend
        #              Nothing to do here
        return(0)


    # update NetworkProtocolsDb Info
    def updateManagerNetworkProtocolsDbFromBackend(self, mgrid, noCache=False):
        # set local properties to point to this managerid Db and VolDict, ...
        resDb=self.rdr.root.managers.managersDb[mgrid]

        backendSupportedProtocols = ["HTTP","HTTPS","SSH"]

        if "NetworkProtocols" in resDb:
            rc,mgrNetwkProtoInfo = self.linuxApis.getObmcNetworkProtocolInfo()
            if rc==0:
                for proto in backendSupportedProtocols:
                    if proto in resDb["NetworkProtocols"] and proto in mgrNetwkProtoInfo:
                        resDb["NetworkProtocols"][proto]["ProtocolEnabled"] = mgrNetwkProtoInfo[proto]["ProtocolEnabled"]
                if "HostName" in mgrNetwkProtoInfo:
                        resDb["NetworkProtocols"]["HostName"] = mgrNetwkProtoInfo["HostName"]
                if "FQDN" in mgrNetwkProtoInfo:
                        resDb["NetworkProtocols"]["FQDN"] = mgrNetwkProtoInfo["FQDN"]
            else:
                return(9)
        return(0)


    # update EthernetInterface Info
    def updateManagerEthernetEnterfacesDbFromBackend(self, mgrid, noCache=False, ethid=None):
        resDb=self.rdr.root.managers.managersDb[mgrid]
        if "EthernetInterfaces" in resDb:
            if (ethid is not None) and (ethid in resDb["EthernetInterfaces"]):
                ethResDb = resDb["EthernetInterfaces"][ethid]

                # update IPv4Address info and MACAddress info
                rc,ipInfo=self.linuxApis.getObmcIpInfo(ethid)
                ipProperties = ["Name","MACAddress","PermanentMACAddress","InterfaceEnabled","LinkStatus",
                                "SpeedMbps","HostName","FQDN","AutoNeg", "IPv4Addresses" ]
                for ipProp in ipProperties:
                    if ipProp in ipInfo:
                        ethResDb[ipProp] = ipInfo[ipProp]

        return(0)

