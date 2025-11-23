import machine
from machine import Pin, I2C, PWM
from time import sleep_ms, ticks_us, ticks_diff

class Motor:
    def __init__(self, start_freq, pin):
        # ---- PWM init ----
        print("Motor class init")
        pA = Pin(pin)
        self.pmA = machine.PWM(pA)
        print(self.pmA)
        self.pmA.duty(512)
        self.pmA.freq(start_freq)
        self.freq_last = 0
    
    def move(self, angle):
        frequency = self.get_freq(angle)
        self.pmA.duty(512)
        self.pmA.freq(frequency)
        sleep_ms(10)
        self.pmA.duty(0)
        self.pmA.freq(1)
        
    def get_freq(self, angle):
        if angle < 0:
            ratio = (angle) / 90
            freq = (ratio * 300 ) + 600
            freq = round(freq)
        elif angle > 0:
            ratio = angle / 90
            freq = (ratio * 400) + 600
            freq = round(freq)
        elif angle == 0:
            freq = 1
        if freq < 1000 and freq > 300:
            if abs(self.freq_last - freq) > 8:
                    self.freq_last = freq
        return freq
    
    
