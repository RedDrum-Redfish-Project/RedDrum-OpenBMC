# RedDrum-OpenBMC  
A python based Redfish service for the OpenBMC using the RedDrum Redfish Service

## About ***RedDrum-OpenBMC***

***RedDrum-OpenBMC*** is a python app that leverages the RedDrum-Frontend and implements a Redfish Service for an OpenBMC platform comformant eith the OCP Base Server Profile.

As a RedDrum Redfish Service implementation: 
* The ***Frontend*** is implemented by RedDrum-Frontend and the package name is **reddrum_frontend**
  * see RedDrum-Redfish-Project/RedDrum-Frontend/README.md and RedDrum-Frontend/reddrum_frontend/README.txt for details

* The ***Backend***  is implemented as a package from this  repo (RedDrum-OpenBMC) -- named **reddrum_openbmc**

* The ***Httpd Config*** is implemented with Apache2 and configured by running setup scripts from RedDrum-Httpd-Configs/OpenBMC-Apache2-ReverseProxy

* The ***RedDrum-OpenBMC/RedDrumObmcMain.py*** startup script (also in scripts dir) implements the calls to the frontend
and backend to start-up the service.

* The ***RedDrum-OpenBMC/reddrum_yocto_recipes*** directory contains OpenBMC Yocto "recipes" to include the RedDrum-Frontend, RedDrum-OpenBMC (backend), and RedDrum-Httpd-Configs (config scripts)

* The ***RedDrum-OpenBMC/reddrum_yocto_patches*** directory contains git patch files to update OpenBMC build

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
SEE: github.com/RedDrum-Redfish-Project/RedDrum-Frontend/README.md for description of the architecture
RedDrum Redfish Service Architecture breaks the Redfish service into three parts:
* A standard httpd service
* The RedDrum-Frontend -- the implementation independent frontend code is implemented leveraging RedDrum-Frontend 
* RedDrum Backend -- The backend implementation-depended interfaces to the real hardware resources
  * The full Backend code for the RedDrum-OpenBMC is included in this repo in package reddrum_openbmc
* The `redDrumObmcMain.py` Startup Script -- used to start the service.  It uses APIs to the Frontend and Backend to initialize Resource, initiate HW resource discovery, and Startup the Frontend Flask app.
  * the RedDrumObmcMain.py script is in this repo for the OpenBMC service

## Conformance Testing
Re-running of SPMF conformance tests is currently in progress.
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
---
# HOWTO Create and Install a RedDrum Redfish Image on a real OpenBMC #
***NOTE:  This generates a 25MB rootfs file system***
* this will not  fit on some OpenBMC systems that have only 32MB of total Flash due  to flash size limitation. 
* it fits ok on BMCs with 64MB or more flash space
* for testing and integration on systems with only 32MB, ***we are running an image from the RAM by tftp'ing it to BMC uboot***

## Get the `openbmc`, `meta-openembedded` and  RedDrum-OpenBMC Repos ##
```
git clone git@github.com:openbmc/openbmc.git
git clone git@github.com:openembedded/meta-openembedded.git
git clone git@github.com:RedDrum-Redfish-Project/RedDrum-OpenBMC.git

```

## Update the OpenBMC recipes ##
* Update `passlib` recipe
```
cp meta-openembedded/meta-python/recipes-devtools/python/python-passlib.inc \
openbmc/import-layers/meta-openembedded/meta-python/recipes-devtools/python/

cp meta-openembedded/meta-python/recipes-devtools/python/python3-passlib_1.7.1.bb \
openbmc/import-layers/meta-openembedded/meta-python/recipes-devtools/python/
```
* Add `pytz` recipe
```
cp meta-openembedded/meta-python/recipes-devtools/python/python-pytz.inc \
openbmc/import-layers/meta-openembedded/meta-python/recipes-devtools/python/

cp meta-openembedded/meta-python/recipes-devtools/python/python3-pytz_2018.3.bb \
openbmc/import-layers/meta-openembedded/meta-python/recipes-devtools/python/
```
* Add `redfish` Recipes
```
cp -r RedDrum-OpenBMC/reddrum_yocto_recipes  openbmc/meta-phosphor/common/recipes-phosphor/
```
* Update `bblayers.conf.sample`
```
git apply RedDrum-OpenBMC/reddrum_yocto_patches/bblayers.conf.sample.patch
```
* Update `obmc-phosphor-image.bbclass`
```
git apply RedDrum-OpenBMC/reddrum_yocto_patches/obmc-phosphor-image-bbclass.patch
```

## Target your hardware and build ##
```
cd openbmc
export TEMPLATECONF=meta-openbmc-machines/meta-openpower/meta-ibm/meta-witherspoon/conf
. openbmc-env
bitbake obmc-phosphor-image
```

## Run BMC image from RAM using uboot ##
* The following instructions are for a ***Power9 Witherspoon*** 
  * Update the machine type and load addresses suitably specific to other platforms...
* Copy `fitImage` and `obmc-phosphor-image-witherspoon.cpio.lzma.u-boot` found at `openbmc/build/tmp/deploy/images/witherspoon/` to a TFTP Server that can be reached by OpenBMC Uboot
* At OpenBMC Uboot prompt:

```
ast# setenv ethaddr aa:bb:cc:dd:ee:ff
ast# setenv serverip <TFTP Server's IP Address>
ast# tftp 0x93000000 fitImage
ast# tftp 0x94000000 obmc-phosphor-image-witherspoon.cpio.lzma.u-boot
ast# bootm 0x93000000 0x94000000
```

## Login to BMC ##
* Setup httpd.conf, ssl.conf, and create/install Self Signed Certificates, and start Apache
  * ***NOTE: This sets configures Apache to use port 5050 for HTTPS***
  * This is because Obc Gevent has already claimed port 443 for the dbus browser
  * long-term, we need to merge these be behind the same base httpd
```
root@witherspoon:~# obmcApache2Httpd_config.sh
Generating RSA private key, 2048 bit long modulus
.+++
....+++
e is 65537 (0x10001)
Signature ok
subject=/C=US/ST=TX/L=Round Rock/O=Dell Inc./OU=ESI/CN=OpenBMCx
Getting Private key
httpd config complete
```
* Start RedDrum Redfish Server 
  * Note Again:  httpd is using port 80 for http and (currently) ***port 5050 for https*** 
```
root@witherspoon:~# python3 /usr/bin/redDrumObmcMain
```
---
---
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
     # now use pip to install this into your local site-packages
     cd ..
     # now dir is at <your_path_to_Directory_Holding_RedDrumOpenBMC_Code>  
     pip install -e ./RedDrum-Frontend
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
