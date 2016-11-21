import time
import threading
import Queue
import sys
import demjson
import socket
import datetime
class SocketThread(threading.Thread):
    def __init__(self,q):
        threading.Thread.__init__(self)
        self.q =q
        self.s = socket.socket()
        self.host = socket.gethostname()
        self.port = 4689
        self.s.bind(('', self.port))
        self.s.listen(5)
        self.c, (remotehost, remoteport) = self.s.accept()
        ##print ("[%s:%s]connect " % (remotehost, remoteport))
        self.start()
    def run(self):

        while True:

            while True:
               # revcData = self.c.recv(1024)
                try:
                    revcData = self.c.recv(1024)
                except socket.error:
                    self.c.close()
                    print "recv socket.error"
                    break
                if not len(revcData):
                    print "close socket"
                    self.c.close()
                    break
                #data = ord(revcData[2])
                now = datetime.datetime.now()
                otherStyleTime = now.strftime("%Y-%m-%d %H:%M:%S")
                print otherStyleTime+"recvdata"+revcData
                self.q.put(revcData)
               # #print data
            self.c, (remotehost, remoteport) = self.s.accept()
            print ("[%s:%s]connect " % (remotehost, remoteport))
            ##print revcData
        self.c.close()

    def net_data_pack(payload_data_len, msg_id, msg_code, payload_data, send_data):
        send_data[0] = 4
        send_data[1] = msg_id
        send_data[2] = msg_code
        send_data[3] = 0
        send_data[4] = payload_data_len >> 8
        send_data[5] = payload_data_len % 256
        send_data[6] = 0
        send_data[7] = 0
        for i in range(payload_data_len):
            send_data[i + 8 ]= payload_data[i]
    def net_send(self,data):
        json = demjson.encode(data)
        now = datetime.datetime.now()
        otherStyleTime = now.strftime("%Y-%m-%d %H:%M:%S")
        print otherStyleTime+json

        self.q.queue.clear()
        #self.c.send(json)
        try:
            self.c.send(json)
        except socket.error:
            self.c.close()
            print "send socket.error"
    def smartlink(self,wifissid,wifi_type,is_smarlink,is_bind,deviceid):
        data = {"msgcode":1,"wifissid":wifissid,"type":wifi_type,"is_smartlink":is_smarlink,"is_bind":is_bind, "deviceid": deviceid}
        self.net_send(data)
    def is_bind(self,deviceid):
        data = {"msgcode":2,"deviceid": deviceid}
        self.net_send(data)
    def con_receptacle(self,channel,switch):
        data = {"msgcode":3,"channel": channel,"switch":switch}
        self.net_send(data)
    def con_wifi(self,switch,deviceid):
        data = {"msgcode": 4,"switch":switch, "deviceid": deviceid}
        self.net_send(data)
    def wifi_license(self,deviceid,deviceip):
        data = {"msgcode": 5, "deviceid": deviceid,"ip":deviceip}
        self.net_send(data)
    def is_online(self,deviceid,env):
        data = {"msgcode": 6, "deviceid": deviceid, "env": env}
        self.net_send(data)
    def con_lan_wifi(self,switch,deviceid,deviceip):
        data = {"msgcode": 7,"switch":switch, "deviceid": deviceid,"ip":deviceip}
        self.net_send(data)