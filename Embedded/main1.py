import machine
from machine import Pin
from machine import I2C
from time import sleep
import esp32

def main():
    clk = Pin(20)
    da = Pin(22)
    i2c = I2C(1, scl=clk, sda=da, freq=40000)
    print("init\n")

if __name__ == "__main__":
    main()