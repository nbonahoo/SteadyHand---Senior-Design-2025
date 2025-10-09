import machine
from machine import Pin
from machine import I2C
from time import sleep

from machine import Pin, I2C
from time import sleep

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

def read_raw_data(addr):
    high, low = i2c.readfrom_mem(MPU6050_ADDR, addr, 2)
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value

def move_motor():
    pA0 = Pin(26)
    pmA0 = machine.PWM(pA0)
    pmA0.freq(500)
while True:
    # Read accelerometer data
    acc_x = read_raw_data(ACCEL_XOUT_H)
    acc_y = read_raw_data(ACCEL_XOUT_H + 2)
    acc_z = read_raw_data(ACCEL_XOUT_H + 4)

    # Read gyroscope data
    gyro_x = read_raw_data(GYRO_XOUT_H)
    gyro_y = read_raw_data(GYRO_XOUT_H + 2)
    gyro_z = read_raw_data(GYRO_XOUT_H + 4)

    # Convert to 'g' and 'deg/s' (approx)
    Ax = acc_x / 16384.0
    Ay = acc_y / 16384.0
    Az = acc_z / 16384.0

    Gx = gyro_x / 131.0
    Gy = gyro_y / 131.0
    Gz = gyro_z / 131.0

    print("Accel (g): X={:.2f}, Y={:.2f}, Z={:.2f}".format(Ax, Ay, Az))
    print("Gyro (deg/s): X={:.2f}, Y={:.2f}, Z={:.2f}".format(Gx, Gy, Gz))
    print("------")
    sleep(0.5)
    
# FULL_DUTY_CYCLE = 1023
# 
# pA0 = Pin(26)
# pA1 = Pin(25)
# p33 = Pin(33)
# pmA0 = machine.PWM(pA0)
# pmA1 = machine.PWM(pA1)
# pm33 = machine.PWM(p33)
# pmA0.freq(40)
# pmA1.freq(1000)
# pm33.freq(750)
# pmA0.duty(512)
# print("Outputting PWM Wave")
# while True:
#     pass
# pmA1.duty(300)
# pm33.duty(300)
# 
# sleep(2)
# 
# pmA0.duty(500)
# pmA1.duty(512)
# pm33.duty(512)
# 
# sleep(2)
# 
# pmA0.duty(300)
# pmA1.duty(300)
# pm33.duty(300)
# 
# sleep(2)
# 
# pmA0.duty(500)
# pmA1.duty(512)
# pm33.duty(512)
# 
# print("I like to move it move it!")
