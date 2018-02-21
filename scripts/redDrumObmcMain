#!/usr/bin/python
# Copyright Notice:
#    Copyright 2018 Dell, Inc. All rights reserved.
#    License: BSD License.  For full license text see link: https://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC/LICENSE.txt

# **** Run  RedDrum OpenBMC Backend Service
# ****  python3.4  redDrumMain.py --Target=OpenBMC
#
# **** Install directly from github by:
#    cd yourPath
#    git https://RedDrumRedfish/RedDrum-Frontend  RedDrum-Frontend
#    git https://RedDrumRedfish/RedDrum-OpenBMC   RedDrum-OpenBMC  
#    cd RedDrum-OpenBMC  
#    ./runRedDrum 
#
# This program is dependent on the following Python packages that should be installed separately with pip:
#    pip install Flask
#    pip install passlib=v1.7.1
#
# standard python packages
import sys
import os
import getopt
import inspect

def rdUsage(rdProgram):
    print("Usage:")
    print("   {}:    [-Vh][--Version][--help] ".format(rdProgram))
    print("   {}:    [--Host=<hostIP>][--Port=<port>] ".format(rdProgram))
    return(0)

def rdHelp(rdProgram, rdVersion):
    print("Version: {}".format(rdVersion))
    rdUsage(rdProgram)
    print("")
    print("       -V,      --Version     --- prints the RedDrum program version and exits")
    print("       -h,      --help,       --- prints usage and exits ")
    print("       -L       --Local       --- run using resource cache files and RedDrum.conf file paths below current dir for testing")
    print("                                  if -L, the Debug option is automatically invoked")
    print("       -D       --Debug       --- print debug messages on Flask console for each API executed")
    print("       --Host=<hostIp>        --- host IP address. dflt=127.0.0.1")
    print("       --Port=<port>          --- the port to use. dflt=5001")
    print("       --EnableBackendStubs   --- for testing on Linux, run using stub code in Backend instead of real dbus calls")
    print("")
    return(0)


def main(argv):
    #set default option args
    rdProgram="RedDrum"
    rdServiceName="RedDrumService"
    rdHost="127.0.0.1"
    rdPort=5001
    isLocal=False
    debug=False
    rdTarget="OpenBMC"
    rdVersion="0.9.5"
    rdProfile=""
    enableBackendStubs=False
    startupMsgSuffix=""

    try:
        opts, args = getopt.getopt(argv[1:],"VhLD", ["Version", "help", "Debug", "Local", "Host=", "Port=", "EnableBackendStubs"  ])
    except getopt.GetoptError:
        print(" {}: Error parsing options".format(rdProgram))
        rdUsage(rdProgram)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            rdHelp(rdProgram,rdVersion)
            sys.exit(0)
        elif opt in ("-V", "--Version"):
            print("Version: {}".format(rdVersion))
            sys.exit(0)
        elif opt in ("-D", "--Debug"):
            debug=True
        elif opt in ("-L", "--Local"):
            isLocal=True
            debug=True
        elif opt in ("--Host="):
            rdHost=arg
        elif opt in ("--Port="):
            rdPort=int(arg)
        elif opt in ("--EnableBackendStubs"):
            enableBackendStubs=True
            startupMsgSuffix=" -- using backend stubs enabled for testing"
        else:
            print(" {}: Error: unsupported option".format(rdProgram))
            rdUsage(rdProgram)
            sys.exit(3)

    print("Running RedDrum OpenBMC Service From Main {}".format(startupMsgSuffix))
    sys.stdout.flush()

    # start the service.   Returns if control-C
    redDrumMain(rdHost=rdHost, rdPort=rdPort, isLocal=isLocal, debug=debug, rdServiceName=rdServiceName, rdTarget=rdTarget, 
                rdVersion=rdVersion, rdProfile=rdProfile, enableBackendStubs=enableBackendStubs)


    print("Exiting RedDrum Service From Main Console")
    sys.exit(0)




