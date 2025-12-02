import machine
from machine import Pin, I2C, PWM
from time import sleep_ms, ticks_us, ticks_diff

class Motor:
    def __init__(self, start_freq, pin, high, low):
        # ---- PWM init ----
        print("Motor class init")
        pA = Pin(pin)
        self.pmA = machine.PWM(pA)
        print(self.pmA)
        self.pmA.duty(512)
        self.pmA.freq(start_freq)
        self.freq_last = 0
        self.cutoff_high = high
        self.cutoff_low = low
        self.cutoff_diff = high - low
    
    def move(self, angle):
        frequency = self.get_freq(angle)
        self.pmA.duty(512)
        self.pmA.freq(frequency)
        sleep_ms(10)
        self.pmA.duty(0)
        self.pmA.freq(1)
        
    def get_freq(self, angle):
        if (angle < -30) or (angle > 30):
            return 1 # return no movement if the angle is too high
        
        angle = angle + 30 # make all angles positive (-30 to 30) now (0 to 60)
        print("adj angle: ", angle)
        ratio = (angle) / 60
        freq = (ratio * self.cutoff_diff ) + self.cutoff_low
        freq = round(freq)
        if abs(self.freq_last - freq) > 10: # Only move motor is frequency has increase by at least ###
            self.freq_last = freq
            return freq
        else:
            return 1
        
        
        
#         # Old logic
#         if angle < 0:
#             ratio = (angle) / 90
#             freq = (ratio * 300 ) + 600
#             freq = round(freq)
#         elif angle > 0:
#             ratio = angle / 90
#             freq = (ratio * 400) + 600
#             freq = round(freq)
#         elif angle == 0:
#             freq = 1
#         if freq < 1000 and freq > 300:
#             if abs(self.freq_last - freq) > 8:
#                     self.freq_last = freq
#         return freq
    
    
