import machine
from machine import Pin
from machine import I2C
from time import sleep_ms, sleep
from motor import Motor
    

def main():
    # init motor : Motor(start frequency, Pin number, High cutoff frequency, Low cutoff frequency)
    motor_pitch = Motor(300, 25, 550, 300)
    motor_roll = Motor(300, 26, 400, 200)
    
    # init motor start positions
    motor_roll.move(300)
    motor_pitch.move(300)
    
    while True:
        motor_roll.move(400)
        sleep(0.2)
        motor_pitch.move(500)
        sleep(0.2)
        
        motor_roll.move(250)
        sleep(0.2)
        motor_pitch.move(300)
        sleep(0.2)
        
        

if __name__ == "__main__":
    main()
