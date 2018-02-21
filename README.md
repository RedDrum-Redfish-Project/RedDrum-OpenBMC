# RedDrum-OpenBMC  
A python based Redfish service for the OpenBMC using the RedDrum Redfish Service

## About ***RedDrum-OpenBMC***

***RedDrum-OpenBMC*** is a python app that leverages the RedDrum-Frontend and implements a Redfish Service for an OpenBMC platform comformant eith the OCP Base Server Profile.

As a RedDrum Redfish Service implementation, the Frontend is implemented by RedDrum-Frontend.
* see RedDrum-Frontend/README.md and RedDrum-Frontend/reddrum_frontend/README.txt for details

The OpenBMC Backend  is implemented as a package from this  repo -- named **reddrum_openbmc**

The RedDrum-OpenBMC/***RedDrumObmcMain.py*** startup script (also in scripts dir) implements the calls to the frontend
and backend to start-up the service.

## RedDrum-OpenBMC Feature Level
The RedDRum-OpenBMC service strives to implement a feature level compatible with the OCP Base Server Profile
* Mandatory OCP Base Server Profile features are all implemented
* Some Recommended features are implemented
* a few features beyond the recommended level may be implemented


## About the ***RedDrum Redfish Project***
The ***RedDrum Redfish Project*** includes several github repos for implementing python Redfish servers.
* RedDrum-Frontend  -- the Redfish Service Frontend that implements the Redfish protocol and common service APIs
* RedDrum-Httpd-Configs -- docs and setup scripts to integrate RedDrum with common httpd servers eg Apache and NGNX
* RedDrum-OpenBMC -- a "high-fidelity" simulator built on RedDrum with several feature profiles and server configs
* RedDrum-OpenBMC -- a RedDrum Redfish service integrated with the OpenBMC platform

## Architecture 
RedDrum Redfish Service Architecture breaks the Redfish service into three parts:
* A standard httpd service
  * The RedDrum-OpenBMC initial base implementation uses an Apache httpd to implement a reverse proxy to the RedDrum-Frontend
  * A virtual server is defined for both http(port 80) and https on port xxx. 
    * port 443 is claimed by the Gevent serivce so the Redfish serivce currently is not able to listen on 443.
    * instead, we implemented the https on port xxx.
  * The Reverse Proxy Config directs Apache to reverse-proxy all incoming http[s] requests having URIs starting with `/redfish` reverse proxied" to the RedDrum-Frontend using http
  * The RedDrum-Frontend listens on http:<127.0.0.1:5001> (localhost port 5001 http) and only processes defined URIs
  * SSL is handled by Apache and reverse proxied over to the RedDrum-Frontend as an internal http connection
    * SEE RedDrum-Redfish-Project/RedDrum-Httpd-Config  Repo for description of how to configure Apache 
  * we are investigating integration with the egvent service so that the RedDrum can share https on port 443

* The RedDrum-Frontend -- the implementation independent frontend code is implemented leveraging RedDrum-Frontend 
  * All authentication is implemented by the Frontend
  * The Redfish protocol is implemented by the Frontend -- along with the AccountService, SessionService, rootService,
and top-level APIs for JsonSchemas, Registries, odata, and $metadata
  * the frontend is single threaded but blazing fast since much of the data is cached in the frontend dictionaries

* RedDrum Backend -- The backend implementation-depended interfaces to the real hardware resources
  * The full Backend code for the RedDrum-OpenBMC is included in this repo in package reddrum_openbmc

* The `redDrumObmcMain.py` Startup Script -- used to start the service.  uses APIs to the Frontend and Backend to initialize Resource,
initiate HW resource discovery, and Startup the Frontend Flask app.
  * the RedDrumObmcMain.py scriptoes this for the OpenBMC service

## Conformance Testing
Re-running of SPMF conformance tests is currently in progress.
(earlier versions  of the Simulator and conformance tests passed on the RedDrum-Simulator so generally the OpenBMC service should also pass.
* List of DMTF/SPMF Conformance tools being used:
  * Mockup-Creator
  * Service-Validator
  * JsonSchema-Response-Validator
  * Conformance-Check
  * (new) Ocp Base Server Profile Tester

* RedDrum-specific tests (not yet open sourced)
  * RedDrum-URI-Tester -- tests against all supported URIs for specific simulator profiles
  * RedDrum-Stress-Tester -- runs 1000s of simultaneous requests in parallel

---
## How to Install the RedDrum-OpenBMC on Centos7.1+-- to test with BackendStubs enabled for Linux Testing
#### Manual Install from git clone
* Install on Centos7.1 or later Linux system
* Install and configure the Apache httpd 

```
     yum install httpd
     cd  <your_path_to_Directory_Holding_RedDrumOpenBMC_Code>
     mkdir RedDrumSim
     git clone https://github.com RedDrum-Redfish-Project/RedDrum-Httpd-Configs RedDrum-Httpd-Configs
     cd RedDrum-Httpd-Configs/Apache-ReverseProxy
     ./subSystem_config.sh # creates a httpd.conf file in etc/httpd and creates self-signed ssl certificates
```

* Install the RedDrum-Frontend code

```
     cd  <your_path_to_Directory_Holding_RedDrumOpenBMC_Code>
     git clone http://github.com/RedDrum-Redfish-Project/RedDrum-Frontend  RedDrum-Frontend
```

* Install the RedDrum-OpenBMC code

```
     cd  <your_path_to_Directory_Holding_RedDrumOpenBMC_Code>
     git clone http://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC  RedDrum-OpenBMC  
```

#### Install using `pip install` from github (currently testing)
* ***currently verifying that installing directly from github using pip install***

#### Install using `pip install` from pypi (not working yet)


### How to Start  the RedDrum-OpenBMC

```
     cd  <your_path_to_Directory_Holding_RedDrumOpenBMC_Code>/RedDrum-OpenBMC/scripts
     ./runRedDrumStubs       # to run with Backend Stubs enables so that the Dbus calls are stubbed out
     ./redRedDrum            # to run on a real OpenBMC BMC where real Dbus calls are used to get HW info
```

### How to Clear Data Caches
The RedDrum Frontend keeps resource data for non-volatile resource models cached in files, so if you add/delete users, change passwords, set AssetTags, etc, the changes will persist stopping and re-starting the simulator
* To clear all data caches to defaults and also clear python caches, run:
  * NOTE that IF YOU CHANGE Simulation Data, you must clear the caches for the changes to appear.

```
     cd  <your_path_to_Directory_Holding_RedDrumOpenBMC_Code>/RedDrum-OpenBMC/scripts
     ./clearCaches
```

---
