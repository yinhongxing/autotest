import time
import threading



class SerialThread(threading.Thread):
    def __init__(self, Ser,Wifi_status,Wifi_test_status,q):
        super(SerialThread, self).__init__()
        self.Ser = Ser
        self.q = q
        self.Wifi_status = Wifi_status
        self.Wifi_test_status = Wifi_test_status
        self.start()
        self.flag = 0
        self.datalen=0
        self.curpklen=0
        self.databuf =[0]*1024
        self.nowtime = 0
        self.oldtime = 0
        self.oldversion = ""
        self.newversion = ""
        self.msgcode={2:self.connect_wifi,3:self.disconnect_wifi,4:self.connect_cloud,5:self.disconnect_cloud,39:self.wifi_state,68:self.wifi_recv_msg,13:\
            self.wifi_recv_ntp,51:self.license_ok}
        self.stacode ={2:self.wifi_con_redirect,3:self.wifi_con_gateway,4:self.wifi_license,6:self.wifi_unbind_ok,7:self.wifi_init_ok,5:self.wifi_version,\
                       8:self.wifi_deviceid,9:self.wifi_bind_ok,10:self.wifi_heartbeat_ok,11:self.wifi_deviceip}
        self.wifitype = {"HF":1,"MX":2,"MA":3,"QC":4,"ES":9,"RT":10,"AI":11}
    def run(self):
        while True:
            if self.Ser.isOpen() and self.Ser.inWaiting():
                self.n=self.Ser.inWaiting()
                self.text = self.Ser.read(self.n)
                self.DataRecv()
                #wx.CallAfter(Publisher.sendMessage('update', text))
                #Publisher.sendMessage('update', text)
                ##print self.text
            time.sleep(0.01)

    def data_pack(self,payload_data_len, lan_id, msg_id, msg_code, payload_data, send_data):
        sum = 0
        send_data[0] = 0x5A
        data_len = payload_data_len + 8
        send_data[1] = data_len >> 8
        send_data[2] = data_len % 256
        send_data[3] = msg_id
        send_data[4] = lan_id
        send_data[5] = msg_code
        for i in range(payload_data_len):
            send_data[i + 6] = payload_data[i]
        for i in range(data_len - 3):
            sum = sum + send_data[i + 1]
        send_data[data_len - 2] = sum & 0xff
        send_data[data_len - 1] = 0x5B
    def start_test(self):
        payload_data = [0xF0, 0x0F]
        send_data = [0] * 10
        self.data_pack(0x2, 0, 1, 0x27, payload_data, send_data)
        # #print send_data
        self.Ser.write(send_data)
    def unbind(self):
        payload_data = [0xA6, 0x6A]
        send_data = [0] * 10
        self.data_pack(0x2,0, 1, 0x24, payload_data, send_data)
        #  #print send_data
        self.Ser.write(send_data)
    def smartlink(self):
        payload_data = [0xD8,0x8D]
        send_data = [0] * 10
        self.data_pack(0x2,0, 1, 0x8, payload_data, send_data)
        # #print send_data
        self.Ser.write(send_data)
    def reboot_wifi(self):
        payload_data = [0xB7, 0x7B]
        send_data = [0] * 10
        self.data_pack(0x2,0, 1, 0xB, payload_data, send_data)
        # #print send_data
        self.Ser.write(send_data)
    def get_ntp(self):
        payload_data = [0xF0, 0x0F]
        send_data = [0] * 10
        self.data_pack(0x2, 0, 1, 0xD, payload_data, send_data)
       # #print send_data
        self.Ser.write(send_data)

    def license_ok(self):
        payload_data = [0xF4, 0x4F]
        send_data = [0] * 10
        self.data_pack(0x2, 0, 1, 0x33, payload_data, send_data)
        # #print send_data
        self.Ser.write(send_data)
    def wifi_bind_ok(self):
        self.Wifi_status.Bind = 1
    def wifi_unbind_ok(self):
        self.Wifi_status.Ubind = 1
    def connect_wifi(self):
        payload_data=[0xff,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x03,0x00,0x06,0xC0,0x43,0xF8,0x9F,0x3F,0x4A,0xF6,0x9B,\
                      0xA2,0x71,0xD3,0xB5,0xAA,0x9E,0xB9,0xDE,0xF6,0x7C,0x45,0x61,0x0C,0x3A,0xAD,0x82,0xCE,0x4F,0x4B,0xCF,\
                      0xBC,0x34,0xB2,0xB5,0xF9,0x05,0xFB,0x12,0x02,0x63,0xCC,0x61,0x88,0x28,0x59,0xFD,0x8E,0x37,0x1E,0x27,\
                      0xC5,0xA6,0xEA,0xF0,0xAD,0x66,0x87,0x2E,0x7F,0x3F,0x7C,0x63,0x5A,0x01,0x4D,0xC3,0x80,0x68,0x87,0x18,\
                      0xB8,0x46,0xC1,0xE3,0x21,0x14,0xBD,0xA2,0xB3,0xAC,0xD4,0x4D,0xAE,0x27,0xBF,0x87,0xC6,0x22,0x3B,0x26,\
                      0xBB,0x34,0xA3,0x53,0x9F,0x70,0xDA,0xA5,0xE6,0xEF,0xC1,0x36,0xE1,0x46,0xD2,0x32,0xE6,0xEB,0x91,0xEC,\
                      0x68,0x42,0x9D,0xD2]
        payload_data[0] = self.Wifi_status.Env
        send_data=[0]*133
        self.Wifi_status.ConWifi = 1
        #print "connect wifi \n"
        self.data_pack(0x7d,0,0,7,payload_data,send_data)
        ##print send_data
        self.Ser.write(send_data)

    def disconnect_wifi(self):
        self.Wifi_status.ConWifi = 0
        #print "disconnect_wifi"
    def connect_cloud(self):
        #print "connect_cloud"
        self.Wifi_status.ConCloud = 1
    def disconnect_cloud(self):
        self.Wifi_status.DisConCloud = 1
        #print "disconnect_cloud"



    def wifi_recv_msg(self):
        if self.databuf[4]==1:
            payload_data =[0x00,0x00,0x00,0x00,0x01,0x00,0x00,0x00]
            for i in range(4):
                payload_data[i] = self.databuf[6+i]
            send_data = [0]*0x10
            print "lan recv \n"
            self.data_pack(0x8, 1, self.databuf[3], 0x66, payload_data, send_data)
        else:
            payload_data = [0x01, 0x00, 0x00, 0x00]
            send_data = [0] * 0x0c
            print "cloud recv \n"
            self.data_pack(0x4, 0, self.databuf[3], 0x66, payload_data, send_data)
        self.Ser.write(send_data)

    def wifi_recv_ntp(self):
        now = int(time.time())
        recv_time = self.databuf[14]*(1<<24) + self.databuf[15]*(1<<16) + self.databuf[16]*(1<<8) + self.databuf[17]
        if abs(now-recv_time) <10:
            self.q.put(1)
        else:
            self.q.put(0)
    def wifi_license(self):
        #print "license ok"
        if self.databuf[40] == 1:
            for i in range(29):
                if self.databuf[i+11] >= 128:
                    self.databuf[i + 11] = self.databuf[i + 11] - 256
                self.Wifi_status.Wifilicense[i] = self.databuf[i+11]

        #print self.Wifi_status.Wifilicense
    def wifi_init_ok(self):
        #print "wifi init ok"

        self.Wifi_status.status_init()
    def wifi_con_redirect(self):
        self.Wifi_status.ConRedirect += 1
        #print "wifi con redirect %d" %(self.Wifi_status.ConRedirect)
    def wifi_con_gateway(self):
        self.Wifi_status.ConGateway += 1
        #print "wifi con gateway %d" %(self.Wifi_status.ConGateway)
    def wifi_version(self):
        WifiVersion =[0]*20
        for i in range(20):
           WifiVersion[i]=chr(self.databuf[7+i])
        self.Wifi_status.WifiVersion = ''.join(WifiVersion)
        self.oldversion = self.newversion
        self.newversion = self.Wifi_status.WifiVersion
        self.Wifi_status.Wifitype = self.wifitype[self.Wifi_status.WifiVersion[0:2]]
        if self.oldversion !=self.newversion:
            self.Wifi_test_status.ota_test_success_count +=1
        else:
            self.Wifi_test_status.ota_test_fail_count +=1
       # #print "ota_test_success_count is %d,ota_test_fail_count is %d" %(self.Wifi_test_status.ota_test_success_count,\
                                                                       #  self.Wifi_test_status.ota_test_fail_count)
        self.q.put(3)
        ##print ("%s" % (self.Wifi_status.WifiVersion))
        ##print "wifi version ok"
    def wifi_deviceip(self):
        self.Wifi_status.DeviceIp = str(self.databuf[10])+'.'+str(self.databuf[9])+'.'+str(self.databuf[8])+'.'+str(self.databuf[7])
       # print self.Wifi_status.DeviceIp
    def wifi_deviceid(self):
        DeviceId = [0]*12
        for i in range(12):
            DeviceId[i] = chr(self.databuf[7 + i])
        self.Wifi_status.DeviceId =''.join(DeviceId)
       # #print self.Wifi_status.DeviceId
      # #print "wifi deviceid ok"
    def wifi_heartbeat_ok(self):
        self.oldtime = self.nowtime
        self.nowtime = int(time.time())
        ##print "wifi heartbeat ok"
    def wifi_state(self):
        try:
            self.stacode[self.databuf[6]]()
        except KeyError:
            print "stacode keyError %d" % (self.databuf[6])
    def DateUnpack(self):
        try:
            self.msgcode[self.databuf[5]]()
        except KeyError:
            print "msgcode keyError %d"  % (self.databuf[5])
    def DataRecv(self):
            for i in range(self.n):
                data=ord(self.text[i])
                #print  data
                if self.flag == 0:
                    if data == 0x5A:
                        self.flag = 1
                        self.datalen=1
                        self.curpklen=0
                elif self.flag == 1:
                    self.databuf[self.datalen]=data
                    self.datalen+=1
                    if self.datalen==2:
                        self.curpklen = data<<8
                    elif self.datalen==3:
                        self.curpklen=self.curpklen+data
                    elif self.curpklen==self.datalen:
                        if data==0x5b:
                            #print "recv data\n"
                            self.DateUnpack()
                        else:
                            print "error data end\n"
                        self.flag=0
                        self.curpklen=0
                        self.datalen=0