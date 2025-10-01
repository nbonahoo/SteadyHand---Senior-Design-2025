from machine import Pin
from time import sleep
from neopixel import NeoPixel

neopixel_pwr = Pin(2, Pin.OUT)
neopixel_pwr.value(1)
def switchpress():
    button = Pin(38, Pin.IN)
    neo = Pin(0, Pin.OUT)
    np = NeoPixel(neo, 8)
    
    current_state = 1
    last_state = 0
    
    num_press = 0
    while num_press < 5 or current_state == 0:
        current_state = button.value()
        if current_state != last_state: # if change in button state, run loop
            if current_state == 1: # Button if OFF
                # set neo to RED
                np[0] = (0, 0, 255)
                np.write()
            elif current_state == 0:
                # set neo to GREEN
                np[0] = (248, 24, 148)
                np.write()   
                num_press += 1
            last_state = current_state
    # Turn OFF Neopixel
    np[0] = (0, 0, 0)
    np.write()
    print("You have successfully implemented LAB1!")
