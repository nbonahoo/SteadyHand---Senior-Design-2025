import machine
from machine import Pin, I2C
from time import sleep_ms, ticks_us, ticks_diff
import math
import numpy as np

# ---- MPU-6050 constants ----
MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

# -------------------- LIS3MDL setup --------------------
LIS3MDL_ADDR = 0x1C  # 0x1E is common; some modules use 0x1C, 0x1D, 0x1F
WHO_AM_I = 0x0F
CTRL_REG1 = 0x20
CTRL_REG2 = 0x21
CTRL_REG3 = 0x22
OUT_X_L = 0x28  # 6 bytes: X_L,X_H,Y_L,Y_H,Z_L,Z_H

# Sensitivity (default ranges assumed: accel ±2g, gyro ±250°/s)
ACCEL_SCALE = 16384.0   # LSB/g for ±2g
GYRO_SCALE = 131.0      # LSB/(°/s) for ±250°/s

# ---- I2C init ---- #
i2c = I2C(0, scl=Pin(20), sda=Pin(22), freq=400000)

def mpu_write(reg, data):
    i2c.writeto_mem(MPU_ADDR, reg, bytes([data]))

def mpu_read(reg, n):
    return i2c.readfrom_mem(MPU_ADDR, reg, n)

def lis_write(reg, data):
    i2c.writeto_mem(LIS3MDL_ADDR, reg, bytes([data]))

def lis_read(reg, n):
    return i2c.readfrom_mem(LIS3MDL_ADDR, reg, n)

# ---- Read Accelerometer ---- #
def mpu_write(reg, data):
    i2c.writeto_mem(MPU_ADDR, reg, bytes([data]))

def mpu_read(reg, nbytes):
    return i2c.readfrom_mem(MPU_ADDR, reg, nbytes)

def mpu_init():
    # Wake up device
    mpu_write(PWR_MGMT_1, 0x00)
    sleep_ms(100)
    # sample rate divider: set to 1 kHz / (1 + SMPLRT_DIV)
    mpu_write(SMPLRT_DIV, 0x07)  # sample rate ~125 Hz (if DLPF=0)
    # DLPF config
    mpu_write(CONFIG, 0x01)      # DLPF ~184Hz accel, 188Hz gyro (tweak if needed)
    # gyro full scale ±250°/s
    mpu_write(GYRO_CONFIG, 0x00)
    # accel full scale ±2g
    mpu_write(ACCEL_CONFIG, 0x00)
    sleep_ms(50)

def read_raw16(addr):
    b = mpu_read(addr, 2)
    hi = b[0]
    lo = b[1]
    val = (hi << 8) | lo
    if val & 0x8000:
        val = -((65535 - val) + 1)
    return val

def read_accel():
    ax = read_raw16(ACCEL_XOUT_H)
    ay = read_raw16(ACCEL_XOUT_H + 2)
    az = read_raw16(ACCEL_XOUT_H + 4)
    # convert to physical units
    ax_g = ax / ACCEL_SCALE
    ay_g = ay / ACCEL_SCALE
    az_g = az / ACCEL_SCALE
    return np.array([ax_g, ay_g, az_g])

def read_gyro():
    gx = read_raw16(GYRO_XOUT_H)
    gy = read_raw16(GYRO_XOUT_H + 2)
    gz = read_raw16(GYRO_XOUT_H + 4)
    # convert to physical units
    gx_dps = gx / GYRO_SCALE
    gy_dps = gy / GYRO_SCALE
    gz_dps = gz / GYRO_SCALE
    return np.array([gx_dps, gy_dps, gz_dps])

# -------------------- LIS3MDL functions --------------------
def lis3mdl_init():
    who = lis_read(WHO_AM_I, 1)[0]
    if who != 0x3D:
        print("Warning: LIS3MDL WHO_AM_I not 0x3D (got 0x{:02X})".format(who))
    # Configure for 80 Hz, ultra-high-performance XY and Z, continuous mode
    lis_write(CTRL_REG1, 0b11111100)  # Temp disable, 80Hz, high-perf XY
    lis_write(CTRL_REG2, 0b00000000)  # +/-4 gauss
    lis_write(CTRL_REG3, 0b00000000)  # continuous-conversion mode
    sleep_ms(50)

