#!/usr/bin/env python
# cofing:utf-8
import netsnmp

print "---v3 setup-------------------------------------\n"
sess = netsnmp.Session(Version=3,
                       DestHost='localhost',
                       SecLevel='authPriv',
                       SecName='snmpuser',
                       PrivPass='passworddes',
                       AuthPass='password')

sess.UseSprintValue = 1

vars = netsnmp.VarList(netsnmp.Varbind('sysUpTime', 0),
                       netsnmp.Varbind('sysContact', 0),
                       netsnmp.Varbind('sysLocation', 0))
print "---v3 get-------------------------------------\n"
vals = sess.get(vars)
print "v3 sess.get result: ", vals, "\n"

for var in vars:
    print var.tag, var.iid, "=", var.val, '(', var.type, ')'
print "\n"

print "---v3 getnext-------------------------------------\n"

vals = sess.getnext(vars)
print "v3 sess.getnext result: ", vals, "\n"

for var in vars:
    print var.tag, var.iid, "=", var.val, '(', var.type, ')'
print "\n"

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
