# -*- coding:utf8 -*-
import os
from datetime import time

import pymongo
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from pymongo import MongoClient

from tornado.options import define, options

define("port", default=9998, help="run on the given port", type=int)
define("dbhost", default='192.168.43.116')
define("dbport", default=27017, help="run on the given port", type=int)


def insertdb(info):
    client = MongoClient('192.168.43.116', 27017)
    monitor = client.switchlist
    monitorlog = monitor.switchlistlog
    monitorlog.insert(info)
def deldb(ipaddr):
    client1 = MongoClient('192.168.43.116', 27017)
    client2 = MongoClient('192.168.43.116', 27017)
    monitor1 = client1.switchlist
    print monitor1
    monitor2= client2.monitor_huawei
    print monitor2
    monitorlog1 = monitor1.switchlistlog
    monitorlog2 = monitor2.monitorlog_huawei
    monitorlog1.remove({"ipaddr":ipaddr})
    monitorlog2.remove({"serverip":ipaddr})

class addHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("add.html")
    def post(self):
        ipaddr=self.get_argument("ipaddr")
        community=self.get_argument("community")
        info={
            'ipaddr':ipaddr,
            'community':community
        }
        insertdb(info)
        self.redirect('/')
class delHandler(tornado.web.RequestHandler):
    def get(self,ipaddr):
        ip=ipaddr
        print ip
        deldb(ip)
        self.redirect('/show')


class showHandler(tornado.web.RequestHandler):
    def get(self):
        conn = MongoClient(host=options.dbhost, port=options.dbport)
        # select db
        db = conn.switchlist
        # select connection
        monitorlog = db.switchlistlog
        servers = monitorlog.distinct('ipaddr')  # 看有多少serverip
        server_info = []
        for server in servers:
            info = monitorlog.find({'ipaddr': server}).sort('time', -1).limit(1)
            print type(info),info
            for i in info:
                tmp = {}
                tmp['ipaddr'] = i['ipaddr']
                tmp['community']= i['community']

                server_info.append(tmp)

        self.render("show.html", server_info=server_info)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # Connect to Mongodb
        conn = MongoClient(host=options.dbhost, port=options.dbport)
        # select db
        db = conn.monitor_huawei
        # select connection
        monitorlog = db.monitorlog_huawei
        servers = monitorlog.distinct('serverip')#distint查询不同的ip
        print servers
        server_info = []
        for server in servers:
            info = monitorlog.find({'serverip': server}).sort('time', -1).limit(1)#每个info代表当前主机最新(第一条)的一条数据
            print info
            server_info.append(info)#server_info代表当前一组主机中最新的一批数据
        self.render("index.html", servers=servers, server_info=server_info)#展示到前面


class DetailHandler(tornado.web.RequestHandler):
    def chu(self,arg):
        return round(arg/1024/1024,3)
    def get(self, argv):
        serverip = argv#这里的ip就是前边点击之后传过来的那个
        print serverip
        conn = MongoClient(host=options.dbhost, port=options.dbport)
        # select db
        db = conn.monitor_huawei
        # select connection
        monitorlog = db.monitorlog_huawei
        server_info = monitorlog.find({'serverip': serverip}).sort('time', -1).limit(120) #当前主机前120条数据
        # print server_info
        categories = []
        fiveSecUsed = []  # oneM = []
        oneMinUsed = []  # fiveM = []
        fiveMinUsed = []  # fifteenM = []
        memTotalReal = []
        memTotalFree = []
        memTotalUsed = []
        memTotalPer = []
        flowin=[]
        flowout=[]
        # ifInOctets=[]
        # ifOutOctet=[]
        ifcard=[]
        package_lost=[]
        mrtt=[]
        artt=[]

        for item in server_info:
            # print item
            categories.append(str(item['time'])[:-7])#按时间得到时间的序列
            # print categories
            fiveSecUsed.append(float(item['fiveSecUsed']))#得到FSEC的序列list
            oneMinUsed.append(float(item['oneMinUsed']))
            fiveMinUsed.append(float(item['fiveMinUsed']))
            memTotalReal.append(self.chu(float(item['memTotalReal'])))
            memTotalFree.append(self.chu(float(item['memTotalFree'])))
            memTotalUsed.append(self.chu(float(item['memTotalUsed'])))
            memTotalPer.append(item['memTotalPer'])
            package_lost.append(float(item['package_lost']))
            mrtt.append(float(item['mrtt']))
            artt.append(float(item['artt']))

            # ifInOctets=item['ifInOctets']
            flowin.append(item['flowin'])#内容为字典的字典，如何按照名称取数？？？
            # ifInOctets= [int(i) for i in item['ifInOctets']]
            # ifOutOctet = item['ifOutOctet']
            flowout.append(item['flowout'])#内容为字典的字典，如何按照名称取数？？？
            # ifOutOctet=[int(i) for i in item['ifOutOctet']]
            # ifcard = item['ifcard']
            ifcard.append(item['ifcard'])
        list_in=[]
        list_out=[]
        # print flowin
        print ifcard[-1]
        for card in ifcard[-1]:
            _in=[]
            _out=[]
            for item in flowin:
                _in.append(self.chu(float(item[card])))
            temp_in=_in[::-1]
            list_in.append(list(map(lambda x:round(temp_in[x]-temp_in[x-1],3),range(1,len(temp_in)))))
            for item in flowout:
                _out.append(self.chu(float(item[card])))
            temp_out=_out[::-1]
            list_out.append(list(map(lambda x:round(temp_out[x]-temp_out[x-1],3),range(1,len(temp_out)))))
                # break
        print list_in
        # list_in=[ i/60 for i in list_in]
        print list_in
        print list_out
        print categories

        self.render("detail.html", serverip=serverip, categories=categories[::-1], \
                    fiveSecUsed=fiveSecUsed, oneMinUsed=oneMinUsed, fiveMinUsed=fiveMinUsed, \
                    memTotalReal=memTotalReal, memTotalFree=memTotalFree, memTotalUsed=memTotalUsed, \
                    memTotalPer=memTotalPer,ifcard=list(map(str,ifcard[-1])), \
                    package_lost=package_lost,mrtt=mrtt,artt=artt,list_out=list_out,list_in=list_in
                    )


def main():
    settings = dict(
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
    )
    # print(type(settings))

    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/add", addHandler),
        (r"/show", showHandler),
        (r"/detail/(.*)", DetailHandler),
        (r"/del/(.*)", delHandler),
    ], **settings)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
