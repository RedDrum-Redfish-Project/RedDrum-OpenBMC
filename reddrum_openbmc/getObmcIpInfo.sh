#!/bin/sh
# Copyright Notice:
#    Copyright 2018 Dell, Inc. All rights reserved.
#    License: BSD License.  For full license text see link: https://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC/LICENSE.txt

# $1 is the Management Port: eg p4p1 or eth0
id="$1"
debug="$2"

# get the route info and extract the devicename and gateway from the route info
routeinfo=`ip route`  
dev=`echo ${routeinfo} | awk '/default/ {print $5; exit}'`

#xg gateway 
#xg gateway=`ip route |awk -v dev="$dev" '$1=="default" && $5==dev {print $3}'`

# get the device address info and extract
if [ "${dev}" = "" ]; then
   ipDeviceInfo=""
   gateway=""
else
   ipDeviceInfo=`ip addr show ${dev}`
   gateway=`echo "${routeinfo}" | awk '/default/ {print $3; exit}'`
fi

# for reference, below is howto pass a var into an awk string
#   gw=`echo ${routeinfo} | awk -v dev="$dev" '$1=="default" && $5==dev {print $3}'`

if [ "${debug}" == "debug" ]; then
    echo "-----------------------------------"
    echo "DEBUG: "
    echo "Device:"  ${dev}
    echo "Gateway:" ${gateway}
    echo "ip addr show ${dev}:"
    echo "ip addr show $dev:  "  "${ipDeviceInfo}" 
    echo "-----------------------------------"
fi


# extract mac, and IP addresses
#mac=`echo "${ipDeviceInfo}" | awk '$1 == "link/ether" {print $2; exit}'`

ipv4Address=`echo "${ipDeviceInfo}" | awk '$1 == "inet" {print $2; exit}'`
ipv6Address=`echo "${ipDeviceInfo}" | awk '$1 == "inet6" && $4 == "global" {print $2; exit}'`



isV4Dynamic=`echo "${ipDeviceInfo}" | awk '$1 == "inet" {print $7; exit}'`
isV6Dynamic=`echo "${ipDeviceInfo}" | awk '$1 == "inet6" && $4 == "global" {print $6; exit}'`
v4Mode="static"
v6Mode="static"

if [ "${isV4Dynamic}" = "dynamic" ]; then
    v4Mode="DHCP"
elif [ "${isV4Dynamic}" = "" ]; then
    v4Mode=""
else
    v4Mode="STATIC"
fi
if [ "${isV6Dynamic}" = "dynamic" ]; then
    v6Mode="DHCP"
elif [ "${isV6Dynamic}" = "" ]; then
    v6Mode=""
else
    v6Mode="STATIC"
fi

if [ "${dev}" = "" ]; then
    isinterfaceEnabled="false"
else
    isinterfaceEnabled="true"
fi

devPath="/sys/class/net/"${dev}"/"
speed=`cat ${devPath}speed`
mac=`cat  ${devPath}address`
duplex=`cat  ${devPath}duplex`       # full or half
operstate=`cat  ${devPath}operstate` # up or down
if [ "${duplex}" = "full" ]; then
    isfullduplex="true"
else
    isfullduplex="false"
fi
if [ "${operstate}" = "up" ]; then
    linkstatus="LinkUp"
elif [ "${operstate}" = "down" ]; then
    linkstatus="LinkDown"
else
    linkstatus="NoLink"
fi

hostname=`hostname`
fqdn=`hostname -f`

isautoneg="true"
  

echo "{"
echo "    \"Device\": " "\"${dev}\","
echo "    \"Name\": " "\"${dev}\","
echo "    \"Id\": " "\"${id}\","
echo "    \"SpeedMbps\": " "\"${speed}\","
echo "    \"InterfaceEnabled\": " "${isinterfaceEnabled},"
echo "    \"EthDevice\": " "\"${dev}\","
echo "    \"MACAddress\": " "\"${mac}\","
echo "    \"PermanentMACAddress\": " "\"${mac}\","
echo "    \"IPV4Address\": " "\"${ipv4Address}\","
echo "    \"IPV6Address\": " "\"${ipv6Address}\","
echo "    \"IPV4Origin\": " "\"${v4Mode}\","
echo "    \"IPV6Origin\": " "\"${v6Mode}\","
echo "    \"Gateway\": " "\"${gateway}\","
echo "    \"HostName\": " "\"${hostname}\","
echo "    \"FQDN\": " "\"${fqdn}\","
echo "    \"LinkStatus\": " "\"${linkstatus}\","
echo "    \"FullDuplex\": " "${isfullduplex},"
echo "    \"AutoNeg\": " "${isautoneg}"
echo "}"

exit 0


