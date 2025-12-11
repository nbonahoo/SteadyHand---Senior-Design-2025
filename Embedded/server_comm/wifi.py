import network
import machine

# ssid = "Jordan iPhone"
# password = "wifiwifiwifi"

ssid = "Jordan iPhone"
password = "wifiwifiwifi"

def do_connect():

    wlan = network.WLAN()
    wlan.active(True)
   
    print('connecting to network...')
    wlan.connect(ssid, password)
    i = 0
    while not wlan.isconnected():
        if i is 5000:
            print('connection failed, trying again')
            i = 0
        i += 1
        machine.idle()

    print('network config:', wlan.ipconfig('addr4')[0])

def do_disconnect():
    wlan = network.WLAN() 
    if wlan.isconnected():
        print("Disconnecting from network:", wlan.config('essid'))
        wlan.disconnect()      
        wlan.active(False)   
        print("Disconnected.")
    else:
        print("No active Wi-Fi connection found.")

# do_disconnect()
# do_connect()
