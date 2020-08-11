# -*- coding:utf8 -*-
import datetime
import time
from pymongo import MongoClient
import os
import ping

gaptime=15 #设置取数间隔周期，方便计算周期内平均流量速率

def getlist():
    iplist=[]
    conn=MongoClient('127.0.0.1',27017)
    monitor=conn.switchlist
    monitorlog=monitor.switchlistlog
    switchs=monitorlog.distinct('ipaddr')
    for item in switchs:
        iplist.append(str(item))
    return iplist

def getcommunity(ip):
    # iplist = []
    conn = MongoClient('127.0.0.1', 27017)
    monitor = conn.switchlist
    monitorlog = monitor.switchlistlog
    # switchs = monitorlog.distinct('ipaddr')
    info=monitorlog.find({'ipaddr':ip}).sort('time',-1).limit(1)
    for item in info:
        return item['community']

def snmpWalk(host, community, oid):
    result = os.popen('snmpwalk -v 2c -c' + community + ' ' + host + ' ' + oid).read().split('\n')[:-1]
    return result


# ---------------------------------------------------------------------------------------
# # 获取设备名称：
# def getuptime(ver, host, passwd):
#     result = {}
#     var = netsnmp.Varbind('hrSystemUptime.0')#sysUpTime
#     ret = netsnmp.snmpget(var, Version=ver, DestHost=host, Community=passwd)
#     result['uptime'] = ret[0]
#
#     return result
# ---------------------------------------------------------------------------------------
# 获取mac表数目
def getmactable(ver,host,community):
    result={}
    mactable=snmpWalk(host,community,'1.3.6.1.2.1.17.4.3.1.1')
    result['macnum']=len(mactable)

    return result

# ---------------------------------------------------------------------------------------
# 获取arp表数目
def getarptable(ver,host,community):
    result={}
    arptable=snmpWalk(host,community,'1.3.6.1.2.1.4.22.1.2')
    result['arpnum']=len(arptable)

    return result

# ---------------------------------------------------------------------------------------
# 获路由表数目
def getroutetable(ver,host,community):
    result={}
    result['routenum']=snmpWalk(host,community,'1.3.6.1.2.1.4.24.6')[0].split(':')[-1]

    return result

# 获取cpu负载,目前适用于华为
def getcpuload(ver, host, community):
    result = {}
    if host not in ['30.15.1.1','30.0.0.15']:
        result['fiveSecUsed'] = snmpWalk(host, community, '1.3.6.1.4.1.2011.6.3.4.1.2')[0].split(':')[-1]
        result['oneMinUsed'] = snmpWalk(host, community, '1.3.6.1.4.1.2011.6.3.4.1.3')[0].split(':')[-1]
        result['fiveMinUsed'] = snmpWalk(host, community, '1.3.6.1.4.1.2011.6.3.4.1.4')[0].split(':')[-1]
    else:
        result['fiveSecUsed'] =snmpWalk(host, community, '1.3.6.1.4.1.25506.2.6.1.1.1.1.6.192')[0].split(':')[-1]
        result['oneMinUsed']=snmpWalk(host, community, '1.3.6.1.4.1.25506.2.6.1.1.1.1.33.192')[0].split(':')[-1]
        result['fiveMinUsed']=snmpWalk(host, community,'1.3.6.1.4.1.25506.2.6.1.1.1.1.34.192')[0].split(':')[-1]
    return result


