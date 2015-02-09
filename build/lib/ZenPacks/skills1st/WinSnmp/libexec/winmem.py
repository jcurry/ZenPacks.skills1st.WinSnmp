#!/usr/bin/python
# Originally from Ryan Matte's ZenPacks.Nova.Windows.SNMPPerfMonitor
# Uses a command to drive SNMP to get RAM and Paging values from Host Resources MIB
#  SNMP OIDs are table values - hrStorageEntry    1.3.6.1.2.1.25.2.3.1
#  The .2 column gives hrStorageType with values like hrStorageRam and hrStorageVirtualMemory
#  The .4 column gives hrStorageAllocationUnits (ie block size in bytes)
#  The .5 column gives hrStorageSize (ie total number of allocation units)
#  The .6 column gives hrStorageUsed (ie number of allocation units used)


import sys
import commands

host = sys.argv[1]
snmp_ver = sys.argv[2]
community_string = sys.argv[3]

oidnum_command = "snmpwalk -" + snmp_ver + " -c " + community_string + " " + host + " .1.3.6.1.2.1.25.2.3.1.2"
(status, oidnum_output) = commands.getstatusoutput(oidnum_command)
if status == 0:
    oidnum_list = oidnum_output.split('\n')
    for line in oidnum_list:
        if 'hrStorageRam' in line:
            oid_mem = line.split('.')[1]
            oid_mem = oid_mem.split(' ')[0]
        elif 'hrStorageVirtualMemory' in line:
            oid_paging = line.split('.')[1]
            oid_paging = oid_paging.split(' ')[0]
        else:
            oid_mem = None
            oid_paging = None

    if oid_mem and oid_paging:
        command = "snmpget -v2c -c " + community_string + " " + host + \
                  " .1.3.6.1.2.1.25.2.3.1.6." + oid_mem + \
                  " .1.3.6.1.2.1.25.2.3.1.5." + oid_mem + \
                  " .1.3.6.1.2.1.25.2.3.1.4." + oid_mem + \
                  " .1.3.6.1.2.1.25.2.3.1.6." + oid_paging + \
                  " .1.3.6.1.2.1.25.2.3.1.5." + oid_paging + \
                  " .1.3.6.1.2.1.25.2.3.1.4." + oid_paging 
        command_output = commands.getoutput(command)
        command_list = command_output.split('\n')
        for s in command_list:
            if 'hrStorageUsed.'+oid_mem in s:
                usage_mem = float(s.split(' ')[-1])
            elif 'hrStorageSize.'+oid_mem in s:
                total_mem = float(s.split(' ')[-1])
            elif 'hrStorageAllocationUnits.'+oid_mem in s:
                units_mem = float(s.split(' ')[-2])
            elif 'hrStorageUsed.'+oid_paging in s:
                usage_paging = float(s.split(' ')[-1])
            elif 'hrStorageSize.'+oid_paging in s:
                total_paging = float(s.split(' ')[-1])
            elif 'hrStorageAllocationUnits.'+oid_paging in s:
                units_paging = float(s.split(' ')[-2])

        print "OK|MemoryTotal=%1.0f MemoryUsed=%1.0f PercentMemoryUsed=%1.0f PagingTotal=%1.0f PagingUsed=%1.0f PercentPagingUsed=%1.0f" % \
            ((total_mem * units_mem / 1.024), (usage_mem * units_mem / 1.024), (usage_mem / total_mem * 100),
             (total_paging * units_paging / 1.024), (usage_paging * units_paging / 1.024), (usage_paging / total_paging * 100))
    else:
        print "Unknown"
else:
    print "Unknown"
