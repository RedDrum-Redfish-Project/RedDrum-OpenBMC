# Copyright Notice:
#    Copyright 2018 Dell, Inc. All rights reserved.
#    License: BSD License.  For full license text see link: https://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC/LICENSE.txt

import dbus
import obmc.mapper
import sys
import re
import yaml

BMC_SUBPATH = '/xyz/openbmc_project'
CONFIG_YML = '/usr/share/RedDrum-Redfish/config.yml'

HOST_INDEX = 0
INTERFACE_INDEX = 1
OBJPATH_INDEX = 2
PROPERTY_INDEX = 3

"""

{property_key1:[property1_Host_string, property1_interface_string, property1_ObjPath_string, property1],
 property_key2:[property2_Host_string, property2_interface_string, property2_ObjPath_string, property2],
...}

NOTE: self.lookupValues provides the necessary DBus Object Name, Interface, Object Path and Property name.

      1. propertyX_interface_string and propertyX are a Must.
      2. propertyX_Host_string and propertyX_ObjPath_string are optional.
      3. When propertyX_Host_string and propertyX_ObjPath_string are specified, proxy object lookup is faster.
      4. When propertyX_Host_string and propertyX_ObjPath_string are NOT specified, proxy object lookup is slower
          as a subtree lookup on /xyz/openbmc_project is enumerated to find a list of objects and corresponding interfaces.
          Then a matching interface and path is looked up.

"""

