


This is the Backend RedDrum implementation for the OpenBMC 

The code implements all of the APIs required by the RedDrum-Frontend and maps the RedDrum frontend APIs
to OpenBMC Dbus calls or Linux calls.

Backend data that does not change (eg BMC Firmware Version) is read into the Frontend databases during 
Resource Discovery.

Backend data that can change (eg Server PowerState) is obtained on-demand when needed to process an API
that must return that information.
   The Frontend code requests the backend to update a specific database,
   Backend code executes dbus or Linux calls to get all of the required information,
   then the frontend returns the API in the proper Redfish formats.

Standard Backend API Handlers:
  The backendRoot.py,  chassisBackend.py,   managersBackend.py,  and systemsBackend.py
  implement the standard interfaces to the RedDrum-Frontend code, but have special processing that
  is specific to the openBMC backend.   

  obmcDiscovery.py is called by the discovery interfadces in backendRoot.py to build the discovery time resources.

  The standard Backend API handlers then call the low-level API handlers to get the actual data:

Low-Level Backend API Handlers:
  obmcLinuxInterfaces.py has low-level interfaces used to get data from Linux

  obmcStaticConfig.py implements some statically defined properties eg systemId, chassisId and may
     be considered an implementation specific config file if there is a need to customize these.

  obmcDbusInterfaces.py has mid-level interfaces used to get data that comes from dbus queries
     It calls process.py methods to implement actual dbus calls to get data from open BMC Dbus.    


