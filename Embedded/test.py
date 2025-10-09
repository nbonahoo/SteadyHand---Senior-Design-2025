# ESP32 (Feather V2) + MPU-6050 + Kalman filter (MicroPython)
# Estimates pitch and roll using a 2-state Kalman filter per axis (angle, gyro bias).
# Wiring:
#   MPU-6050 VCC -> 3.3V (or module VCC if it accepts 3.3V)
#   GND -> GND
#   SDA -> ESP32 SDA (GPIO21)
#   SCL -> ESP32 SCL (GPIO22)
# Note: many breakout boards include pull-ups. If not, add 4.7k pull-ups on SDA/SCL.

from machine import Pin, I2C
from time import sleep_ms, ticks_us, ticks_diff
import math

# ---- MPU-6050 constants ----
MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

# Sensitivity (default ranges assumed: accel ±2g, gyro ±250°/s)
ACCEL_SCALE = 16384.0   # LSB/g for ±2g
GYRO_SCALE = 131.0      # LSB/(°/s) for ±250°/s

# ---- I2C init (adjust pins if needed) ----
i2c = I2C(0, scl=Pin(20), sda=Pin(22), freq=400000)

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

def read_accel_gyro():
    ax = read_raw16(ACCEL_XOUT_H)
    ay = read_raw16(ACCEL_XOUT_H + 2)
    az = read_raw16(ACCEL_XOUT_H + 4)
    gx = read_raw16(GYRO_XOUT_H)
    gy = read_raw16(GYRO_XOUT_H + 2)
    gz = read_raw16(GYRO_XOUT_H + 4)
    # convert to physical units
    ax_g = ax / ACCEL_SCALE
    ay_g = ay / ACCEL_SCALE
    az_g = az / ACCEL_SCALE
    gx_dps = gx / GYRO_SCALE
    gy_dps = gy / GYRO_SCALE
    gz_dps = gz / GYRO_SCALE
    return (ax_g, ay_g, az_g, gx_dps, gy_dps, gz_dps)

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
def accel_to_pitch_roll(ax, ay, az):
    # pitch: rotation around X-axis: atan2(-ax, sqrt(ay^2 + az^2))
    # roll:  rotation around Y-axis: atan2(ay, az)
    # Use conventions: pitch positive when nose up
    pitch = math.degrees(math.atan2(-ax, math.sqrt(ay*ay + az*az)))
    roll = math.degrees(math.atan2(ay, az))
    return pitch, roll

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

    # Initialize angles from accel for a stable starting point
    ax, ay, az, gx, gy, gz = read_accel_gyro()
    pitch, roll = accel_to_pitch_roll(ax, ay, az)
    kalman_pitch.set_angle(pitch)
    kalman_roll.set_angle(roll)

    last_time = ticks_us()

    print("Starting filter loop. Ctrl+C to stop.")
    while True:
        now = ticks_us()
        dt = ticks_diff(now, last_time) / 1_000_000.0  # seconds
        if dt <= 0:
            dt = 0.001
        last_time = now

        ax, ay, az, gx_raw, gy_raw, gz_raw = read_accel_gyro()

        # subtract calibration biases from gyro readings
        gx = gx_raw - gx_bias
        gy = gy_raw - gy_bias
        gz = gz_raw - gz_bias

        # compute accelerometer angles
        a_pitch, a_roll = accel_to_pitch_roll(ax, ay, az)

        # note: depending on mounting/orientation, you may need to swap signs or axes
        # feed gyro rates (dps) and accel angle (deg) into kalman filters
        filt_pitch = kalman_pitch.get_angle(gx, a_pitch, dt)
        filt_roll  = kalman_roll.get_angle(gy, a_roll, dt)

        # optional: complementary fallback if kalman diverges (not usually necessary)
        # comp_pitch = 0.98*(prev_comp_pitch + gx*dt) + 0.02*a_pitch

        print("Pitch: accel={:+06.2f} filt={:+06.2f} | Roll: accel={:+06.2f} filt={:+06.2f}".format(
            a_pitch, filt_pitch, a_roll, filt_roll))
        # adjust sleep to control update rate; loop timing dominated by i2c read
        sleep_ms(20)

if __name__ == "__main__":
    main()