class ProcessDbus():
    def __init__(self):
        self.conn = dbus.SystemBus()
        self.mapper = obmc.mapper.Mapper(self.conn)
        self.lookupValues = {}
        self.processYAML()

    def processYAML(self):
        with open(CONFIG_YML, 'r') as ymlFile:
            config = yaml.load(ymlFile)
        for key in list(config.keys()):
            self.lookupValues.update({key:[config[key]['objname'], config[key]['interface'], config[key]['objpath'], config[key]['property']]})

    def get_bmc_fw_ver(self):
        try:
            obj = self.conn.get_object('xyz.openbmc_project.Software.BMC.Updater', '/xyz/openbmc_project/software', introspect=False)
            iface = dbus.Interface(obj, dbus.PROPERTIES_IFACE)
            for a in iface.Get('org.openbmc.Associations', 'associations'):
                if a[0] == 'functional':
                    obj1 = self.conn.get_object('xyz.openbmc_project.Software.BMC.Updater', a[2],  introspect=False)
                    iface1 = dbus.Interface(obj1, dbus.PROPERTIES_IFACE)
                    if re.search('BMC', iface1.Get('xyz.openbmc_project.Software.Version', 'Purpose')):
                        return iface1.Get('xyz.openbmc_project.Software.Version', 'Version')
        except Exception as e:
            print(e)
            return

    def get_bios_fw_ver(self):
        try:
            obj = self.conn.get_object('org.open_power.Software.Host.Updater', '/xyz/openbmc_project/software', introspect=False)
            iface = dbus.Interface(obj, dbus.PROPERTIES_IFACE)
            for a in iface.Get('org.openbmc.Associations', 'associations'):
                if a[0] == 'functional':
                    obj1 = self.conn.get_object('org.open_power.Software.Host.Updater', a[2],  introspect=False)
                    iface1 = dbus.Interface(obj1, dbus.PROPERTIES_IFACE)
                    if re.search('Host', iface1.Get('xyz.openbmc_project.Software.Version', 'Purpose')):
                        return iface1.Get('xyz.openbmc_project.Software.Version', 'Version')
        except Exception as e:
            print(e)
            return

    def get_dimm_nums(self):
        dimm_num = 0
        max_dimm = 0
        resp = dict()
        try:
            bus = self.mapper.get_subtree(self.lookupValues['CHASSIS_DIMM_PRES'][OBJPATH_INDEX])
            for path, info in list(bus.items()):
                if re.search('dimm[0-9][0-9]$', path) or re.search('dimm[0-9]$', path):
                    max_dimm = max_dimm + 1
                    for host, ifaces in list(info.items()):
                        obj = self.conn.get_object(host, path, introspect=False)
                        iface = dbus.Interface(obj, dbus.PROPERTIES_IFACE)
                        dimm_pres = iface.Get(self.lookupValues['CHASSIS_DIMM_PRES'][INTERFACE_INDEX], self.lookupValues['CHASSIS_DIMM_PRES'][PROPERTY_INDEX])
                        if dimm_pres == dbus.Boolean(True, variant_level=1):
                            dimm_num = dimm_num + 1
            resp['MaxNumOfDIMMs'] = max_dimm
            resp['MinNumOfDIMMs'] = 1
            resp['PresNumOfDIMMs'] = dimm_num
            return resp
        except Exception as e:
            print(e)
            return {'MaxNumOfDIMMs': 0, 'MinNumOfDIMMs': 0, 'PresNumOfDIMMs': 0}

    def get_psu_nums(self):
        psu_num = 0
        max_psu = 0
        resp = dict()
        resp['MaxNumOfPSUs'] = max_psu
        resp['MinNumOfPSUs'] = 1
        try:
            bus = self.mapper.get_subtree(self.lookupValues['CHASSIS_PSU_PRES'][OBJPATH_INDEX])
            for path, info in list(bus.items()):
                if re.search('powersupply[0-9][0-9]$', path) or re.search('powersupply[0-9]$', path):
                    max_psu = max_psu + 1
                    for host, ifaces in list(info.items()):
                        obj = self.conn.get_object(host, path, introspect=False)
                        iface = dbus.Interface(obj, dbus.PROPERTIES_IFACE)
                        psu_pres = iface.Get(self.lookupValues['CHASSIS_PSU_PRES'][INTERFACE_INDEX], self.lookupValues['CHASSIS_PSU_PRES'][PROPERTY_INDEX])
                        if psu_pres == dbus.Boolean(True, variant_level=1):
                            psu_num = psu_num + 1
            resp['MaxNumOfPSUs'] = max_psu
            resp['MinNumOfPSUs'] = 1
            resp['PresNumOfPSUs'] = psu_num
            return resp
        except Exception as e:
            print(e)
            return {'MaxNumOfPSUs': 0, 'MinNumOfPSUs': 0,  'PSU0present': False, 'PSU1present': False}

    def get_cpu_nums(self):
        cpu_num = 0
        max_cpu = 0
        resp = dict()
        try:
            bus = self.mapper.get_subtree(self.lookupValues['CHASSIS_CPU_PRES'][OBJPATH_INDEX])
            for path, info in list(bus.items()):
                if re.search('cpu[0-9][0-9]$', path) or re.search('cpu[0-9]$', path):
                    max_cpu = max_cpu + 1
                    for host, ifaces in list(info.items()):
                        obj = self.conn.get_object(host, path, introspect=False)
                        iface = dbus.Interface(obj, dbus.PROPERTIES_IFACE)
                        psu_pres = iface.Get(self.lookupValues['CHASSIS_CPU_PRES'][INTERFACE_INDEX], self.lookupValues['CHASSIS_CPU_PRES'][PROPERTY_INDEX])
                        if psu_pres == dbus.Boolean(True, variant_level=1):
                            cpu_num = cpu_num + 1
            resp['MaxNumOfCPUs'] = max_cpu
            resp['MinNumOfCPUs'] = 1
            resp['PresNumOfCPUs'] = cpu_num
            return resp
        except Exception as e:
            print(e)
            return {'MaxNumOfCPUs': 0, 'MinNumOfCPUs': 0, 'PresNumOfCPUs': 0}


                    
    def get_prop_for_interface(self, interface, prop, Host=None, objpath=None):
        try:
            if objpath and Host:
                obj = self.conn.get_object(Host, objpath, introspect=False)
                iface = dbus.Interface(obj, dbus.PROPERTIES_IFACE)
                return iface.Get(interface, prop)
            else:
                bus = self.mapper.get_subtree(BMC_SUBPATH)
                for path, info in list(bus.items()):
                    for host, ifaces in list(info.items()):
                        obj = self.conn.get_object(host, path, introspect=False)
                        iface = dbus.Interface(obj, dbus.PROPERTIES_IFACE)
                        if interface in ifaces:
                            if objpath:
                                if objpath == path:
                                    return iface.Get(interface, prop)
                            else:
                                return iface.Get(interface, prop)
        except Exception as e:
            print(e)
            return

    def set_prop_for_interface(self, interface, prop, val, Host=None, objpath=None):
        try:
            if objpath and Host:
                obj = self.conn.get_object(Host, objpath, introspect=False)
                iface = dbus.Interface(obj, dbus.PROPERTIES_IFACE)
                return iface.Set(interface, prop, val)
            else:
                bus = self.mapper.get_subtree(BMC_SUBPATH)
                for path, info in list(bus.items()):
                    for host, ifaces in list(info.items()):
                        obj = self.conn.get_object(host, path, introspect=False)
                        iface = dbus.Interface(obj, dbus.PROPERTIES_IFACE)
                        if interface in ifaces:
                            if objpath:
                                if objpath == path:
                                    iface.Set(interface, prop, val)
                            else:
                                iface.Set(interface, prop, val)
        except Exception as e:
            print(e)
            return

    
    def get_bmc_state(self):
        """
        [(dbus.String(u'RequestedBMCTransition'), dbus.String(u'xyz.openbmc_project.State.BMC.Transition.None', variant_level=1))]
        [(dbus.String(u'CurrentBMCState'), dbus.String(u'xyz.openbmc_project.State.BMC.BMCState.Ready', variant_level=1))]
        """
        return self.get_prop_for_interface(prop=self.lookupValues['BMC_STATE'][PROPERTY_INDEX], Host=self.lookupValues['BMC_STATE'][HOST_INDEX], interface=self.lookupValues['BMC_STATE'][INTERFACE_INDEX], objpath=self.lookupValues['BMC_STATE'][OBJPATH_INDEX])
    
    def reset_bmc(self):
        """
        [(dbus.String(u'RequestedBMCTransition'), dbus.String(u'xyz.openbmc_project.State.BMC.Transition.Reebot', variant_level=1)),]
        """
        p = dbus.String(self.lookupValues['RESET_BMC_STATE'][PROPERTY_INDEX])
        v = dbus.String('xyz.openbmc_project.State.BMC.Transition.Reboot', variant_level=1)
        self.set_prop_for_interface(prop=p, value=v, Host=self.lookupValues['RESET_BMC_STATE'][HOST_INDEX], interface=self.lookupValues['RESET_BMC_STATE'][INTERFACE_INDEX], objpath=self.lookupValues['RESET_BMC_STATE'][OBJPATH_INDEX])
    
    def get_bmc_UUID(self):
        """
        [(dbus.String(u'UUID'), dbus.String(u'd3f20589-bca9-434c-8671-251843e37a38', variant_level=1))]
        """
        return self.get_prop_for_interface(prop=self.lookupValues['BMC_UUID'][PROPERTY_INDEX], Host=self.lookupValues['BMC_UUID'][HOST_INDEX], interface=self.lookupValues['BMC_UUID'][INTERFACE_INDEX], objpath=self.lookupValues['BMC_UUID'][OBJPATH_INDEX])
    

    def get_host_state(self):
        """
        [(dbus.String(u'CurrentPowerState'), dbus.String(u'xyz.openbmc_project.State.Host.HostState.Running', variant_level=1)),
        """
        return self.get_prop_for_interface(prop=self.lookupValues['HOST_STATE'][PROPERTY_INDEX], Host=self.lookupValues['HOST_STATE'][HOST_INDEX], interface=self.lookupValues['HOST_STATE'][INTERFACE_INDEX], objpath=self.lookupValues['HOST_STATE'][OBJPATH_INDEX])

    def set_host_state(self, ResetState):
        """
        [(dbus.String(u'RequestedHostTransition'), dbus.String(u'xyz.openbmc_project.State.Host.Transition.Off', variant_level=1))]
        [(dbus.String(u'RequestedHostTransition'), dbus.String(u'xyz.openbmc_project.State.Host.Transition.On', variant_level=1))]
        [(dbus.String(u'RequestedHostTransition'), dbus.String(u'xyz.openbmc_project.State.Host.Transition.Reboot', variant_level=1))]
        """
        p = dbus.String(self.lookupValues['HOST_RESET_STATE'][PROPERTY_INDEX])
        v = dbus.String(ResetState, variant_level=1)
        self.set_prop_for_interface(prop=p, val=v, Host=self.lookupValues['HOST_RESET_STATE'][HOST_INDEX], interface=self.lookupValues['HOST_RESET_STATE'][INTERFACE_INDEX], objpath=self.lookupValues['HOST_RESET_STATE'][OBJPATH_INDEX])

    def set_host_state_On(self):
        self.set_host_state('xyz.openbmc_project.State.Host.Transition.On')

    """
    Graceful Shutdown
    """
    def set_host_state_Off(self):
        self.set_host_state('xyz.openbmc_project.State.Host.Transition.Off')

    """
    Graceful reboot
    """
    def set_host_state_Reboot(self):
        self.set_host_state('xyz.openbmc_project.State.Host.Transition.Reboot')

    def get_chassis_state(self):
        """
        [(dbus.String(u'CurrentPowerState'), dbus.String(u'xyz.openbmc_project.State.Chassis.PowerState.Off', variant_level=1)),]
        [(dbus.String(u'CurrentPowerState'), dbus.String(u'xyz.openbmc_project.State.Chassis.PowerState.On', variant_level=1)),]
        """
        ChassState = self.get_prop_for_interface(prop=self.lookupValues['CHASSIS_STATE'][PROPERTY_INDEX], Host=self.lookupValues['CHASSIS_STATE'][HOST_INDEX], interface=self.lookupValues['CHASSIS_STATE'][INTERFACE_INDEX], objpath=self.lookupValues['CHASSIS_STATE'][OBJPATH_INDEX])
        data = ChassState.split('xyz.openbmc_project.State.Chassis.PowerState.')
        return (data[1])

    def set_chassis_state(self, ResetState):
        """
        (dbus.String(u'RequestedPowerTransition'), dbus.String(u'xyz.openbmc_project.State.Chassis.Transition.Off', variant_level=1))]
        (dbus.String(u'RequestedPowerTransition'), dbus.String(u'xyz.openbmc_project.State.Chassis.Transition.On', variant_level=1))]
        """
        p = dbus.String(self.lookupValues['CHASSIS_RESET_STATE'][PROPERTY_INDEX])
        v = dbus.String(ResetState, variant_level=1)
        self.set_prop_for_interface(prop=p, val=v, Host=self.lookupValues['CHASSIS_RESET_STATE'][HOST_INDEX], interface=self.lookupValues['CHASSIS_RESET_STATE'][INTERFACE_INDEX], objpath=self.lookupValues['CHASSIS_RESET_STATE'][OBJPATH_INDEX])
    
    def set_chassis_state_On(self):
        self.set_chassis_state('xyz.openbmc_project.State.Chassis.Transition.On')
    
    """
    Hard Power Off!!!
    """
    def set_chassis_state_Off(self):
        self.set_chassis_state('xyz.openbmc_project.State.Chassis.Transition.Off')
    
    def get_chassis_asset_tag(self):
        """
        [(dbus.String(u'AssetTag'), dbus.String(u'123456', variant_level=1))]
        """
        return self.get_prop_for_interface(prop=self.lookupValues['CHASSIS_ASSET_TAG'][PROPERTY_INDEX], Host=self.lookupValues['CHASSIS_ASSET_TAG'][HOST_INDEX], interface=self.lookupValues['CHASSIS_ASSET_TAG'][INTERFACE_INDEX], objpath=self.lookupValues['CHASSIS_ASSET_TAG'][OBJPATH_INDEX])
    
    def set_chassis_asset_tag(self, AssetTagVal):
        """
        [(dbus.String(u'AssetTag'), dbus.String(u'123456', variant_level=1))]
        """
        p = dbus.String(self.lookupValues['CHASSIS_ASSET_TAG'][PROPERTY_INDEX])
        v = dbus.String(AssetTagVal, variant_level=1)
        self.set_prop_for_interface(prop=p, val=v, Host=self.lookupValues['CHASSIS_ASSET_TAG'][HOST_INDEX], interface=self.lookupValues['CHASSIS_ASSET_TAG'][INTERFACE_INDEX], objpath=self.lookupValues['CHASSIS_ASSET_TAG'][OBJPATH_INDEX])
    
    def get_chassis_ID_LED(self):
        """
        [(dbus.String(u'Asserted'), dbus.Boolean(False, variant_level=1))]
        """
        LEDState = self.get_prop_for_interface(prop=self.lookupValues['CHASSIS_ID_LED'][PROPERTY_INDEX], Host=self.lookupValues['CHASSIS_ID_LED'][HOST_INDEX], interface=self.lookupValues['CHASSIS_ID_LED'][INTERFACE_INDEX], objpath=self.lookupValues['CHASSIS_ID_LED'][OBJPATH_INDEX])
        if LEDState == True:
            return 'Blinking'
        else:
            return 'Off'
    
    def deassert_chassis_ID_LED(self):
        """
        [(dbus.String(u'Asserted'), dbus.Boolean(False, variant_level=1))]
        """
        p = dbus.String(self.lookupValues['CHASSIS_ID_LED'][PROPERTY_INDEX])
        v = dbus.Boolean(False, variant_level=1)
        self.set_prop_for_interface(prop=p, val=v, Host=self.lookupValues['CHASSIS_ID_LED'][HOST_INDEX], interface=self.lookupValues['CHASSIS_ID_LED'][INTERFACE_INDEX], objpath=self.lookupValues['CHASSIS_ID_LED'][OBJPATH_INDEX])
    
    def assert_chassis_ID_LED(self):
        """
        [(dbus.String(u'Asserted'), dbus.Boolean(True, variant_level=1))]
        """
        p = dbus.String(self.lookupValues['CHASSIS_ID_LED'][PROPERTY_INDEX])
        v = dbus.Boolean(True, variant_level=1)
        self.set_prop_for_interface(prop=p, val=v, Host=self.lookupValues['CHASSIS_ID_LED'][HOST_INDEX], interface=self.lookupValues['CHASSIS_ID_LED'][INTERFACE_INDEX], objpath=self.lookupValues['CHASSIS_ID_LED'][OBJPATH_INDEX])
    
    def get_chassis_power_limit(self):
        """
        [(dbus.String(u'PowerCap'), dbus.UInt32(0L, variant_level=1)), 
        (dbus.String(u'PowerCapEnable'), dbus.Boolean(False, variant_level=1))]
        """
        return self.get_prop_for_interface(prop=self.lookupValues['CHASSIS_POWER_LIMIT'][PROPERTY_INDEX], Host=self.lookupValues['CHASSIS_POWER_LIMIT'][HOST_INDEX], interface=self.lookupValues['CHASSIS_POWER_LIMIT'][INTERFACE_INDEX], objpath=self.lookupValues['CHASSIS_POWER_LIMIT'][OBJPATH_INDEX])
    
    def set_chassis_power_limit(self, PowerLimit):
        """
        [(dbus.String(u'PowerCap'), dbus.UInt32(0L, variant_level=1)), 
        """
        p = dbus.String(self.lookupValues['CHASSIS_POWER_LIMIT'][PROPERTY_INDEX])
        v = dbus.UInt32(PowerLimit, variant_level=1)
        self.set_prop_for_interface(prop=p, val=v, Host=self.lookupValues['CHASSIS_POWER_LIMIT'][HOST_INDEX], interface=self.lookupValues['CHASSIS_POWER_LIMIT'][INTERFACE_INDEX], objpath=self.lookupValues['CHASSIS_POWER_LIMIT'][OBJPATH_INDEX])
    
    def get_chassis_power_reading(self):
        """
        (dbus.String(u'PowerReading'), dbus.String(u'250', variant_level=1))]
        """
        val = self.get_prop_for_interface(prop=self.lookupValues['CHASSIS_POWER_READING_VALUE'][PROPERTY_INDEX], Host=self.lookupValues['CHASSIS_POWER_READING_VALUE'][HOST_INDEX], interface=self.lookupValues['CHASSIS_POWER_READING_VALUE'][INTERFACE_INDEX], objpath=self.lookupValues['CHASSIS_POWER_READING_VALUE'][OBJPATH_INDEX])
        scale = self.get_prop_for_interface(prop=self.lookupValues['CHASSIS_POWER_READING_SCALE'][PROPERTY_INDEX], Host=self.lookupValues['CHASSIS_POWER_READING_SCALE'][HOST_INDEX], interface=self.lookupValues['CHASSIS_POWER_READING_SCALE'][INTERFACE_INDEX], objpath=self.lookupValues['CHASSIS_POWER_READING_SCALE'][OBJPATH_INDEX])
        if all(val_scale is not None for val_scale in [val, scale]):
            return int(val) * (10 ** int(scale))
        else:
            return 0
    
    def get_chassis_Manuf(self):
        """
        [(dbus.String(u'Manufacturer'), dbus.String(u'OpenBmc', variant_level=1))]
        """
        return self.get_prop_for_interface(prop=self.lookupValues['CHASSIS_MANUF'][PROPERTY_INDEX], Host=self.lookupValues['CHASSIS_MANUF'][HOST_INDEX], interface=self.lookupValues['CHASSIS_MANUF'][INTERFACE_INDEX], objpath=self.lookupValues['CHASSIS_MANUF'][OBJPATH_INDEX])
    
    def get_chassis_Model(self):
        """
        [(dbus.String(u'Model'), dbus.String(u'OpenBMC', variant_level=1))]
        """
        return self.get_prop_for_interface(prop=self.lookupValues['CHASSIS_MODEL'][PROPERTY_INDEX], Host=self.lookupValues['CHASSIS_MODEL'][HOST_INDEX], interface=self.lookupValues['CHASSIS_MODEL'][INTERFACE_INDEX], objpath=self.lookupValues['CHASSIS_MODEL'][OBJPATH_INDEX])
    
    def get_chassis_SerialNum(self):
        """
        [(dbus.String(u'SerialNumber'), dbus.String(u'Y130UF727037', variant_level=1))]
        """
        return self.get_prop_for_interface(prop=self.lookupValues['CHASSIS_SERIAL_NUM'][PROPERTY_INDEX], Host=self.lookupValues['CHASSIS_SERIAL_NUM'][HOST_INDEX], interface=self.lookupValues['CHASSIS_SERIAL_NUM'][INTERFACE_INDEX], objpath=self.lookupValues['CHASSIS_SERIAL_NUM'][OBJPATH_INDEX])
    
    def get_chassis_PartNum(self):
        """
        [(dbus.String(u'PartNumber'), dbus.String(u'00VK525', variant_level=1))]
        """
        return self.get_prop_for_interface(prop=self.lookupValues['CHASSIS_PART_NUM'][PROPERTY_INDEX], Host=self.lookupValues['CHASSIS_PART_NUM'][HOST_INDEX], interface=self.lookupValues['CHASSIS_PART_NUM'][INTERFACE_INDEX], objpath=self.lookupValues['CHASSIS_PART_NUM'][OBJPATH_INDEX])
