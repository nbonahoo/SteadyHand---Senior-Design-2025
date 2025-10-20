import machine
from machine import Pin
from machine import I2C
from time import sleep

global pmA1
pA1 = Pin(25)
pmA1= machine.PWM(pA1)
pmA1.duty(512)
# pmA0.freq(300)

def move(frequency):
    global pmA1
    pmA1.duty(512)
    pmA1.freq(frequency)
    sleep(0.5)
    pmA1.duty(0)
    

def main():
    for i in range(1000, 299, -100):
        print(i)
        move(i)
        
    for n in range(300, 1001, 100):
        print(n)
        move(n)
    
    # Final position
    move(600)

if __name__ == "__main__":
    main()
