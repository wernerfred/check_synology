from pysnmp.hlapi import *
import argparse
import sys
import math

AUTHOR = "Frederic Werner"
VERSION = 0.1

parser = argparse.ArgumentParser()
parser.add_argument("hostname", help="the hostname", type=str)
parser.add_argument("username", help="the snmp user name", type=str)
parser.add_argument("authkey", help="the auth key", type=str)
parser.add_argument("privkey", help="the priv key", type=str)
parser.add_argument("mode", help="the mode", type=str, choices=["load", "memory", "disk", "storage", "update", "status"])
parser.add_argument("-w", help="warning value for selected mode", type=int)
parser.add_argument("-c", help="critical value for selected mode", type=int)
args = parser.parse_args()

hostname = args.hostname
user_name = args.username
auth_key = args.authkey
priv_key = args.privkey
mode = args.mode
warning = args.w
critical = args.c

state = 'OK'

def snmpget(oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               UsmUserData(user_name, auth_key, priv_key, authProtocol=usmHMACMD5AuthProtocol, privProtocol=usmAesCfb128Protocol),
               UdpTransportTarget((hostname, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)
                #.addAsn1MibSource('file:///usr/share/snmp', 'http://mibs.snmplabs.com/asn1/@mib@')
                ))
    )

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            answer = (' = '.join([x.prettyPrint() for x in varBind]))
            #print(' = '.join([x.prettyPrint() for x in varBind]))
            return x.prettyPrint()

def exitCode():
    if state == 'OK':
        sys.exit(0)
    if state == 'WARNING':
        sys.exit(1)
    if state == 'CRITICAL':
        sys.exit(2)
    if state == 'UNKNOWN':
        sys.exit(3)

if mode == 'load':
    load1 = str(float(snmpget('1.3.6.1.4.1.2021.10.1.5.1'))/100)
    load5 = str(float(snmpget('1.3.6.1.4.1.2021.10.1.5.2'))/100)
    load15 = str(float(snmpget('1.3.6.1.4.1.2021.10.1.5.3'))/100)

    if warning and warning < int(math.ceil(float(load1))):
        state = 'WARNING'
    if critical and critical < int(math.ceil(float(load1))):
        state = 'CRITICAL'

    print state + ' - load average: %s, %s, %s' % (load1, load5, load15), '| load1=%sc' % load1, 'load5=%sc' % load5, 'load15=%sc' % load15
    exitCode()

if mode == 'memory':
    memory_total = float(snmpget('1.3.6.1.4.1.2021.4.5.0'))
    memory_unused = float(snmpget('1.3.6.1.4.1.2021.4.6.0'))
    memory_percent = 100 / memory_total * memory_unused

    if warning and warning > int(memory_percent):
        state = 'WARNING'
    if critical and critical > int(memory_percent):
        state = 'CRITICAL'

    print state + ' - {:0.1f}% '.format(memory_percent) + 'free ({0:0.1f} MB out of {1:0.1f} MB)'.format((memory_unused / 1024), (memory_total / 1024)), '|memory_total=%dc' % memory_total, 'memory_unused=%dc' % memory_unused , 'memory_percent=%d' % memory_percent + '%'
    exitCode()

if mode == 'disk':
    maxDisk = 0
    output = ''
    perfdata = '|'
    for i in range(0, 64, 1):
        disk = snmpget('1.3.6.1.4.1.6574.2.1.1.2.' + str(i))
        if disk.startswith("No Such Instance"):
            break
        maxDisk = maxDisk + 1
    for i in range(0, maxDisk, 1):
        disk_name = snmpget('1.3.6.1.4.1.6574.2.1.1.2.' + str(i))
        disk_status_nr = snmpget('1.3.6.1.4.1.6574.2.1.1.5.' + str(i))
        disk_temp = snmpget('1.3.6.1.4.1.6574.2.1.1.6.' + str(i))
        status_translation = {
            '1': "Normal",
            '2': "Initialized",
            '3': "NotInitialized",
            '4': "SystemPartitionFailed",
            '5': "Crashed"
        }
        disk_status = status_translation.get(disk_status_nr)
        disk_name = disk_name.replace(" ", "")

        if warning and warning < int(disk_temp):
            if state != 'CRITICAL':
                state = 'WARNING'
        if critical and critical < int(disk_temp) or int(disk_status_nr) == (4 or 5):
            state = 'CRITICAL'

        output += ' - ' + disk_name + ': Status: ' + disk_status + ', Temperature: ' + disk_temp + ' C'
        perfdata += 'temperature' + disk_name + '=' + disk_temp + 'c '
    print '%s%s %s' % (state, output, perfdata)
    exitCode()