def read_magnetometer():
    data = lis_read(OUT_X_L | 0x80, 6)  # auto-increment
    x = (data[1] << 8) | data[0]
    y = (data[3] << 8) | data[2]
    z = (data[5] << 8) | data[4]
    
    for v in (x, y, z):
        if v & 0x8000:
            v -= 65536
    # Convert to microtesla (±4 gauss = ±400 µT range => 6842 LSB/gauss)
    # 1 gauss = 100 µT
    x = x % 10000
    y = y % 10000
    z = z % 10000
    print("x: ", x)
    print("y: ", y)
    print("z: ", z)
    SCALE = 6842.0 / 100.0
    return np.array([x / SCALE, y / SCALE, z / SCALE])

# ---- Simple Kalman filter for angle (angle + bias) ----
class KalmanAngle:
    def __init__(self, Q_angle=0.001, Q_bias=0.003, R_measure=0.03):
        # Process noise variances
        self.Q_angle = Q_angle
        self.Q_bias = Q_bias
        
        # Measurement noise variance
        self.R_measure = R_measure

        # state
        self.angle = 0.0
        self.bias = 0.0

        # error covariance matrix P (2x2)
        self.P = [[0.0, 0.0],
                  [0.0, 0.0]]

    def set_angle(self, angle):
        self.angle = angle

    def get_angle(self, newRate, newAngle, dt):
        # Predict
        # Rate minus bias
        rate = newRate - self.bias
        self.angle += dt * rate

        # Update covariance matrix P
        # P = A * P * A^T + Q
        # For our simple model:
        
        self.P[0][0] += dt * (dt*self.P[1][1] - self.P[0][1] - self.P[1][0] + self.Q_angle)
        self.P[0][1] -= dt * self.P[1][1]
        self.P[1][0] -= dt * self.P[1][1]
        self.P[1][1] += self.Q_bias * dt

        # Innovation
        y = newAngle - self.angle

        # Innovation covariance S
        S = self.P[0][0] + self.R_measure

        # Kalman gain K = P * H^T * S^-1
        K0 = self.P[0][0] / S
        K1 = self.P[1][0] / S

        # Update state
        self.angle += K0 * y
        self.bias += K1 * y

        # Update covariance P = (I - K*H) * P
        P00_temp = self.P[0][0]
        P01_temp = self.P[0][1]

        self.P[0][0] -= K0 * P00_temp
        self.P[0][1] -= K0 * P01_temp
        self.P[1][0] -= K1 * P00_temp
        self.P[1][1] -= K1 * P01_temp

        return self.angle

# ---- Utility: accel -> angles (degrees) ----
def wrap_angle(angle):
    while angle < 0:
        angle += 360
    while angle >= 360:
        angle -= 360
    return angle

def normalize_mag(mx, my, mz):
    mag_norm = math.sqrt(mx*mx + my*my + mz*mz)
    if mag_norm == 0:
        return mx, my, mz
    return mx / mag_norm, my / mag_norm, mz / mag_norm

def accel_to_pitch_roll(ax, ay, az):
    # pitch: rotation around X-axis: atan2(-ax, sqrt(ay^2 + az^2))
    # roll:  rotation around Y-axis: atan2(ay, az)
    # Use conventions: pitch positive when nose up
    
    pitch = math.degrees(math.atan2(-ax, math.sqrt(ay*ay + az*az)))
    roll = math.degrees(math.atan2(ay, az))
    return pitch, roll

def tilt_compensated_yaw(mx, my, mz, pitch, roll):
    # Convert degrees to radians
    pitch_rad = math.radians(pitch)
    roll_rad = math.radians(roll)
    # Apply tilt compensation
    mx, my, mz = normalize_mag(mx, my, mz)
    Xh = mx * math.cos(pitch_rad) + mz * math.sin(pitch_rad)
    print("Xh: ", Xh)
    Yh = mx * math.sin(roll_rad) * math.sin(pitch_rad) + my * math.cos(roll_rad) - mz * math.sin(roll_rad) * math.cos(pitch_rad)
    print("Yh: ", Yh)
    yaw = math.degrees(math.atan2(Yh, Xh))
