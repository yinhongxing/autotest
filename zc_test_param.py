class wifi_test_parameter:
    def __init__(self):
        self.uart_port = 'com33'
        self.uart_baud = 9600
        self.is_continue = 1
        self.ota_test_count = 0
        self.connect_difrouter_test_count = 1
        self.connect_info_test_count = 1
        self.bind_ubind_test_count = 1
        self.ntp_test_count = 1
        self.router_disnet_test_count = 1
        self.router_blackout_test_count = 1
        self.headbeat_test_count = 1
        self.con_wifi_test_count = 1
        self.con_lan_wifi_test_count = 1
        self.unite_firmware_test_count = 1
        self.license_test_count = 1
class wifi_status:
    def __init__(self):
        self.WifiVersion = "1"
        self.ConRedirect = 0
        self.ConGateway = 0
        self.ConCloud = 0
        self.DisConCloud = 0
        self.Ubind = 0
        self.bind = 0
        self.DeviceId = "C8934693EEF3"
        self.Env = 0xff
        self.IsOutTime = 0
        self.ConWifi = 0
        self.Wifilicense = [0]*29
        self.Applicense = [0]*29
        self.Wifitype = 2
        self.DeviceIp =""
    def status_init(self):
        self.ConRedirect = 0
        self.ConGateway = 0
        self.ConCloud = 0
        self.DisConCloud = 0
        self.Ubind = 0
        self.Bind = 0
        self.ConWifi = 0
        #self.wifilicense = [0] * 29
        #self.applicense = [0] * 29
class wifi_test_status:
    def __init__(self):
        self.ota_test_fail_count = 0
        self.ota_test_success_count = 0
        self.connect_difrouter_test_fail_count = 0
        self.connect_info_test_fail_count = 0
        self.bind_ubind_test_fail_count = 0
        self.ntp_test_fail_count = 0
        self.router_disnet_test_fail_count = 0
        self.router_blackout_test_fail_count = 0
        self.headbeat_test_fail_count = 0
        self.con_wifi_test_fail_count = 0
        self.con_lan_wifi_test_fail_count = 0
        self.unite_firmware_test_fail_count = 0
        self.smarlink_fail_count = 0
        self.all_test_fail_count = 0