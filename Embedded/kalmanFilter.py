import machine
from machine import Pin
from machine import I2C
from time import sleep

from machine import Pin, I2C
from time import sleep

class KalmanFilter():
    def __init__(self, F, B, H, Q, R, x0, P0):
        self.F = F          # State transition matrix
        self.B = B          # Control Matrix
        self.H = H          # Observation Matrix
        self.Q = Q          # Process Noise Covariance
        self.R = R          # Measurement Noise Covariance
        self.x = x0         # Initial State Estimate
        self.P = P0         # Initial Error Covariance
        