#     yaw = math.degrees(math.atan2(my, mx))
    yaw = wrap_angle(yaw)
    print("yaw: ", yaw)
    if yaw < 0:
        yaw += 360
    return yaw

# ---- Gyro bias calibration ----
def calibrate_gyro(samples=200, delay_ms=5):
    print("Calibrating gyro bias: keep board still...")
    gx_sum = gy_sum = gz_sum = 0.0
    for i in range(samples):
        ax, ay, az, gx, gy, gz = read_accel_gyro()
        gx_sum += gx
        gy_sum += gy
        gz_sum += gz
        sleep_ms(delay_ms)
    gx_bias = gx_sum / samples
    gy_bias = gy_sum / samples
    gz_bias = gz_sum / samples
    print("Calib done. gx_bias={:.4f} gy_bias={:.4f} gz_bias={:.4f}".format(gx_bias, gy_bias, gz_bias))
    return gx_bias, gy_bias, gz_bias

# ---- Main ----
def main():
    try:
        mpu_init()
        lis3mdl_init()
    except Exception as e:
        print("MPU init failed:", e)
        return

    # warm up read
    sleep_ms(100)
    
    # calibrate gyro biases (in dps)
    gx_bias, gy_bias, gz_bias = calibrate_gyro(samples=300, delay_ms=5)

    # Create Kalman filters for pitch and roll
    # Tweak Q and R to taste: smaller R -> trusts accelerometer more (less smoothing),
    # larger Q_bias -> allows bias to vary more quickly, etc.
    kalman_pitch = KalmanAngle(Q_angle=0.001, Q_bias=0.003, R_measure=0.03)
    kalman_roll  = KalmanAngle(Q_angle=0.001, Q_bias=0.003, R_measure=0.03)
#     kalman_yaw = KalmanAngle(Q_angle=0.001, Q_bias=0.003, R_measure=0.03)
    
    # Initialize angles from accel and magno for a stable starting point
    ax, ay, az, gx, gy, gz = read_accel_gyro()
    mx, my, mz = read_magnetometer()
    
    pitch, roll = accel_to_pitch_roll(ax, ay, az)
    yaw = tilt_compensated_yaw(mx, my, mz, pitch, roll)

    kalman_pitch.set_angle(pitch)
    kalman_roll.set_angle(roll)
#     kalman_yaw.set_angle(yaw)
    
    last_time = ticks_us()
    print("Starting filter loop. Ctrl+C to stop.")
    while True:
        now = ticks_us()
        dt = ticks_diff(now, last_time) / 1_000_000.0  # seconds
        if dt <= 0:
            dt = 0.001
        last_time = now

        ax, ay, az, gx_raw, gy_raw, gz_raw = read_accel_gyro()
        mx, my, mz = read_magnetometer()
    
        # subtract calibration biases from gyro readings
        gx = gx_raw - gx_bias
        gy = gy_raw - gy_bias
        gz = gz_raw - gz_bias

        # compute accelerometer and magnometer angles
        a_roll, a_pitch = accel_to_pitch_roll(ax, ay, az)
        yaw = tilt_compensated_yaw(mx, my, mz, pitch, roll)
        
        # feed gyro rates (dps) and accel angle (deg) into kalman filters
        pitch_angle = -1 * kalman_pitch.get_angle(gx, a_pitch, dt)
        roll_angle  = kalman_roll.get_angle(gy, a_roll, dt)
#         yaw_angle = kalman_yaw.get_angle(gz, yaw, dt)
        

        # placeholder
        yaw_angle = yaw
        print("Pitch Angle:{:+06.2f} | Roll Angle:{:+06.2f} | Yaw Angle:{:+06.2f}".format(pitch_angle, roll_angle, yaw_angle))
        # adjust sleep to control update rate; loop timing dominated by i2c read
        sleep_ms(15)

if __name__ == "__main__":
    main()
