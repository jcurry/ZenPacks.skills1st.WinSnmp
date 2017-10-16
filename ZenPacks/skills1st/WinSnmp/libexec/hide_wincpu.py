#!/usr/bin/python
# Originally from Ryan Matte's ZenPacks.Nova.Windows.SNMPPerfMonitor
# Uses a command to run an snmpwalk to get cpu utilisation
# SNMP OID is actually a table of values - 1 value per processor
#   hrProcessorLoad     .1.3.6.1.2.1.25.3.3.1.2
#   For multiple CPUs, simply sum up the values

import sys
import commands

host = sys.argv[1]
snmp_ver = sys.argv[2]
community_string = sys.argv[3]

total = 0
cpu_index = 1

cpu_command = "snmpwalk -" + snmp_ver + " -c " + community_string + " " + host + " .1.3.6.1.2.1.25.3.3.1.2"
(status, cpu_output) = commands.getstatusoutput(cpu_command)
if status == 0:
    cpu_list = cpu_output.split('\n')
    num_cpus = len(cpu_list)

    if num_cpus > 0:
        sys.stdout.write("OK|")
        for cpu in cpu_list:
            value = int(cpu.split(' ')[-1])
            total = total + value
            sys.stdout.write("CPU" + str(cpu_index) + "=" + str(value) + " "),
            cpu_index += 1
        sys.stdout.write("Total=" + str((total / num_cpus)) + "\n")
        sys.stdout.flush()
    else:
	print "Unknown"
else:
    print "Unknown"
