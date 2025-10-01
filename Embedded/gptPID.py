# stabilizer.py
# MicroPython utensil stabilizer prototype
# - IMU: MPU6050 (I2C)
# - Tremor detection: Goertzel bank (2-12 Hz)
# - Controller: PID (position) + feedforward sinusoid from dominant component
# - Actuators: PWM (servos or motor drivers)
#
# Note: This is a prototype. Tune gains & safety limits for your device and test carefully.

import machine
import time
import math
from array import array

# --------------------------
# Hardware configuration
# --------------------------
I2C_SCL_PIN = 22
I2C_SDA_PIN = 21
MPU6050_I2C_ADDR = 0x68

# PWM pins for two axes (adjust)
PWM_X_PIN = 14
PWM_Y_PIN = 27

# PWM frequency for servos (Hz)
PWM_FREQ = 200  # servo: typically 50-400 Hz depending on actuator; set appropriate

# If using hobby servos, map angle -> duty accordingly:
SERVO_MIN_DUTY = 40   # change to match your board and servo (0..1023 or 0..65535 depending)
SERVO_MAX_DUTY = 115  # example for ESP32 10-bit duty; tune for your board

# --------------------------
# Control parameters
# --------------------------
SAMPLE_RATE_HZ = 200           # sensor + control loop
SAMPLE_PERIOD = 1.0 / SAMPLE_RATE_HZ

# Tremor band & Goertzel resolution
FREQ_MIN = 2.0
FREQ_MAX = 12.0
FREQ_STEP = 0.5                # step of tested frequency (0.5 Hz gives many bins)
GOERTZEL_M = 200               # number of samples for internal averaging; choose such that M/SR ~ 0.5-1s
                               # using larger M gives better frequency resolution but more smoothing
# We will compute Goertzel every sample with moving-window approach (simple implementation below).

# Feedforward scale: how much of estimated sinusoid to feed to actuator (0..1)
FEEDFORWARD_GAIN = 1.0

# PID gains (position-domain). Start small and tune. Example starting guesses:
PID_KP = 12.0
PID_KI = 0.0
PID_KD = 0.6

# actuator (angle) limits (radians)
ACT_ANGLE_LIMIT = 0.35  # around +/-20 degrees safe start

# Safety thresholds
MAX_INTENTIONAL_ANG_VEL = 1.5  # rad/s - if above this, assume intentional motion and reduce stabilization

# --------------------------
# Utilities: I2C + MPU6050 driver (very small)
# --------------------------
class MPU6050:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        # wake up device
        try:
            self.i2c.writeto_mem(self.addr, 0x6B, bytes([0]))  # PWR_MGMT_1 = 0
        except Exception as e:
            raise RuntimeError("MPU6050 I2C error: %s" % e)

    def read_raw(self):
        # read 14 bytes starting at ACCEL_XOUT_H
        d = self.i2c.readfrom_mem(self.addr, 0x3B, 14)
        ax = self._conv(d[0], d[1])
        ay = self._conv(d[2], d[3])
        az = self._conv(d[4], d[5])
        temp = self._conv(d[6], d[7])
        gx = self._conv(d[8], d[9])
        gy = self._conv(d[10], d[11])
        gz = self._conv(d[12], d[13])
        return (ax, ay, az, temp, gx, gy, gz)

    @staticmethod
    def _conv(h, l):
        v = (h << 8) | l
        if v & 0x8000:
            v = -((v ^ 0xFFFF) + 1)
        return v

    def read_gyro_rads(self, scale_g=131.0):
        # returns angular velocity in rad/s for x,y,z using default gyro scale of 131 LSB/(deg/s)
        _, _, _, _, gx, gy, gz = self.read_raw()
        # convert deg/s -> rad/s; MPU default 131 LSB/(deg/s) (for ±250°/s)
        gx_dps = gx / scale_g
        gy_dps = gy / scale_g
        gz_dps = gz / scale_g
        rad = math.pi / 180.0
        return (gx_dps * rad, gy_dps * rad, gz_dps * rad)

