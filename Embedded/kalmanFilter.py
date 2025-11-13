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