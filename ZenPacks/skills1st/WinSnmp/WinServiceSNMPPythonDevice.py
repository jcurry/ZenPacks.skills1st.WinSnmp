################################################################################
#
# This program is part of the WinServiceSNMP Zenpack for Zenoss.
# Copyright (C) 2012 Ryan Matte
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

from Globals import InitializeClass
from Products.ZenRelations.RelSchema import *
from Products.ZenModel.Device import Device
from Products.ZenModel.ZenossSecurity import *
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenModel.OSComponent import OSComponent
from Products.ZenModel.Service import Service
from Products.ZenModel.OSProcess import OSProcess
from Products.ZenWidgets import messaging
import copy
import types

class WinServiceSNMPPythonDevice(Device):
    "A WinServiceSNMPPython Device"

    _relations = Device._relations + (
        ('WinServiceSNMPPython', ToManyCont(ToOne,
            'ZenPacks.skills1st.WinSnmp.WinServiceSNMPPython', 'WinServiceSNMPPythonDevice')),
        )

    factory_type_information = copy.deepcopy(Device.factory_type_information)

    custom_actions = []
    custom_actions.extend(factory_type_information[0]['actions'])
    custom_actions.insert(2,
           { 'id'            : 'WinServiceSNMPPython'
           , 'name'          : 'Services'
           , 'action'        : 'WinServiceSNMPPythonDeviceDetail'
           , 'permissions'   : (ZEN_VIEW,) },
           )
    factory_type_information[0]['actions'] = custom_actions


    def __init__(self, *args, **kw):
        Device.__init__(self, *args, **kw)
        self.buildRelations()


    def setWinServiceSNMPPythonMonitored(self, componentNames=[],
                               monitored=True, REQUEST=None):
        """
        Set monitored status for selected components.
        """
        comp_ids = []
        if not componentNames: return self()
        if isinstance(componentNames, basestring):
            componentNames = (componentNames,)
        monitored = bool(monitored)
        for componentName in componentNames:
            for obj in self.WinServiceSNMPPython.objectValuesAll():
                if obj.id == componentName:
                    comp = obj
                    comp_ids.append(comp.id)
            if comp and comp.monitored() != monitored:
                comp.monitor = monitored
                if isinstance(comp, (Service, OSProcess)):
                    comp.setAqProperty('zMonitor', monitored, 'boolean')
                comp.index_object()
        if REQUEST:
            verb = monitored and "Enabled" or "Disabled"
            messaging.IMessageSender(self).sendToBrowser(
                'Monitoring %s' % verb,
                'Monitoring was %s on %s.' % (verb.lower(),
                                              ', '.join(comp_ids))
            )
            return self.callZenScreen(REQUEST)


    def unlockWinServiceSNMPPythonComponents(self, componentNames=[], REQUEST=None):
        """Unlock device components"""
        if not componentNames: return self()
        if type(componentNames) in types.StringTypes:
            componentNames = (componentNames,)
        for componentName in componentNames:
            for obj in self.WinServiceSNMPPython.objectValuesAll():
                if obj.id == componentName:
                    obj.unlock()
        if REQUEST:
            return self.callZenScreen(REQUEST)


    def lockWinServiceSNMPPythonComponentsFromUpdates(self, componentNames=[],
            sendEventWhenBlocked=None, REQUEST=None):
        """Lock device components from updates"""
        if not componentNames: return self()
        if type(componentNames) in types.StringTypes:
            componentNames = (componentNames,)
        for componentName in componentNames:
            for obj in self.WinServiceSNMPPython.objectValuesAll():
                if obj.id == componentName:
                    obj.lockFromUpdates(sendEventWhenBlocked)
        if REQUEST:
            return self.callZenScreen(REQUEST)


    def lockWinServiceSNMPPythonComponentsFromDeletion(self, componentNames=[],
            sendEventWhenBlocked=None, REQUEST=None):
        """Lock device components from deletion"""
        if not componentNames: return self()
        if type(componentNames) in types.StringTypes:
            componentNames = (componentNames,)
        for componentName in componentNames:
            for obj in self.WinServiceSNMPPython.objectValuesAll():
                if obj.id == componentName:
                    obj.lockFromDeletion(sendEventWhenBlocked)
        if REQUEST:
            return self.callZenScreen(REQUEST)        


    def unlockWinServiceSNMPPython(self, componentNames=[], REQUEST=None):
        """Unlock Logical Volumes"""
        self.unlockWinServiceSNMPPythonComponents(componentNames, REQUEST)
        if REQUEST:
            messaging.IMessageSender(self).sendToBrowser(
                'Windows Services Unlocked',
                'Windows Services %s were unlocked.' % (', '.join(componentNames))
            )
            return self.callZenScreen(REQUEST)


    def lockWinServiceSNMPPythonFromDeletion(self, componentNames=[],
            sendEventWhenBlocked=None, REQUEST=None):
        """Lock Logical Volumes from deletion"""
        self.lockWinServiceSNMPPythonComponentsFromDeletion(componentNames,
            sendEventWhenBlocked, REQUEST)
        if REQUEST:
            messaging.IMessageSender(self).sendToBrowser(
                'Windows Services Locked',
                'Windows Services %s were locked from deletion.' % (
                    ', '.join(componentNames))
            )
            return self.callZenScreen(REQUEST)


    def lockWinServiceSNMPPythonFromUpdates(self, componentNames=[],
            sendEventWhenBlocked=None, REQUEST=None):
        """Lock Logical Volumes from updates"""
        self.lockWinServiceSNMPPythonComponentsFromUpdates(componentNames,
            sendEventWhenBlocked, REQUEST)
        if REQUEST:
            messaging.IMessageSender(self).sendToBrowser(
                'Windows Services Locked',
                'Windows Services %s were locked from updates and deletion.' % (
                    ', '.join(componentNames))
            )
            return self.callZenScreen(REQUEST)


InitializeClass(WinServiceSNMPPythonDevice)
