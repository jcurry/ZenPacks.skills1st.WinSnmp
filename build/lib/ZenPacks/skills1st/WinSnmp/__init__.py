################################################################################
#
# This program is part of the WinSnmp Zenpack for Zenoss.
# Copyright (C) 2012 Ryan Matte and Jane Curry
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

import Globals
import logging
import os
log = logging.getLogger('zen.PythonWinSnmp')

from Products.CMFCore.DirectoryView import registerDirectory
from Products.ZenModel.ZenossSecurity import *

skinsDir = os.path.join(os.path.dirname(__file__), 'skins')
if os.path.isdir(skinsDir):
    registerDirectory(skinsDir, globals())

from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenUtils.Utils import zenPath
from Products.ZenModel.ZenMenu import ZenMenu
from Products.ZenModel.Device import Device
from Products.ZenRelations.RelSchema import ToManyCont, ToOne

class ZenPack(ZenPackBase):
    packZProperties =  [
        ('zWinServiceSNMPPythonIgnoreNames', '', 'lines'),
        ('zWinServiceSNMPPythonMonitorNames', '', 'lines'),
        ('zWinServiceSNMPPythonMonitorNamesEnable', False, 'boolean'),
        ]

    def install(self, app):
        super(ZenPack, self).install(app)
        log.info('Installing menus')
        self.installMenuItems(app.zport.dmd)
        windowsOrg = app.dmd.unrestrictedTraverse('Devices/Server/Windows/Snmp')
        if not windowsOrg.zPythonClass:
            log.info('Setting zPythonClass in /Server/Windows/Snmp to \'ZenPacks.skills1st.WinSnmp.WinServiceSNMPPythonDevice\'')
            windowsOrg.setZenProperty('zPythonClass', 'ZenPacks.skills1st.WinSnmp.WinServiceSNMPPythonDevice')
        elif windowsOrg.zPythonClass == "ZenPacks.Nova.WinServiceSNMP.WinServiceSNMPDevice":
            log.info('Setting zPythonClass in /Server/Windows/Snmp to \'ZenPacks.skills1st.WinSnmp.WinServiceSNMPPythonDevice\'')
            windowsOrg.setZenProperty('zPythonClass', 'ZenPacks.skills1st.WinSnmp.WinServiceSNMPPythonDevice')
        else:
            if windowsOrg.zPythonClass != "ZenPacks.skills1st.WinSnmp.WinServiceSNMPPythonDevice":
                log.info('Unable to set zPythonClass in /Server/Windows/Snmp to \'ZenPacks.skills1st.WinSnmp.WinServiceSNMPPythonDevice\' (already set to something else)')
        log.info('Adding collector plugin \'community.snmp.WinServicePythonMap\' to /Server/Windows/Snmp')
        plugins=[]
        for plugin in windowsOrg.zCollectorPlugins:
            plugins.append(plugin)
        plugins.append('community.snmp.WinServicePythonMap')
        windowsOrg.setZenProperty('zCollectorPlugins', plugins)
        log.info('Rebuilding device relations')
        self.rebuildRelations(app.zport.dmd)

    def remove(self, app, leaveObjects=False):
        log.info('Removing menus')
        self.removeMenuItems(app.zport.dmd)
        if not leaveObjects:
            windowsOrg = app.dmd.unrestrictedTraverse('Devices/Server/Windows/Snmp')
            log.info('Removing collector plugin \'community.snmp.WinServicePythonMap\' from /Server/Windows/Snmp')
            plugins=[]
            for plugin in windowsOrg.zCollectorPlugins:
                if plugin != 'community.snmp.WinServicePythonMap':
                    plugins.append(plugin)
            windowsOrg.setZenProperty('zCollectorPlugins', plugins)
            if windowsOrg.zPythonClass == 'ZenPacks.skills1st.WinSnmp.WinServiceSNMPPythonDevice':
                log.info('Clearing zPythonClass in /Server/Windows/Snmp')
                windowsOrg._delProperty('zPythonClass')
            log.info('Rebuilding device relations')
            self.rebuildRelations(app.zport.dmd)
        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)


    def installMenuItems(self, dmd):
        winservpythonmenu = ZenMenu('WinServiceSNMPPython')
        dmd.zenMenus._setObject(winservpythonmenu.id, winservpythonmenu)
        winservpythonmenu = dmd.zenMenus._getOb(winservpythonmenu.id)

        winservpythonmenu.manage_addZenMenuItem('lockWinServiceSNMP',
                                   action='winservdialog_lockWinServiceSNMPPython',  # page template that is called
                                   description='Lock Windows Service...',
                                   permissions=(ZEN_MANAGE_DEVICE,),
                                   ordering=2.0,
                                   isdialog=True)

        winservpythonmenu.manage_addZenMenuItem('changeMonitoring',
                                   action='winservdialog_changeWinServiceSNMPPythonMonitoring',  # page template that is called
                                   description='Monitoring...',
                                   permissions=(ZEN_MANAGE_DEVICE,),
                                   ordering=0.0,
                                   isdialog=True)


    def removeMenuItems(self,dmd):
        try:
            dmd.zenMenus._delObject('WinServiceSNMPPython')
        except AttributeError:
            pass


    def rebuildRelations(self, dmd):
        zcat_logger = logging.getLogger('Zope.ZCatalog')
        zcat_logger.setLevel(logging.CRITICAL)
        zcat_logger2 = logging.getLogger('zen.DeviceClass')
        zcat_logger2.setLevel(logging.CRITICAL)
        for d in dmd.Devices.getSubDevicesGen():
            d.buildRelations()
            if d.__class__ != d.deviceClass().getPythonDeviceClass():
                d.changeDeviceClass(d.getDeviceClassPath())
        zcat_logger.setLevel(logging.INFO)
        zcat_logger2.setLevel(logging.INFO)
