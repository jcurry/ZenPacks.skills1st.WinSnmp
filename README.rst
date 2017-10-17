============================================================================
ZenPack to manage SNMP devices using the Python Collector ZenPack
============================================================================

Description
===========

THIS IS CURRENTLY A BETA ZENPACK. IT SHOULD ONLY BE INSTALLED IN A TEST ENVIRONMENT!!!


This ZenPack serves two purposes.  One is to manage Windows devices via the
SNMP protocol; the second is to demonstrate examples of using the Python Collector ZenPack.

The ZenPack is based on two earlier ZenPacks by Ryan Matte:
    * ZenPacks.Nova.Windows.SNMPPerfMonitor  is available at http://wiki.zenoss.org/ZenPack:Windows_SNMP_Performance_Monitor_%28Advanced%29 
    * ZenPacks.Nova.WinServiceSNMP can be found on the Zenoss  wiki at  http://wiki.zenoss.org/ZenPack:Windows_SNMP_Service_Monitor .  


ZenPacks.Nova.Windows.SNMPPerfMonitor monitors cpu, memory, paging and processes; ZenPacks.Nova.WinServiceSNMP has a modeler to gather
Windows Services components and a template to then gather operational status data.

This ZenPack combines the functionality into one ZenPack and changes the data collection method from using commands to
using SNMP.  This ZenPack can coexist with Ryan's ZenPacks.  In general, names have had "Python" appended to them to make
similar objects distinct from Ryan's.

The ZenPack introduces a new device class of /Server/Windows/Snmp and then adds subclasses for different numbers of processors,
whereas Ryan's ZenPack works directly with devices under /Server/Windows.

To determine which group to place a server in perform an snmpwalk command for hrProcessorLoad as follows:

snmpwalk -v1 -c <snmp string> <host> hrProcessorLoad

The number of lines corresponds to the number of CPUs.

Unlike Ryan's ZenPack, I have NOT provided exhaustive templates for each different number of processors. A sample is
provided; please expand the templates to suit your own device requirements.

During installation and removal the ZenPack rebuilds device relations for all devices within the /Server/WindowsSnmp device class. 
Depending on the number of devices that you have in that class, it can take a long time. You will notice some errors 
in the UI while the relations are being rebuilt, which is normal. Please be patient and allow it to complete. 
After the relations have been rebuilt Zenoss should be restarted. 

Make sure that you lock the services to prevent them from being removed during a remodel while a service is down. 
Modeling will only pick up services that are running. 

zProperties
===========

    * zWinServiceSNMPIgnoreNames: Place the full names of any services that you want to ignore in this line by line.
    * zWinServiceSNMPMonitorNames: Place the full names of any services which you explicitly want to monitor (ignoring all others) in this line by line.
    * zWinServiceSNMPMonitorNamesEnable: This enables/disables the use of zWinServiceSNMPMonitorNames 

Note that you need to remodel your devices for the above to take effect.

Keep in mind that zWinServiceSNMPIgnoreNames is constantly in use. If you put the same service name in both 
zWinServiceSNMPIgnoreNames and zWinServiceSNMPMonitorNames it will be ignored. 
The default is that all modeled services are monitored.

Templates
=========

    * PyTestSnmpCpu  monitors CPU utilisation for each processor and the average total. Uses Python to drive SNMP
    * PyTestSnmpMem  monitors memory and paging using Python to drive SNMP.  Adds total swap to the device os relationship.
    * PyTestCmdMemCpu  monitors cpu and memory / paging using Python to drive commands. This template is not bound by default.
    * PyTestSnmpServProc  monitors number of processes and number of services. Uses Python to drive SNMP.
    * WinServiceSNMPPython in /Server/Windows/Snmp: This template is required for monitoring services. Do not bind this template to the device. Make sure the template is in the class that the device is in (or a higher class). The template will automatically be used for the windows services components.


Modeler Plugins
===============

community.snmp.WinServiceMap: This plugin is required during modeling. It currently is based on the standard SnmpPlugin.


Events
======

This ZenPack ships 2 events that are used with thresholds and templates.  Both have transforms.
    * /Perf/Memory/Snmp
    * /Status/WinServiceSNMPPython


Daemon
======
There is no daemon shipped with this ZenPack.  zenpython does all the work.

Requirements & Dependencies
===========================

    * Zenoss Versions Supported: 4.x
    * External Dependencies: 
    * ZenPack Dependencies: ZenPacks.zenoss.PythonCollector at least 1.6 - earlier versions will not work
    * Installation Notes: Restart zenhub, zopectl and zenpython after installation
    * Configuration:


Download
========
Download the appropriate package for your Zenoss version from the list
below.

* Zenoss 4.0+ `Latest Package for Python 2.7`_

ZenPack installation
======================

Beware, as with any ZenPack, if you remove the ZenPack and devices exist under
classes defined in this ZenPack - /Server/Windows/Snmp - then these devices will be removed.

This is NOT the case if you reinstall the ZenPack.  I suggest you move any affected
device to another class (/Ping might be good, temporarily) if you are going
to remove the ZenPack.

This ZenPack can be installed from the .egg file using either the GUI or the
zenpack command line but, since it is demonstration code that you are likely to 
want to modify, it is more likely installed in development mode.  From github - 
https://github.com/jcurry/ZenPacks.skills1st.WinSnmp  use the ZIP button
(top left) to download a tgz file and unpack it to a local directory, say,
$ZENHOME/local.  Install from $ZENHOME/local with:

zenpack --link --install ZenPacks.skills1st.WinSnmp

Restart zenhub, zopectl and zenpython after installation.



Change History
==============
* 1.0.0
   * Initial Release
* 1.0.2
   * Check made to close snmp session.
   * SnmpWinServComponentDataSource datasource generates event if service not found
   * SnmpMemDataSource datasource updates model with totalSwap on os relation 


Screenshots
===========

.. External References Below. Nothing Below This Line Should Be Rendered

.. _Latest Package for Python 2.7: https://github.com/jcurry/ZenPacks.skills1st.WinSnmp/blob/master/dist/ZenPacks.skills1st.WinSnmp-1.0.2-py2.7.egg?raw=true

