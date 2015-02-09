################################################################################
#
# This program is part of the WinSnmp Zenpack for Zenoss.
# Copyright (C) 2012 Ryan Matte and Jane Curry
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""WinServiceSNMPPython

WinServiceSNMPPython is a component of WinServiceSNMPPythonDevice

$Id: $"""

__version__ = "$Revision: $"[11:-2]

from Globals import DTMLFile
from Globals import InitializeClass
from Products.ZenRelations.RelSchema import *
from Products.ZenModel.ZenossSecurity import *
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenWidgets import messaging
from AccessControl import ClassSecurityInfo

import logging
log = logging.getLogger('zen.PythonWinSnmp')

class WinServiceSNMPPython(DeviceComponent, ManagedEntity):
    """WinServiceSNMPPython object"""

    # Set so a template named WinServiceSNMPPython will bind automatically
    portal_type = meta_type = 'WinServiceSNMPPython'

    #************ Custom data Variables here from modeling **********

    WinServiceSNMPName = 'Unknown'

    #**************END CUSTOM VARIABLES *****************************
    
    _properties = (
        {'id':'snmpindex', 'type':'string', 'mode':''},
        {'id':'WinServiceSNMPName', 'type':'string', 'mode':''},
        {'id':'monitor', 'type':'boolean', 'mode':''},
        )
    
    _relations = (
        ("WinServiceSNMPPythonDevice", ToOne(ToManyCont,
            "ZenPacks.skills1st.WinSnmp.WinServiceSNMPPythonDevice", "WinServiceSNMPPython")),
        )

    factory_type_information = ( 
        { 
            'id'             : 'WinServiceSNMPPython',
            'meta_type'      : 'WinServiceSNMPPython',
            'description'    : """WinServiceSNMPPython Interface info""",
            'product'        : 'winservicesnmppython',
            'immediate_view' : 'viewWinServiceSNMPPython',
            'actions'        :
            ( 
                { 'id'            : 'status'
                , 'name'          : 'Status'
                , 'action'        : 'viewWinServiceSNMPPython'
                , 'permissions'   : (ZEN_VIEW, )
                },
                { 'id'            : 'perfConf'
                , 'name'          : 'Template'
                , 'action'        : 'objTemplates'
                , 'permissions'   : (ZEN_CHANGE_SETTINGS, )
                },                
                { 'id'            : 'viewHistory'
                , 'name'          : 'Modifications'
                , 'action'        : 'viewHistory'
                , 'permissions'   : (ZEN_VIEW, )
                },
            )
          },
        ) 

    isUserCreatedFlag = True


    def isUserCreated(self):
        """
        Returns the value of isUserCreated. True adds SAVE & CANCEL buttons to Details menu
        """
        return self.isUserCreatedFlag


    def viewName(self):
        """Pretty version human readable version of this object"""
        return str(self.WinServiceSNMPName)


    # use viewName as titleOrId because that method is used to display a human
    # readable version of the object in the breadcrumbs
    titleOrId = name = viewName


    def primarySortKey(self):
        """Sort by Service name"""
        return "%s" % (self.WinServiceSNMPName)


    def device(self):
        return self.WinServiceSNMPPythonDevice()
    

    def monitored(self):
        """
        Return monitoring status for service.
        """
        return self.monitor
        

    security = ClassSecurityInfo()
    security.declareProtected(ZEN_MANAGE_DEVICE, 'manage_editWinServiceSNMPPython')
    def manage_editWinServiceSNMPPython(self, monitor=False,
                WinServiceSNMPName=None,
                snmpindex=None, REQUEST=None):
        """
        Edit Services from a web page.
        """

        if WinServiceSNMPName:
            self.WinServiceSNMPName = WinServiceSNMPName

        self.monitor = monitor
        self.index_object()

        if REQUEST:
            messaging.IMessageSender(self).sendToBrowser(
                'Windows Service Updated',
                'Windows Service %s was edited.' % self.id
            )
            return self.callZenScreen(REQUEST)


InitializeClass(WinServiceSNMPPython)