# --------------------------
# PID controller
# --------------------------
class PID:
    def __init__(self, kp, ki, kd, dt, out_min=-1.0, out_max=1.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt
        self.out_min = out_min
        self.out_max = out_max
        self.integral = 0.0
        self.prev_err = 0.0

    def update(self, error):
        self.integral += error * self.dt
        deriv = (error - self.prev_err) / self.dt
        out = self.kp * error + self.ki * self.integral + self.kd * deriv
        self.prev_err = error
        # clamp
        if out > self.out_max:
            out = self.out_max
        elif out < self.out_min:
            out = self.out_min
        return out

# --------------------------
# Goertzel implementation for a dynamic bank of frequencies
# --------------------------
class GoertzelBank:
    def __init__(self, sample_rate, freqs, N):
        """
        sample_rate: Hz
        freqs: list of frequencies to track (Hz)
        N: number of samples over which to accumulate (window)
        """
        self.fs = sample_rate
        self.freqs = freqs
        self.N = N
        self.coeffs = []
        self.reset_states()
        for f in freqs:
            k = int(0.5 + (N * f) / sample_rate)
            omega = (2.0 * math.pi * k) / N
            coeff = 2.0 * math.cos(omega)
            self.coeffs.append((k, coeff, omega))

    def reset_states(self):
        # states per frequency: s_prev, s_prev2, sample_count
        self.states = [[0.0, 0.0, 0] for _ in self.freqs]

    def add_sample(self, x):
        """
        Feed one sample (float) into the bank. Returns None or dictionary of results when a freq window completes.
        We compute magnitude & phase when a window of N samples is reached (per bin).
        """
        results = []
        for i, (k, coeff, omega) in enumerate(self.coeffs):
            s_prev, s_prev2, cnt = self.states[i]
            s = x + coeff * s_prev - s_prev2
            self.states[i][1] = s_prev   # new s_prev2
            self.states[i][0] = s        # new s_prev
            cnt += 1
            self.states[i][2] = cnt
            if cnt >= self.N:
                # compute complex result:
                real = s_prev - s_prev2 * math.cos(omega)
                imag = s_prev2 * math.sin(omega)
                mag = math.sqrt(real * real + imag * imag) / self.N
                phase = math.atan2(imag, real)
                results.append((self.freqs[i], mag, phase))
                # reset for next window:
                self.states[i][0] = 0.0
                self.states[i][1] = 0.0
                self.states[i][2] = 0
        return results if results else None

# --------------------------
# Actuator wrapper (servo-like)
# --------------------------
class Actuator:
    def __init__(self, pin_no, pwm_freq=PWM_FREQ):
        self.pin = machine.Pin(pin_no)
        self.pwm = machine.PWM(self.pin)
        try:
            self.pwm.freq(pwm_freq)
        except:
            pass
        # duty range and angle mapping will be handled in set_angle
        self.angle = 0.0

    def set_angle(self, angle_rad):
        # clamp
        if angle_rad > ACT_ANGLE_LIMIT:
            angle_rad = ACT_ANGLE_LIMIT
        elif angle_rad < -ACT_ANGLE_LIMIT:
            angle_rad = -ACT_ANGLE_LIMIT
        self.angle = angle_rad
        # map -limit..+limit -> SERVO_MIN_DUTY..SERVO_MAX_DUTY
        t = (angle_rad + ACT_ANGLE_LIMIT) / (2.0 * ACT_ANGLE_LIMIT)
        duty = int(SERVO_MIN_DUTY + t * (SERVO_MAX_DUTY - SERVO_MIN_DUTY))
        # set duty - adapt to board PWM resolution
        try:
            self.pwm.duty(duty)
        except AttributeError:
            # some ports have duty_u16
            try:
                self.pwm.duty_u16(int(duty * 65535 / 1023))
            except:
                pass

# --------------------------
# Main stabilizer
# --------------------------
class Stabilizer:
    def __init__(self):
        # I2C + IMU
        i2c = machine.I2C(0, scl=machine.Pin(I2C_SCL_PIN), sda=machine.Pin(I2C_SDA_PIN), freq=400000)
        self.imu = MPU6050(i2c, MPU6050_I2C_ADDR)

        # Actuators
        self.act_x = Actuator(PWM_X_PIN)
        self.act_y = Actuator(PWM_Y_PIN)

        # PID controllers for each axis (we control angle to zero)
        self.pid_x = PID(PID_KP, PID_KI, PID_KD, SAMPLE_PERIOD, out_min=-ACT_ANGLE_LIMIT, out_max=ACT_ANGLE_LIMIT)
        self.pid_y = PID(PID_KP, PID_KI, PID_KD, SAMPLE_PERIOD, out_min=-ACT_ANGLE_LIMIT, out_max=ACT_ANGLE_LIMIT)

        # Tremor detection bank (for X and Y separately)
        freqs = []
        f = FREQ_MIN
        while f <= FREQ_MAX + 1e-9:
            freqs.append(round(f, 3))
            f += FREQ_STEP
        self.goertzel_x = GoertzelBank(SAMPLE_RATE_HZ, freqs, GOERTZEL_M)
        self.goertzel_y = GoertzelBank(SAMPLE_RATE_HZ, freqs, GOERTZEL_M)

        # keep last gyro values for integration (angle estimate)
        self.ang_x = 0.0
        self.ang_y = 0.0

        # dominant component cache
        self.dom_x = (0.0, 0.0, 0.0)  # (freq, mag, phase)
        self.dom_y = (0.0, 0.0, 0.0)

        # time tracking
        self.t0 = time.ticks_ms()
        self.sample_count = 0

    def run_once(self):
        # read gyro (rad/s)
        gx, gy, gz = self.imu.read_gyro_rads()
        # integrate angular velocity to approximate angle (simple integrator)
        self.ang_x += gx * SAMPLE_PERIOD
        self.ang_y += gy * SAMPLE_PERIOD

        # run goertzel bank on angular velocity (bandpass-ish effect): tremor appears in gyro signal
        res_x = self.goertzel_x.add_sample(gx)
        res_y = self.goertzel_y.add_sample(gy)

        # update dominant estimates if results returned
        if res_x:
            # choose largest magnitude component
            best = max(res_x, key=lambda r: r[1])
            # small smoothing on amplitude/phase could be added - here we directly store
            self.dom_x = best  # (freq, mag, phase)
        if res_y:
            best = max(res_y, key=lambda r: r[1])
            self.dom_y = best

        # detect intentional motion: if absolute angular velocity too large, reduce feedforward/pid aggressiveness
        intent_factor = 1.0
        if abs(gx) > MAX_INTENTIONAL_ANG_VEL or abs(gy) > MAX_INTENTIONAL_ANG_VEL:
            intent_factor = 0.25  # be conservative during large intentional motions

        # PID targets: we aim for zero angle (stabilize to keep utensil steady)
        err_x = -self.ang_x
        err_y = -self.ang_y
        pid_out_x = self.pid_x.update(err_x) * intent_factor
        pid_out_y = self.pid_y.update(err_y) * intent_factor

        # Feedforward synthesis from dominant component
        now_ms = time.ticks_ms() - self.t0
        now_t = now_ms / 1000.0

        ff_x = 0.0
        f_freq, f_mag, f_phase = self.dom_x
        if f_mag > 1e-5 and f_freq > 0.0:
            # amplitude in rad/s maybe; we synthesize angle offset as integral of velocity sinusoid
            # If gyro shows tremor in rad/s: v = A*sin(2π f t + phi)
            # angle contribution ~ -A/(2π f) * cos(2π f t + phi)  (since integral of sin is -cos/(2π f))
            ff_x = - FEEDFORWARD_GAIN * (f_mag / (2.0 * math.pi * f_freq)) * math.cos(2.0 * math.pi * f_freq * now_t + f_phase)

        ff_y = 0.0
        f_freq, f_mag, f_phase = self.dom_y
        if f_mag > 1e-5 and f_freq > 0.0:
            ff_y = - FEEDFORWARD_GAIN * (f_mag / (2.0 * math.pi * f_freq)) * math.cos(2.0 * math.pi * f_freq * now_t + f_phase)

        # final actuator command = pid + feedforward
        cmd_x = pid_out_x + ff_x
        cmd_y = pid_out_y + ff_y

        # clamp to safe angle range
        if cmd_x > ACT_ANGLE_LIMIT:
            cmd_x = ACT_ANGLE_LIMIT
        elif cmd_x < -ACT_ANGLE_LIMIT:
            cmd_x = -ACT_ANGLE_LIMIT
        if cmd_y > ACT_ANGLE_LIMIT:
            cmd_y = ACT_ANGLE_LIMIT
        elif cmd_y < -ACT_ANGLE_LIMIT:
            cmd_y = -ACT_ANGLE_LIMIT

        # send to actuators
        self.act_x.set_angle(cmd_x)
        self.act_y.set_angle(cmd_y)

        self.sample_count += 1

    def loop(self):
        print("Stabilizer started. Sample rate = %d Hz, goertzel window=%d samples" % (SAMPLE_RATE_HZ, GOERTZEL_M))
        next_t = time.ticks_ms()
        while True:
            start = time.ticks_ms()
            self.run_once()
            # sleep to maintain SAMPLE_RATE_HZ
            next_t = time.ticks_add(next_t, int(SAMPLE_PERIOD * 1000))
            now = time.ticks_ms()
            delay = time.ticks_diff(next_t, now)
            if delay > 0:
                time.sleep_ms(delay)
            else:
                # overrun; adjust next_t and continue (consider lowering SAMPLE_RATE_HZ or reduce work)
                next_t = now

# --------------------------
# Entrypoint
# --------------------------
def main():
    s = Stabilizer()
    try:
        s.loop()
    except KeyboardInterrupt:
        print("Stopped by user")

if __name__ == "__main__":
    main()
