# This file is the conventional place for "Info" adapters. Info adapters are
# a crucial part of the Zenoss API and therefore the web interface for any
# custom classes delivered by your ZenPack. Examples of custom classes that
# will almost certainly need info adapters include datasources, custom device
# classes and custom device component classes.

# Mappings of interfaces (interfaces.py) to concrete classes and the factory
# (these info adapter classes) used to create info objects for them are managed
# in the configure.zcml file.

from zope.interface import implements

from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.component import ComponentInfo
from ZenPacks.skills1st.WinSnmp import interfaces


class WinServiceSNMPPythonInfo(ComponentInfo):
    implements(interfaces.IWinServiceSNMPPythonInfo)

    snmpindex = ProxyProperty("snmpindex")
    WinServiceSNMPName = ProxyProperty("WinServiceSNMPName")
    monitor = ProxyProperty("monitor")