def redDrumMain(rdHost="127.0.0.1", rdPort=5001, isLocal=False, debug=False, rdServiceName="RedDrumService", rdTarget="", 
                rdVersion="0.9.5", rdProfile="", enableBackendStubs=False):

    # create instance of RedDrum root data object 
    # this includes method logMsg used to print messages and integrate with the logger
    #   logMsg is called with syntax: 
    #      rdr=RdRootData()
    #      rdr.logMsg(sev,"message")  # where sev= "INFO" "WARNING" "ERROR" "CRITICAL" "DEBUG"
    #

    # ***********************************
    # *** EDIT THIS TO PUT THE " RedDrum-Frontend " package in the Python Path:
    # ******** for now, we will add a path to ../RedDrum-Frontend  
    cwd=os.getcwd()
    defaultFrontendPath=os.path.abspath(os.path.join(cwd,"..","RedDrum-Frontend"))
    sys.path.append(defaultFrontendPath)
    # *** end create path to the Frontend
    # ***********************************

    # now import the FrontEnd
    from reddrum_frontend import RdRootData   # import the RedDrum Root Data Structure and logMsg Method
    rdr=RdRootData()

    # now calculate the directory path to the FrontEnd Package Directory which has /reddrum_frontend 
    # this works even if the Frontend package above was put in site-packages
    rdr.frontEndDirPath=os.path.abspath(os.path.join(os.path.dirname( inspect.getfile(RdRootData)), ".."))
    #print("EEEEEEEEEEEEEEEE DIR: frontend dir: {}".format(rdr.frontEndDirPath))

    # initialize root data with passed-in args
    rdr.rdHost=rdHost                  # the dflt is 127.0.0.1
    rdr.rdPort=rdPort                  # the dflt is 5001
    rdr.isLocal=isLocal                # the dflt is False
    rdr.debug=debug                    # the dflt is False
    rdr.rdServiceName=rdServiceName    # the default is "RedDrumService"
    rdr.rdTarget=rdTarget              # when run from here, the target is not used
    rdr.rdProfile=rdProfile            # when run from here, the target is not used
    rdr.enableBackendStubs=enableBackendStubs # use stub code in backend for testing

    # initialize root data with other constants
    rdr.rdVersion=rdVersion            # the default is "0.9.0" -- the current RedDrum version

    # if the service is not running as a local app for debug, start a syslog logger
    # RdLogger is the RedDrum built-in Linux syslog logger
    # if you want to create your own, copy the front-end of the RdLogger code and then import your own
    # if you don't set rdr.logger=RdLogger() or your custom logger, then messages are not logged
    loggerName="None"
    if rdr.isLocal is not True:     
        from RedfishService import RdLogger         # import the default RedDrum logger
        rdr.rdLogger = RdLogger(rdr.rdServiceName)   # dflt rdLogger=None
        loggerName="RdLogger"


    # if running as a local app, enable printing messages on the local console. default is False
    # if rdr.printLogMsgs=True, then the service will print msgs to stdout/stderr for the service
    if rdr.isLocal is True:     
        rdr.printLogMsgs=True     # dflt is False

    # Print startup message -- goes to log if rdr.logger is set, or console if printLogMsgs=true
    rdr.logMsg("INFO"," Starting RedDrum RedfishService version: {} at IP: {}:{} as {}".format(rdr.rdVersion,rdHost,rdPort,rdr.rdServiceName))
    rdr.logMsg("INFO","    loggerName: {}, printLogMsgs: {}, isLocal:{}".format(loggerName, rdr.printLogMsgs, rdr.isLocal))
    rdr.logMsg("INFO","    loggerName: {}, printLogMsgs: {}, isLocal:{}".format(loggerName, rdr.printLogMsgs, rdr.isLocal))
    rdr.logMsg("INFO","    Using Front-end at dir path:  {}".format(rdr.frontEndDirPath))


    # Startup the Backend
    # This also initiallizes backend resource classes 
    #    and initializes the file paths:  baseDataPath, varDataPath, RedDrumConfPath   based on the target
    # RedDrum currently has three backends defined.   Others can be defined using Sim_Backend as a template
    # the backends are: "Simulator","OpenBMC", "RackManager", and "" used here for testing the Frontend
    from reddrum_openbmc import RedDrumBackend  

    rdr.logMsg("INFO"," Initializing {} Backend".format(rdr.rdTarget))
    rdr.backend=RedDrumBackend(rdr)

    # update the paths (baseDataPath, varDataPath, RedDrumConfPath) and config if isLocal is set true 
    if rdr.isLocal is True:     
        rdr.logMsg("INFO","   RedDrumMain.py:  setting config and paths for Local Execution")
        rdr.setLocalPaths()

    # Now update the root data with any data stored in the RedDrum.conf config file
    #    This includes the config parameteers for Authentication and header processing
    #    Anything from RedDrum.conf can be OVER_WRITTEN by Backend start code!
    rc = rdr.readRedDrumConfFile()
    if rc != 0:
        rdr.logMsg("CRITICAL","   RedDrumMain.py:  Error reading RedDrum.conf file.   exiting")
        sys.exit(9)


    # import the RedfishService front-end root service class 
    #     this instantiates all of the Front-end RedfishService resources--all resource live "under" the ServiceRoot
    from reddrum_frontend import RfServiceRoot
    
    # import the API to start the Main RedDrum Redfish Service Flask app 
    #     this is a function in ./RedfishService/FlaskApp/redfishURIs.py
    # import the API to start the Main RedDrum Redfish Service Flask app 
    #     this is a function in ./RedfishService/FlaskApp/redfishURIs.py
    #     It loads the flask APIs (URIs), and starts the flask service
    from reddrum_frontend  import rdStart_RedDrum_Flask_app

    # Now create the root service resource object
    #     This will create Python dictionary for all resources under the root service 
    #     It also runs phase-1 discovery 
    rdr.logMsg("INFO"," Initializing Frontend ServiceRoot ")
    rdr.root=RfServiceRoot(rdr )

    # run startup discovery
    #   this discovers resources and loads them into the Front-end data cache.
    #   For the Frontend test, no resource data is actually loaded
    rdr.logMsg("INFO"," Running Startup Resource Discovery")
    rdr.backend.runStartupDiscovery(rdr)

    # start the RedDrum Flask app 
    #     This does not return unless the Flask App exits
    #     Once this is called, Flask is handling Fron-end APIs from user
    rdr.logMsg("INFO"," Starting Flask App ")
    rdStart_RedDrum_Flask_app(rdr)


if __name__ == "__main__":
    main(sys.argv)