if mode == 'storage':
    output = ''
    perfdata = '|'
    for i in range(1,256,1):
        storage_name = snmpget('1.3.6.1.2.1.25.2.3.1.3.' + str(i))
        if storage_name.startswith("/volume"):
            allocation_units = snmpget('1.3.6.1.2.1.25.2.3.1.4.' + str(i))
            size = snmpget('1.3.6.1.2.1.25.2.3.1.5.' + str(i))
            used = snmpget('1.3.6.1.2.1.25.2.3.1.6.' + str(i))

            storage_size = int((int(allocation_units) * int(size)) / 1000000000)
            storage_used = int((int(used) * int(allocation_units)) / 1000000000)
            storage_free = int(storage_size - storage_used)
            storage_used_percent = int(storage_used * 100 / storage_size)

            if warning and warning < int(storage_used_percent):
                if state != 'CRITICAL':
                    state = 'WARNING'
            if critical and critical < int(storage_used_percent):
                state = 'CRITICAL'

            output += ' -  free space: ' + storage_name + ' ' + str(storage_free) + ' GB (' + str(storage_used) + ' GB von ' + str(storage_size) + ' GB belegt, ' + str(storage_used_percent) + '%)'
            perfdata += storage_name + '=' + str(storage_used) + 'c '
    print '%s%s %s' % (state, output, perfdata)
    exitCode()

if mode == 'update':
    update_status_nr = snmpget('1.3.6.1.4.1.6574.1.5.4.0')
    update_dsm_verison = snmpget('1.3.6.1.4.1.6574.1.5.3.0')
    status_translation = {
            '1': "Available",
            '2': "Unavailable",
            '3': "Connecting",
            '4': "Disconnected",
            '5': "Others"
        }

    if warning and 1 == int(update_status_nr):
        state = 'WARNING'
    if critical and [4|5] == int(update_status_nr):
        state = 'CRITICAL'

    update_status = status_translation.get(update_status_nr)
    print state + ' - DSM Version: %s, DSM Update: %s' % (update_dsm_verison, update_status), '| DSMupdate=%sc' % update_status_nr
    exitCode()

if mode == 'status':
    status_model = snmpget('1.3.6.1.4.1.6574.1.5.1.0')
    status_serial = snmpget('1.3.6.1.4.1.6574.1.5.2.0')
    status_temperature = snmpget('1.3.6.1.4.1.6574.1.2.0')
    
    status_system_nr = snmpget('1.3.6.1.4.1.6574.1.1.0')
    status_system_fan_nr = snmpget('1.3.6.1.4.1.6574.1.4.1.0')
    status_cpu_fan_nr = snmpget('1.3.6.1.4.1.6574.1.4.2.0')
    status_power_nr = snmpget('1.3.6.1.4.1.6574.1.3.0')

    status_translation = {
            '1': "Normal",
            '2': "Failed"
        }

    status_system = status_translation.get(status_system_nr)
    status_system_fan = status_translation.get(status_system_fan_nr)
    status_cpu_fan = status_translation.get(status_cpu_fan_nr)
    status_power = status_translation.get(status_power_nr)

    if warning and warning < int(status_temperature):
        state = 'WARNING'
    if critical and critical < int(status_temperature):
        state = 'CRITICAL'

    print state + ' - Model: %s, S/N: %s, System Temperature: %s C, System Status: %s, System Fan: %s, CPU Fan: %s, Powersupply : %s' % (status_model, status_serial, status_temperature, status_system, status_system_fan, status_cpu_fan, status_power) + ' | system_temp=%sc' % status_temperature
    exitCode()
