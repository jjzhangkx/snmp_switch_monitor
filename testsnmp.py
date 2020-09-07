#!/usr/bin/env python
# cofing:utf-8
import netsnmp

sess = netsnmp.Session(Version=3,
                       DestHost='localhost',
                       SecLevel='authPriv',
                       SecName='snmpuser',
                       PrivPass='passworddes',
                       AuthPass='password')

vars = netsnmp.VarList(netsnmp.Varbind('sysUpTime'),
                       netsnmp.Varbind('sysORLastChange'),
                       netsnmp.Varbind('sysORID'),
                       netsnmp.Varbind('sysORDescr'),
                       netsnmp.Varbind('sysORUpTime'))

vals = sess.getbulk(2, 8, vars)
print "v3 sess.getbulk result: ", vals, "\n"

for var in vars:
    print var.tag, var.iid, "=", var.val, '(', var.type, ')'
print "\n"

print "---v3 set-------------------------------------\n"

vars = netsnmp.VarList(
    netsnmp.Varbind('sysLocation', '0', 'my final destination'))
res = sess.set(vars)
print "v3 sess.set result: ", res, "\n"

print "---v3 walk-------------------------------------\n"
vars = netsnmp.VarList(netsnmp.Varbind('system'))

vals = sess.walk(vars)
print "v3 sess.walk result: ", vals, "\n"

for var in vars:
    print "  ", var.tag, var.iid, "=", var.val, '(', var.type, ')'
