import ping
def ping_host(ip):
    ip_address=ip
    response= ping.quiet_ping(ip)
    if response is not None:
        # delay=int(response*1000)
        # print delay
        print response

ping_host('www.baidu.com')