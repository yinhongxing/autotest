import Queue
import sys
import datetime
import demjson
import serial
import xml.dom
import xml.dom.minidom
import os
from zc_serial import  *
from zc_socket import  *
from zc_test_param import *
import xml.dom

class wifi_test:
    def __init__(self):
        self.test_case = {0:self.connect_difrouter_test,1:self.connect_info_test,2:self.bind_ubind_test,3:self.ntp_test,\
                          4:self.router_disnet_test,
                          5:self.router_blackout_test,\
                          6:self.headbeat_test,\
                          7:self.unite_firmware_test,\
                          8:self.con_wifi_test,\
                          9:self.con_lan_wifi_test,\
                          10:self.license_test}
        self.Wifi_test_parameter = wifi_test_parameter()
        self.Wifi_status = wifi_status()
        self.test_count ={0:self.Wifi_test_parameter.connect_difrouter_test_count,1:self.Wifi_test_parameter.connect_info_test_count, \
                          2: self.Wifi_test_parameter.bind_ubind_test_count, 3: self.Wifi_test_parameter.ntp_test_count, \
                          4: self.Wifi_test_parameter.router_disnet_test_count, 5: self.Wifi_test_parameter.router_blackout_test_count, \
                          6: self.Wifi_test_parameter.headbeat_test_count, 7: self.Wifi_test_parameter.unite_firmware_test_count,\
                          8: self.Wifi_test_parameter.con_wifi_test_count,
                          9: self.Wifi_test_parameter.con_lan_wifi_test_count, 10: self.Wifi_test_parameter.license_test_count}
        self.wifitype = {"HF": 1, "MX": 2, "MA": 3, "QC": 4, "ES": 9, "RT": 10, "AI": 11}
        self.Wifi_test_status = wifi_test_status()
        self.select_load_parm()
        self.Ser = serial.Serial(self.Wifi_test_parameter.uart_port, self.Wifi_test_parameter.uart_baud, timeout=0.5)
        self.socketQueue = Queue.Queue(100)
        self.serialQueue = Queue.Queue(100)
        self.serialThread = SerialThread(self.Ser,self.Wifi_status,self.Wifi_test_status,self.serialQueue)
        self.socketThread = SocketThread(self.socketQueue)
        self.serialThread.reboot_wifi()
        time.sleep(5)
        while True:
            self.Wifi_test_status.all_test_fail_count = 0
            self.Wifi_test_status.smarlink_fail_count = 0
            self.Wifi_status.status_init()
            self.Wifi_status.Env = 0xff
            self.serialThread.reboot_wifi()
            for i in range(len(self.test_count)):
                rtn = self.case_test_count(i)
                if 1 != rtn:
                     self.Wifi_test_status.all_test_fail_count += 1
                     if i == 2:
                         break
                     if 0 == self.Wifi_test_parameter.is_continue:
                         continue
            # #rtn = self.ota_test(self.Wifi_test_parameter.ota_test_count)
            # if 1 != rtn:
            #     self.Wifi_test_status.all_test_fail_count += 1
            #     if 0 == self.Wifi_test_parameter.is_continue:
            #         continue
            print "smarlink fail count is %d" % (self.Wifi_test_status.smarlink_fail_count)
            if 0 == self.Wifi_test_status.all_test_fail_count:
                print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!test success!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            else:
                print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!test fail!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

    def create_element(self,doc, tag, attr):
        elementNode = doc.createElement(tag)
        textNode = doc.createTextNode(attr)
        elementNode.appendChild(textNode)
        return elementNode
    def save_param(self):
        dom1 = xml.dom.getDOMImplementation()
        doc = dom1.createDocument(None, "info", None)
        top_element = doc.documentElement
        sNode = doc.createElement('list')
        sNode.setAttribute('id', "1")
        uart_portNode = self.create_element(doc, 'uart_port',self.Wifi_test_parameter.uart_port )
        uart_baudNode = self.create_element(doc, 'uart_baud', str(self.Wifi_test_parameter.uart_baud))
        wifi_typeNode = self.create_element(doc, 'wifi_type', str(self.Wifi_status.Wifitype))
        sNode.appendChild(uart_portNode)
        sNode.appendChild(uart_baudNode)
        sNode.appendChild(wifi_typeNode)
        top_element.appendChild(sNode)
        xmlfile = open('autotest.xml', 'w')
        doc.writexml(xmlfile,'',' ','\n','utf-8')
        xmlfile.close()
    def load_param(self):
        dom1 = xml.dom.minidom.parse('autotest.xml')
        root = dom1.documentElement
        paramnode = root.getElementsByTagName('list')[0]
        self.Wifi_test_parameter.uart_port = paramnode.getElementsByTagName('uart_port')[0].childNodes[0].nodeValue.strip()
        self.Wifi_test_parameter.uart_baud = int(paramnode.getElementsByTagName('uart_baud')[0].childNodes[0].nodeValue.strip())
        self.Wifi_status.Wifitype = int(paramnode.getElementsByTagName('wifi_type')[0].childNodes[0].nodeValue.strip())
    def custom_parm(self):
        input = raw_input("please input uart port (e.g 11)")
        if input != "":
            self.Wifi_test_parameter.uart_port = "com" + input
        input = raw_input("please input uart baud (e.g 9600)")
        if input != "":
            self.Wifi_test_parameter.uart_baud = int(input)
        input = raw_input("please input wifi type (e.g mx)")
        if input != "":
            self.Wifi_status.Wifitype = self.wifitype[input[0:2].upper()]
        self.save_param()
    def select_load_parm(self):
        input = raw_input("please select parameter (default 2)\n1:use default parameter\n2:use load parameter\n3:use custom parameter\n ")
        if input != "1":
            if input =="2" or input =="":
                if(os.path.exists('autotest.xml')):
                    self.load_param()
                else:
                    print "not exists xml file use custom parameter"
                    self.custom_parm()
            else:
                self.custom_parm()
    def data_unpack(self,msgcode):
        try:
            self.IsOutTime = 0
            data = self.socketQueue.get(1, 80)
        except Queue.Empty:
            self.IsOutTime = 1
            print "recv data time out"
        if self.IsOutTime == 1:
            return 0
        else:
            now = datetime.datetime.now()
            otherStyleTime = now.strftime("%Y-%m-%d %H:%M:%S")
           # print otherStyleTime+data
            text = demjson.decode(data)
            if text["msgcode"] == msgcode and text["status"] == 1:
               # #print text["msgcode"]
               if msgcode == 5:
                   self.Wifi_status.Applicense = text["license"]
               else:

                return 1
            else:
                print "recv data err"+str(text)
                return 0
    def is_status_ok(self,status,time_count):
        for i in range(time_count):
            if status > 0:
                break
            else:
                time.sleep(1)
        if status > 0:
            return 1
        else:
            return 0
    def is_connect_cloud(self,time_count):
        for i in range(time_count):
            if self.Wifi_status.ConCloud > 0:
                break
            else:
                time.sleep(1)
        if self.Wifi_status.ConCloud > 0:
            return 1
        else:
            return 0

    def is_connect_wifi(self, time_count):
        for i in range(time_count):
            if self.Wifi_status.ConWifi > 0:
                break
            else:
                time.sleep(1)
        if self.Wifi_status.ConWifi > 0:
            return 1
        else:
            return 0
    def is_bind(self,time_count):
        for i in range(time_count):
            if self.Wifi_status.Bind > 0:
                break
            else:
                time.sleep(1)
        if self.Wifi_status.Bind > 0:
            return 1
        else:
            return 0
    def case_test_count(self,test_id):
        flag = 0
        test_case_list = str(self.test_case[test_id]).split(' ', 3 );
        test_case_name = test_case_list[2]
        now = datetime.datetime.now()
        otherStyleTime = now.strftime("%Y-%m-%d %H:%M:%S")
        print "%s %s start" % (otherStyleTime,test_case_name)
        for self.i in range(self.test_count[test_id]):
            if self.test_case[test_id]() == 0:
                flag +=1
        now = datetime.datetime.now()
        otherStyleTime = now.strftime("%Y-%m-%d %H:%M:%S")
        if flag == 0:
            print "%s %s success" % (otherStyleTime,test_case_name)
            return 1
        else:
            print "%s !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!%s test count %d,fail count %d!!!!!!!!!!!!!!!!!!!!!!!!!" % (otherStyleTime,test_case_name, self.test_count[test_id], flag)
            return 0

    def connect_difrouter_test(self):
        while True:
            self.Wifi_status.status_init()
            self.serialThread.smartlink()
            time.sleep(5)
            self.socketThread.smartlink("HW_test",self.Wifi_status.Wifitype,1, 0,self.Wifi_status.DeviceId)
            if self.data_unpack(1) == 0:
                self.Wifi_test_status.smarlink_fail_count += 1
            else:
                break
        if self.is_connect_cloud(60) != 1:
            print "err self.is_connect_cloud(60) != 1"
            return 0
        while True:
            self.Wifi_status.status_init()
            self.serialThread.smartlink()
            time.sleep(5)
            self.socketThread.smartlink("hexin", self.Wifi_status.Wifitype, 1, 0, self.Wifi_status.DeviceId)
            if self.data_unpack(1) == 0:
                self.Wifi_test_status.smarlink_fail_count += 1
            else:
                break
        if self.is_connect_cloud(60) != 1:
            print "err self.is_connect_cloud(60) != 1"
            return 0
        return 1
    def connect_info_test(self):
        while True:
            self.Wifi_status.status_init()
            self.serialThread.smartlink()
            time.sleep(5)
            self.socketThread.smartlink("hexin", self.Wifi_status.Wifitype, 1, 0, self.Wifi_status.DeviceId)
            if self.data_unpack(1) == 0:
                self.Wifi_test_status.smarlink_fail_count += 1
            else:
                break
        if  self.is_connect_cloud(60) != 1:
            print "err self.is_connect_cloud(60) != 1"
            return 0
        if self.Wifi_status.ConRedirect == 0 or self.Wifi_status.ConGateway == 0:
            print "err not connect redirect"
            return 0
        self.Wifi_status.status_init()
        self.serialThread.reboot_wifi()
        if self.is_connect_cloud(60) != 1:
            print "self.is_connect_cloud(60) != 1"
            return 0
        if self.Wifi_status.ConRedirect != 0  or self.Wifi_status.ConGateway == 0:
            print "err connect redirect"
            return 0
        return 1

    def bind_ubind_test(self):
        self.Wifi_status.status_init()
        self.serialThread.unbind()
        time.sleep(1)
        if self.Wifi_status.Ubind == 0:
            print "err ubind fail"
            return 0
        while True:
            self.serialThread.smartlink()
            time.sleep(10)
            self.socketThread.smartlink("hexin", self.Wifi_status.Wifitype, 1, 1, self.Wifi_status.DeviceId)
            if self.data_unpack(1) == 0:
                self.Wifi_test_status.smarlink_fail_count += 1
            else:
                break
        if self.is_connect_cloud(60) != 1:
            print "self.is_connect_cloud(60) != 1"
            return 0
        if self.is_bind(30) !=1:
            print "err bind fail"
            return 0
        return 1
    def ntp_test(self):
        self.serialQueue.queue.clear()
        self.serialThread.get_ntp()
        try:
            self.IsOutTime = 0
            data = self.serialQueue.get(1, 5)
        except Queue.Empty:
            return 0
        if data != 1:
            return 0
        return 1
    def router_disnet_test(self):
        if self.i == 0:
            self.socketThread.smartlink("HW_test", self.Wifi_status.Wifitype, 0, 0, self.Wifi_status.DeviceId)
            if self.data_unpack(1) == 0:
                return 0
            #time.sleep(10)
       # self.serialThread.reboot_wifi()
        self.Wifi_status.status_init()
        self.socketThread.con_receptacle(1,0)
        if self.data_unpack(3) == 0:
            return 0
        time.sleep(120)
       # if self.Wifi_status.DisConCloud ==0:
        #    flag += 1
       #     break
        for i in range(150):
            if self.Wifi_status.ConGateway >= 22:
                break
            else:
                time.sleep(4)
        if self.Wifi_status.ConGateway < 22:
            print "err reconnect gateway time out"
            while True:
                self.socketThread.con_receptacle(1, 1)
                if self.data_unpack(3) == 1:
                    break
            return 0
        for i in range(15):
            if self.Wifi_status.ConRedirect != 0:
                break
            else:
                time.sleep(4)
        if self.Wifi_status.ConRedirect == 0:
            print "err not connect redirect"
            while True:
                self.socketThread.con_receptacle(1, 1)
                if self.data_unpack(3) == 1:
                    break
            return 0
        self.Wifi_status.status_init()
        while True:
            self.socketThread.con_receptacle(1, 1)
            if self.data_unpack(3) == 1:
                break
        if self.is_connect_cloud(60) != 1:
            print "self.is_connect_cloud(60) != 1"
            return 0
        return 1

    def router_blackout_test(self):
        if self.i == 0:
            self.socketThread.smartlink("HW_test", self.Wifi_status.Wifitype, 0, 0, self.Wifi_status.DeviceId)
            if self.data_unpack(1) == 0:
                return 0
           # time.sleep(10)
        self.Wifi_status.status_init()
        self.socketThread.con_receptacle(2, 0)
        if self.data_unpack(3) == 0:
            return 0
        time.sleep(20)
        while True:
            self.socketThread.con_receptacle(2, 1)
            if self.data_unpack(3) == 1:
                break;
        if self.is_connect_cloud(60) == 0:
            print "self.is_connect_cloud(60) != 1"
            return 0
        return 1
    def headbeat_test(self):
        if self.i == 0:
            time.sleep(160)
        else:
            time.sleep(60)
        if abs(self.serialThread.nowtime-self.serialThread.oldtime-60)>3:
            return 0
        return 1
    def con_wifi_test(self):
        self.socketThread.con_wifi(1,self.Wifi_status.DeviceId)
        if self.data_unpack(4) == 0:
            return 0
        return 1
    def con_lan_wifi_test(self):
        if self.i == 0:
            self.socketThread.smartlink("hexin", self.Wifi_status.Wifitype, 0, 0, self.Wifi_status.DeviceId)
            if self.data_unpack(1) == 0:
                return 0
            #time.sleep(10)
        self.socketThread.con_lan_wifi(1,self.Wifi_status.DeviceId,self.Wifi_status.DeviceIp)
        if self.data_unpack(7) == 0:
            return 0
        return 1
    def unite_firmware_test(self):
        flag = 0
        self.Wifi_status.Env = 0x0
        self.serialThread.reboot_wifi()
        self.Wifi_status.status_init()
        if self.is_connect_cloud(60) == 0:
            print "self.is_connect_cloud(60) != 1"
            flag += 1
            #break
        self.socketThread.is_online(self.Wifi_status.DeviceId,self.Wifi_status.Env)
        if self.data_unpack(6) == 0:
            flag += 1
           # break
        self.Wifi_status.Env = 0xff
        self.serialThread.reboot_wifi()
        self.Wifi_status.status_init()
        if self.is_connect_cloud(60) == 0:
            print "self.is_connect_cloud(60) != 1"
            return 0
        self.socketThread.is_online(self.Wifi_status.DeviceId, self.Wifi_status.Env)
        if self.data_unpack(6) == 0:
            return 0
        if flag == 0:
            return 1
        else:

            return 0
    def ota_test(self,count):
        print "%s start" % (sys._getframe().f_code.co_name)
        if count != 0:
            self.Wifi_test_status.ota_test_fail_count = 0
            self.Wifi_test_status.ota_test_success_count = 0
        for i in range(count):
            data = self.serialQueue.get(1)
            print "ota_test_success_count is %d,ota_test_fail_count is %d" % (self.Wifi_test_status.ota_test_success_count, \
              self.Wifi_test_status.ota_test_fail_count)
    def license_test(self):
        self.serialThread.start_test()
        time.sleep(5)
        self.serialThread.reboot_wifi()
        self.Wifi_status.status_init()
        if self.is_connect_cloud(60) == 0:
            print "self.is_connect_cloud(60) != 1"
            return 0
        self.socketThread.wifi_license(self.Wifi_status.DeviceId,self.Wifi_status.DeviceIp)
        if self.data_unpack(5) == 0:
            return 0
        self.serialThread.reboot_wifi()
        self.Wifi_status.status_init()
        if self.is_connect_cloud(60) == 0:
            print "self.is_connect_cloud(60) != 1"
            return 0
        self.serialThread.reboot_wifi()
        self.Wifi_status.status_init()
        if self.is_connect_cloud(60) == 0:
            print "self.is_connect_cloud(60) != 1"
            return 0
        if self.Wifi_status.Applicense != self.Wifi_status.Wifilicense:
            return 0
        return 1

if __name__ == '__main__':
    test = wifi_test()
