import machine
from machine import Pin
from machine import I2C
from time import sleep

global pmA0
pA0 = Pin(26)
pmA0= machine.PWM(pA0)
pmA0.duty(520)
pmA0.freq(600)

def move(frequency):
    global pmA0
    pmA0.duty(520)
    pmA0.freq(frequency)
    sleep(0.5)
    pmA0.duty(0)
    

def main():
    for i in range(600, 199, -50):
        print(i)
        move(i)
        
    for n in range(200, 601, 50):
        print(n)
        move(n)
        
    # Final position
    move(300)

if __name__ == "__main__":
    main()
