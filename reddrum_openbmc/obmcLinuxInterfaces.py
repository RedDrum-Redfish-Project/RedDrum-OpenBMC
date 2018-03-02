
# Copyright Notice:
#    Copyright 2018 Dell, Inc. All rights reserved.
#    License: BSD License.  For full license text see link: https://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC/LICENSE.txt

import sys
import os
import subprocess
from subprocess import Popen, PIPE
import json
import ipaddress

class RdOpenBmcLinuxInterfaces():
    def __init__(self,rdr):
        self.rdr = rdr
        self.x = 1


    # get Network Info
    # Returns dict of form:
    # {
    #     "SSH":   { "ProtocolEnabled":  "True" },
    #     "HTTP":  { "ProtocolEnabled":  "True" },
    #     "HTTPS": { "ProtocolEnabled":  "True" },
    #     "HostName":  "openbmc2",
    #     "FQDN":  "openbmc2.ocp.org"
    # }
    # The script getObmcProtocolInfo.sh uses linux commands to get the protocol info:
    # netstat -tlp output is passed through awk script to determine if ssh, http, and https is enabled
    #  netstatinfo=`netstat -tlp`; echo "${netstatinfo}" | awk '/ssh/ {print $4; exit }' 
    #  if  no response, the ProtocolEnabled is False.  else ProtocolEnabled is True 
    # HostName is output of command:  hostname    -- this gets whatever is in /etc/hosts
    # FQDN     is output of command:  hostname -f -- runs hostname and uses "1st" alias for hostname
    #                                      that is stored in /etc/hosts (1st alias is fqdn)
    #    in linux, to store fqdn, you must thus edit /etc/hosts
    def getObmcNetworkProtocolInfo(self):
        exitcode = 500
        protoInfo={}
        return(exitcode,protoInfo)
        scriptPath = os.path.join(self.rdr.backend.obmcScriptsPath, "getObmcProtocolInfo.sh")
        arg1 = "arg1" # current script doesn't require arg but showing here if we need to add
        arg2 = "arg2" # 
        proc = Popen([scriptPath,arg1,arg2],stdout=PIPE,stderr=PIPE)
        out,err=proc.communicate()
        exitcode=proc.returncode
        # handle error case running script
        if exitcode != 0:
            protoInfo={}
            return(exitcode,protoInfo)

        # else process the output
        #  getObmcProtocolInfo.sh outputs a json response structure with properties 
        #  load to a json struct
        getObmcProtocolInfoOutputString = str(out, encoding='UTF-8')   # convert from bytes to utf8 string. 
        protoInfo=json.loads(getObmcProtocolInfoOutputString )

        return(0,protoInfo)


    # --------------------------------------------------
    # --------------------------------------------------
    # get Manager Ethernet settings, for previously discovered device eg device "Eth0"
    def getObmcIpInfo(self,device):
        exitcode = 500
        ipInfo={}
        return(exitcode,ipInfo)
        scriptPath = os.path.join(self.rdr.backend.obmcScriptsPath, "getObmcIpInfo.sh")
        arg1 = device # the "device" Name to use in the response
        arg2 = "arg2" # 
        proc = Popen([scriptPath,arg1,arg2],stdout=PIPE,stderr=PIPE)
        out,err=proc.communicate()
        exitcode=proc.returncode
        ipInfo=dict()
        ipInfo["MACAddress"]=None
        ipInfo["IPv4Addresses"]=[]
        # handle error case running script
        if exitcode != 0:
            return(exitcode,ipInfo)

        # getObmcIpInfo.sh outputs a json response structure of form:
        #  ipv4info=[{"Address": "EEE", "SubnetMask": "EEE", "Gateway": "EEE", "AddressOrigin": "EEE"}]
        #  ethDeviceInfo = {
        #        "Name": "eth1", "SpeedMbps": 1000, "HostName": "", "FQDN": "", "LinkStatus": "EEE",
        #        "InterfaceEnabled": None, "FullDuplex": True, "AutoNeg": True,
        #        "MACAddress": "AAA", "PermanentMACAddress": "AAA", "IPv4Addresses": ipv4info
        #  }
        #  load to a json struct
        getObmcIpInfoOutputString = str(out, encoding='UTF-8')   # convert from bytes to utf8 string. 
        print("EEEEEEEEEEE")
        print(" ipinfo: {}".format(getObmcIpInfoOutputString))
        backendGetIpInfo=json.loads(getObmcIpInfoOutputString )


        baseEthProperties = ["MACAddress","PermanentMACAddress","InterfaceEnabled","LinkStatus",
                                "SpeedMbps","HostName","FQDN","AutoNeg","Name" ]
        for ipProp in baseEthProperties:
            if ipProp in backendGetIpInfo:
                ipPropVal = backendGetIpInfo[ipProp]
                if ipPropVal == "":
                    ipInfo[ipProp] = None
                ipInfo[ipProp] = ipPropVal
            else:
                ipInfo[ipProp] = None

        # get IPV4 Info
        ipv4AddrEntry=dict()
        # origin: DHCP, STATIC, None
        if "IPV4Origin" in backendGetIpInfo:
            origin=backendGetIpInfo["IPV4Origin"]
            if origin=="":
                origin=None
            ipv4AddrEntry["AddressOrigin"] = origin

        # Gateway
        gateway = backendGetIpInfo["Gateway"]
        if gateway == "":
            gateway = None
        ipv4AddrEntry["Gateway"] =  gateway

        # ipaddress and netmask
        ipv4AddressPlusNetworkBits = backendGetIpInfo["IPV4Address"]       # eg 192.168.22.2/24
        if ipv4AddressPlusNetworkBits == "":
            ipv4AddrEntry["Address"] = None
            ipv4AddrEntry["SubnetMask"] = None
        else:
            ipv4iface = ipaddress.ip_interface(ipv4AddressPlusNetworkBits )    # save as an ip_interface object
            ipv4AddrEntry["Address"] = ipv4iface.with_netmask.split("/")[0]    # get the ipAddr 
            ipv4AddrEntry["SubnetMask"] = ipv4iface.with_netmask.split("/")[1] # get the Netmask 

        # get IPV6 Info
        #ipv6AddrEntry=dict()
        #ipv6AddrEntry["AddressOrigin"] = backendGetIpInfo["IPv6Origin"]
        #ipv6AddressPlusMaskBits = backendGetIpInfo["IPV6Address"]

        ipInfo["IPv4Addresses"].append(ipv4AddrEntry)

        return(0,ipInfo)

    # --------------------------------------------------
