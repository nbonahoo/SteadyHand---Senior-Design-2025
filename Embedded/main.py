import machine
from machine import Pin
from time import sleep
import esp32

FULL_DUTY_CYCLE = 1023

pA0 = Pin(26)
pA1 = Pin(25)
p33 = Pin(33)
pmA0 = machine.PWM(pA0)
pmA1 = machine.PWM(pA1)
pm33 = machine.PWM(p33)
pmA0.freq(500)
pmA1.freq(1000)
pm33.freq(750)
pmA0.duty(300)
pmA1.duty(300)
pm33.duty(300)

sleep(2)

pmA0.duty(500)
pmA1.duty(512)
pm33.duty(512)

sleep(2)

pmA0.duty(300)
pmA1.duty(300)
pm33.duty(300)

sleep(2)

pmA0.duty(500)
pmA1.duty(512)
pm33.duty(512)

print("I like to move it move it!")

