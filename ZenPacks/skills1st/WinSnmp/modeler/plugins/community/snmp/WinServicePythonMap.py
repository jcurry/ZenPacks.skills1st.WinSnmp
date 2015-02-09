################################################################################
#
# This program is part of the WinServiceSNMP Zenpack for Zenoss.
# Copyright (C) 2012 Ryan Matte
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""WinServicePythonMap

WinServicePythonMap maps Windows services via SNMP

$Id: $"""

__version__ = '$Revision: $'[11:-2]

from Products.DataCollector.plugins.CollectorPlugin import SnmpPlugin, GetTableMap, GetMap
from Products.DataCollector.plugins.DataMaps import ObjectMap

# Note: The filename must match the snmpPlugin class name - ie WinServicePythonMap
class WinServicePythonMap(SnmpPlugin):

    maptype = "WinServicePythonMap"
    relname = "WinServiceSNMPPython"
    modname = "ZenPacks.skills1st.WinSnmp.WinServiceSNMPPython"
    deviceProperties = \
                SnmpPlugin.deviceProperties + ('zWinServiceSNMPPythonIgnoreNames',
                                               'zWinServiceSNMPPythonMonitorNames',
                                               'zWinServiceSNMPPythonMonitorNamesEnable')

    columns = {
         '.1': 'WinServiceSNMPName',
         }

    snmpGetTableMaps = (
        GetTableMap('svSvcEntries', '.1.3.6.1.4.1.77.1.2.3.1', columns),
    )

    def process(self, device, results, log):
        """Process SNMP information from this device"""
        log.info('Modeler %s processing data for device %s', self.name(), device.id)
        getdata, tabledata = results
        log.debug("%s tabledata = %s", device.id, tabledata)
        svctable = tabledata.get("svSvcEntries")
        if svctable is None:
            log.error("Unable to get data for %s from svSvcEntries"
                          " -- skipping model" % device.id)
            return None

        rm = self.relMap()
        temptable = tabledata["svSvcEntries"]
        for svc in svctable.values():
            if not self.checkColumns(svc, self.columns, log):
                continue

            om = self.objectMap(svc)
            om.id = self.prepId(om.WinServiceSNMPName)
            dontCollectServiceNames = getattr(device, 'zWinServiceSNMPPythonIgnoreNames', None)
            collectServiceNames = getattr(device, 'zWinServiceSNMPPythonMonitorNames', None)
            collectServiceNamesToggle = getattr(device, 'zWinServiceSNMPPythonMonitorNamesEnable', None)
            if om.WinServiceSNMPName in dontCollectServiceNames:
                log.debug('Service %s matched the zprop zWinServiceSNMPPythonIgnoreNames', om.WinServiceSNMPName)
                continue
            if collectServiceNamesToggle == True and om.WinServiceSNMPName not in collectServiceNames:
                log.debug('Service %s did not match the zprop zWinServiceSNMPPythonMonitorNames', om.WinServiceSNMPName)
                continue
            for oid in temptable:
                tempdata = temptable[oid]
                if tempdata['WinServiceSNMPName'] == om.WinServiceSNMPName:
                    om.snmpindex = oid.strip('.')
                    log.debug('OID FOUND FOR %s: %s', tempdata['WinServiceSNMPName'], oid)
            rm.append(om)
        return rm
