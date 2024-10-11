import logging
import requests


# You can find some more functions here:
# https://developer.arylic.com/httpapi
# https://github.com/Jan21493/Linkplay
# https://github.com/AndersFluur/LinkPlayApi/blob/a11fefcf931827ff3d364d6a3b49575dd0bfc50f/api.md


class LinkPlay:

    def __init__(self, ip: str = '10.10.10.254'):
        if not ip.endswith('254'):
            logging.warning('IP address should normally end with 254')

        self.ip = ip

    def _send_cmd(self, cmd: str, params: str=None) -> requests.Response:
        cmd = f'http://{self.ip}/httpapi.asp?command={cmd}'
        if params:
            cmd += f':{params}'
        r = requests.get(cmd)
        r.raise_for_status()
        return r

    def list_wifi_networks(self):
        res = self._send_cmd('wlanGetApListEx', '')
        nets = []
        for wifi in res.json().get('aplist', []):
            ssid_hex = wifi.get('ssid', '')
            ssid = bytes.fromhex(ssid_hex).decode('utf-8')
            rssi = wifi.get('rssi', '')
            auth = wifi.get('auth', '')
            encry = wifi.get('encry', '')
            nets.append({'ssid': ssid, 'rssi': rssi, 'auth': auth, 'encry': encry})
        return nets

    def connect_to_wifi_net(self, ssid: str, pwd: str, auth: str='WPA2PSK', encry: str='AES', ch: str='', chext: str='1'):
        ssid_hex = ssid.encode().hex()
        pwd_hex = pwd.encode().hex()
        params = f'ssid={ssid_hex}:ch={ch}:auth={auth}:encry={encry}:pwd={pwd_hex}:chext={chext}'
        self._send_cmd('wlanConnectApEx', params)

    def getPlayerStatus(self):
        res = self._send_cmd('getPlayerStatus')
        return res.json()

    def setDeviceName(self, name: str):
        self._send_cmd('setDeviceName', name)
    

if __name__ == '__main__':
    w  = LinkPlay('10.10.10.254')
    w.setDeviceName('Salon')

    print('Available networks:')
    wifi_nets = w.list_wifi_networks()
    for wifi in wifi_nets:
        print(f'- {wifi["ssid"]} - rssi: {wifi["rssi"]} - auth: {wifi["auth"]}')

    wifi_ssid = input('Enter the SSID of the network you want to connect to: ')
    if wifi_ssid not in [wifi['ssid'] for wifi in wifi_nets]:
        print('SSID not found')
        exit(1)

    wifi_net = [wifi for wifi in wifi_nets if wifi['ssid'] == wifi_ssid][0]
    if wifi_net['auth'] != 'OPEN':
        wifi_pwd = input('Enter the password: ')
    else:
        wifi_pwd = ''


    print(f'Connecting to {wifi_ssid}...')
    w.connect_to_wifi_net(wifi_ssid, wifi_pwd, wifi_net['auth'], wifi_net['encry'])




