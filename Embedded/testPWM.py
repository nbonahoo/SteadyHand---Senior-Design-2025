import machine
from machine import Pin
from machine import I2C
from time import sleep

global pmA1
pA1 = Pin(4)
pmA1= machine.PWM(pA1)
pmA1.duty(512)
# pmA0.freq(300)

def move(frequency):
    global pmA1
    pmA1.duty(512)
    pmA1.freq(frequency)
    sleep(0.25)
    pmA1.duty(0)
    

def main():
    for i in range(1000, 300, -50):
        print(i)
        move(i)
        
    for n in range(300, 1000, 50):
        print(n)
        move(n)
    
    # Final position
#     move(10000)
    sleep(0.5)
    move(600)

if __name__ == "__main__":
    main()
