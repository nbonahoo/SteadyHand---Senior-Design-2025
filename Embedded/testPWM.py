import machine
from machine import Pin
from machine import I2C
from time import sleep_ms, sleep

global pmA1
pA1 = Pin(26)
pmA1= machine.PWM(pA1)
pmA1.duty(512)

global pmA2
pA2 = Pin(25)
pmA2 = machine.PWM(pA2)
pmA2.duty(512)
# pmA0.freq(300)

def move(frequency):
    global pmA1
    pmA1.duty(512)
    pmA1.freq(frequency)
    sleep_ms(10)
    pmA1.duty(0)
    pmA1.freq(1)

def move2(frequency):
    global pmA2
    pmA2.duty(512)
    pmA2.freq(frequency)
    sleep_ms(10)
    pmA2.duty(0)
    pmA2.freq(1)
    

def main():
#     move2(1)
    
    for i in range(700, 300, -25):
        print(i)
        move(i)
        sleep(0.25)
        move2(i)
        sleep(0.25)
    
#     for i in range(700, 300, -50):
#         print(i)
#         move2(i)
#         sleep(0.25)
        
#     for n in range(300, 1000, 10):
#         print(n)
#         move(n)
    # Final position
#     move(200)
#     sleep(0.5)
#     move(400)
    pmA1.duty(512)
    pmA1.freq(600)


if __name__ == "__main__":
    main()
