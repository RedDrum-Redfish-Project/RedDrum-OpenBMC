#!/bin/sh
# Copyright Notice:
#    Copyright 2018 Dell, Inc. All rights reserved.
#    License: BSD License.  For full license text see link: https://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC/LICENSE.txt

debug="$1"

# get the route info and extract the devicename and gateway from the route info
#netstatinfo=`netstat -tlp`
netstatinfo=`netstat -tl`
mysshPort=`echo "${netstatinfo}" | awk '/ssh/ {print $4; exit }'`
myhttpPort=`echo "${netstatinfo}" | awk '/http/ {print $4; exit }'`
myhttpsPort=`echo "${netstatinfo}" | awk '/https/ {print $4; exit }'`
myeePort=`echo "${netstatinfo}" | awk '/ee/ {print $4; exit }'`
myhostname=`hostname`
myfqdn=`hostname -f`

sshEnabled="False"
httpEnabled="False"
httpsEnabled="False"
eeEnabled="False"

if [ "${mysshPort}" != "" ]; then
    sshEnabled="True"
fi
if [ "${myhttpPort}" != "" ]; then
    httpEnabled="True"
fi
if [ "${myhttpsPort}" != "" ]; then
    httpsEnabled="True"
fi
if [ "${myeePort}" != "" ]; then
    eeEnabled="True"
fi

if [ "${debug}" == "debug" ]; then
    echo "-----------------------------------"
    echo "DEBUG: "
    #echo "netstate: " "$netstatinfo"
    echo "SSH:   "  "${sshEnabled}"
    echo "HTTP:  "  "${httpEnabled}"
    echo "HTTPS: "  "${httpsEnabled}"
    echo "EE:    "  "${eeEnabled}"
    echo "HostName: " "${myhostname}"
    echo "FQDN:     " "${myfqdn}"
    echo "-----------------------------------"
    exit 1
fi

echo "{"
echo "    \"SSH\":   { \"ProtocolEnabled\": " "\"${sshEnabled}\" },"
echo "    \"HTTP\":  { \"ProtocolEnabled\": " "\"${httpEnabled}\" },"
echo "    \"HTTPS\": { \"ProtocolEnabled\": " "\"${httpsEnabled}\" },"
echo "    \"HostName\": " "\"${myhostname}\","
echo "    \"FQDN\": " "\"${myfqdn}\""
echo "}"

exit 0