# ---------------------------------------------------------------------------------------
# 获取内存使用情况 目前适用于华为
def getmemory(ver, host, community):
    result = {}
    if host not in ['30.15.1.1','30.0.0.15']:
        result['memTotalReal'] = snmpWalk(host, community, '1.3.6.1.4.1.2011.6.3.5.1.1.2')[0].split(':')[-1]
        result['memTotalFree'] = snmpWalk(host, community, '1.3.6.1.4.1.2011.6.3.5.1.1.3')[0].split(':')[-1]
        '''单位字节1'''
        result['memTotalUsed'] = int(result['memTotalReal']) - int(result['memTotalFree'])
        result['memTotalPer'] = float(result['memTotalUsed']) / int(result['memTotalReal'])
    else:
        result['memTotalReal']=snmpWalk(host, community, '1.3.6.1.4.1.25506.2.6.1.1.1.1.10.192')[0].split(':')[-1]
        result['memTotalPer'] =float(snmpWalk(host, community, '1.3.6.1.4.1.25506.2.6.1.1.1.1.8.192')[0].split(':')[-1])/100
        result['memTotalUsed']=int(result['memTotalReal'])*float(result['memTotalPer'])
        result['memTotalFree'] =int(result['memTotalReal'])*(1-float(result['memTotalPer']))
    return result


# ---------------------------------------------------------------------------------------
# 获取ping延时、丢包信息
def getping(host):
    result = {}
    ip_address = ip
    response = ping.quiet_ping(ip_address)

    result['package_lost'] = response[0]
    result['mrtt'] = response[1]
    result['artt'] = response[2]

    return result


# ---------------------------------------------------------------------------------------
# 获取网卡信息
def getinterface(ver, host, community):
    result = {}

    '''
    获取网卡列表
    '''
    PortDevices_mib = snmpWalk(host, community, 'RFC1213-MIB::ifDescr')
    ifcard = []
    for item in PortDevices_mib:
        ifcard.append(item.split(':')[3].strip())
    result['ifcard'] = ifcard

    '''
    获取对应的入流量
    '''
    In_Flow_mib = snmpWalk(host, community, 'IF-MIB::ifInOctets')
    ifInOctets = []
    for item in In_Flow_mib:
        ifInOctets.append(item.split(':')[3].strip())
    result['ifInOctets'] = [i/gaptime for i in ifInOctets]

    '''
    获取对应的出流量
    '''
    Out_Flow_mib = snmpWalk(host, community, 'IF-MIB::ifOutOctets')
    ifOutOctets = []
    for item in Out_Flow_mib:
        ifOutOctets.append(item.split(':')[3].strip())
    result['ifOutOctet'] = ifOutOctets
    # print result

    result['flowin']=dict(zip(ifcard,[i/gaptime for i in ifInOctets]))#这里先除去间隔时间，web中娶到的数即为国际单位，但是存在采样时间误差
    result['flowout']=dict(zip(ifcard,[i/gaptime for i in ifOutOctets]))

    return result


# ---------------------------------------------------------------------------------------
# 获取全部信息
def getallinfo(ver, hostip, community):
    info = {}
    ret = getcpuload(ver, hostip, community)  # cpu负载
    info.update(ret)

    ret = getmemory(ver, hostip, community)  # 内存使用情况
    info.update(ret)

    ret = getinterface(ver, hostip, community)  # 网卡、流量情况
    info.update(ret)

    ret=getarptable(ver,hostip,community) #arp
    info.update(ret)

    ret=getmactable(ver,hostip,community) #mac
    info.update(ret)

    ret=getroutetable(ver,hostip,community)#route
    info.update(ret)

    ret = getping(hostip)#获取延时信息
    info.update(ret)

    info['time'] = datetime.datetime.now()  # 时间
    info['serverip'] = hostip  # 服务器IP
    return info


# ---------------------------------------------------------------------------------------
# 入库
def insertdb(info):
    client = MongoClient('127.0.0.1', 27017)
    monitor = client.monitor_huawei
    monitorlog = monitor.monitorlog_huawei
    monitorlog.insert(info)
    # print info


# ---------------------------------------------------------------------------------------
# 主函数
if __name__ == '__main__':
    while True:
        # 需要获取信息的服务器IP
        iplist = getlist()
        for ip in iplist:
            print "%s %s %s" % ("-" * 50, ip, "-" * 50)
            insertdb(getallinfo(2, ip, getcommunity(ip)))
            print getallinfo(2, ip, getcommunity(ip))

        # 获取信息时间间隔为1分钟
        time.sleep(60 * 1)
