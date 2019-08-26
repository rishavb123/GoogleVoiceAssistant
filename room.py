import requests

server_ip = "192.168.1.68"
port = 8000
key = "blueberrypineapplecactikoi1025"

lights_url = "http://{}:{}/lights?admin_key={}".format(server_ip, port, key)
thermostat_url = "http://{}:{}/thermostat?admin_key={}".format(server_ip, port, key)

def lights(state):
    param = "&state=" + state
    print(requests.get(lights_url + param).text)

def thermostat(temp):
    temp = str(temp)
    param = "&temp=" + temp
    print(requests.get(thermostat_url + param).text)