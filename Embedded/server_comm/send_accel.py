from time import sleep
import time
import machine
from machine import Pin, I2C, idle
import socket
import ds18x20
import onewire
import urequests

ssid = "Jordan iPhone"
password = "wifiwifiwifi"
DEST_IP = "172.20.10.4"
DEST_PORT = 5001
SERVER = "https://steadyhand-server.onrender.com/upload"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# MPU-6050 default I2C address
MPU6050_ADDR = 0x68
FULL_DUTY = 1023
# MPU-6050 Registers
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

# Initialize I2C on ESP32
# (SCL=22, SDA=21 are typical, but you can change them)
i2c = I2C(0, scl=Pin(20), sda=Pin(22), freq=400000)
pA0 = Pin(26)
pmA0 = machine.PWM(pA0)

pmA0.freq(10)
pmA0.duty(512)
sleep(1)
# pmA0.freq(1000)
sleep(1)
pmA0.freq(889)

print(hex(i2c.scan()[0]))
# Wake up MPU6050 (clear sleep bit)
i2c.writeto_mem(MPU6050_ADDR, PWR_MGMT_1, b'\x00')

# Temperature Pin Set up
ds_pin = machine.Pin(13)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()

POINTS_PER_PACKET = 50 # 3 seconds of 50hz samplings

def read_raw_data(addr):
    high, low = i2c.readfrom_mem(MPU6050_ADDR, addr, 2)
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value

def read_temp_data():
    ds_sensor.convert_temp()
    for rom in roms:
        return(ds_sensor.read_temp(rom))
    
def send_packet(packet):
    r = urequests.post(SERVER, json=packet)
    print(r.text)

def take_sample(Ax, Ay, Az, packet):
  # Read accelerometer data
#   acc_x = read_raw_data(ACCEL_XOUT_H)
#   acc_y = read_raw_data(ACCEL_XOUT_H + 2)
#   acc_z = read_raw_data(ACCEL_XOUT_H + 4)
# 
#   # Convert to 'g' and 'deg/s' (approx)
#   Ax = acc_x / 16384.0
#   Ay = acc_y / 16384.0
#   Az = acc_z / 16384.0
  
    temp = int(read_temp_data())

    packet.append({
    "timestamp": time.gmtime(time.time()),
    "accel_x": Ax,
    "accel_y": Ay,
    "accel_z": Az,
    "temperature": temp
    })

    print({
    "timestamp": time.gmtime(time.time()),
    "accel_x": Ax,
    "accel_y": Ay,
    "accel_z": Az,
    "temperature": temp
    })
    return packet

# packet = []
# while True:
#     for i in range(POINTS_PER_PACKET):
#         
#         sleep(1/50)
#         
#     send_packet(packet)
#     packet = []
