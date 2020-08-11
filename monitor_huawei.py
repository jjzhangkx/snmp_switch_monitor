import re
import os
import time
import platform
import datetime
from pymongo import MongoClient


class Monitor(object):

    def bytes_to_gb(self, data, key=""):
        return round(data / (1024 ** 3), 2)

    def snmpWalk(self, host, communty, oid):
        result = os.popen('snmpwalk -v 2c -c' + communty + ' ' + host + ' ' + oid).read().split('\n')[:-1]
        return result
    '''获取接口状态'''
    def getPortInfo(self, host, community):
        PortDevices_mib = self.snmpWalk(host, community, 'RFC1213-MIB::ifDescr')
        PortDevices_list = []
        for item in PortDevices_mib:
            PortDevices_list.append(item.split(':')[3].strip())
        return PortDevices_list

        # PortStatus_mib = self.snmpWalk(host, community, 'RFC1213-MIB::ifOperStatus')
        # PortStatus_list = []
        # for item in PortStatus_mib:
        #     PortStatus_list.append(item.split(':')[3].strip())
        #     PortStatus_list.append(item.split('(')[1].split(')')[0].strip())
        # return dict(zip(PortDevices_list,PortStatus_list))
    '''获取进入流量'''
    def get_In_Flow(self,host,community):
        # PortDevices_mib = self.snmpWalk(host, community, 'RFC1213-MIB::ifDescr')
        # PortDevices_list = []
        # for item in PortDevices_mib:
        #     PortDevices_list.append(item.split(':')[3].strip())

        In_Flow_mib=self.snmpWalk(host, community, 'IF-MIB::ifInOctets')
        In_Flow_list=[]
        for item in In_Flow_mib:
            In_Flow_list.append(item.split(':')[3].strip())
        return In_Flow_list
        # return dict(zip(PortDevices_list,In_Flow_list))
    '''获取出流量'''
    def get_Out_Flow(self, host, community):
        # PortDevices_mib = self.snmpWalk(host, community, 'RFC1213-MIB::ifDescr')
        # PortDevices_list = []
        # for item in PortDevices_mib:
        #     PortDevices_list.append(item.split(':')[3].strip())

        Out_Flow_mib = self.snmpWalk(host, community, 'IF-MIB::ifOutOctets')
        Out_Flow_list = []
        for item in Out_Flow_mib:
            Out_Flow_list.append(item.split(':')[3].strip())
        return Out_Flow_list
        # return dict(zip(PortDevices_list, Out_Flow_list))

    def getCupInfo(self, host, community):
        '''五秒钟'''
        fiveSecUsed = (self.snmpWalk(host, community, '1.3.6.1.4.1.2011.6.3.4.1.2'))[0].split(':')[-1]
        '''一分钟'''
        oneMinUsed = (self.snmpWalk(host, community, '1.3.6.1.4.1.2011.6.3.4.1.3'))[0].split(':')[-1]
        '''五分钟'''
        fiveMinUsed = (self.snmpWalk(host, community, '1.3.6.1.4.1.2011.6.3.4.1.4'))[0].split(':')[-1]
        CupInfo = dict(
            fiveSecUsed=int(fiveSecUsed),
            oneMinUsed=int(oneMinUsed),
            fiveMinUsed=int(fiveMinUsed)
        )

        return CupInfo

    def getMemInfo(self, host, community):
        total = (self.snmpWalk(host, community, '1.3.6.1.4.1.2011.6.3.5.1.1.2'))[0].split(':')[-1]

        print(type(total))
        free = (self.snmpWalk(host, community, '1.3.6.1.4.1.2011.6.3.5.1.1.3'))[0].split(':')[-1]
        print(free)
        used = int(total) - int(free)
        percent = int(used) / int(total)
        MemInfo = dict(
            total=self.bytes_to_gb(int(total)),
            free=self.bytes_to_gb(int(free)),
            used=self.bytes_to_gb(int(used)),
            percent=float(percent)
        )
        return MemInfo

    def getAllInfo(self,host,community):
        info={}
        info['PortInfo']=self.getPortInfo(host,community)
        # ret=self.getPortInfo(host,community)
        # info.update(ret)
        info['In_Flow']=self.get_In_Flow(host,community)
        # info.update(ret)
        info['OutFlow']=self.get_Out_Flow(host,community)
        # info.update(ret)
        ret=self.getMemInfo(host,community)
        info.update(ret)
        ret=self.getCupInfo(host,community)
        info.update(ret)
        info['time']= datetime.datetime.now()
        info['serverip']=host

        return info

def insertdb(info):
    client = MongoClient('192.168.43.116', 27017)
    monitor = client.monitor_huawei
    monitorlog = monitor.monitorlog_huawei
    monitorlog.insert(info)

m = Monitor()

print("IP:")
host = input()
print("community")
community = input()
print('=' * 10 + host + '=' * 10)
insertdb(m.getAllInfo(host,community))
print(m.getAllInfo(host,community))
print(m.getPortInfo(host, community))
# DeviceStatus = m.getPortStatus(host, community)
# print(m.getMemInfo(host, community))
# print(m.getCupInfo(host, community))

