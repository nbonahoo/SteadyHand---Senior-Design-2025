import machine

class PID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0
 
    def update(self, setpoint, process_variable):
        error = setpoint - process_variable
 
        # Proportional term
        p_term = self.kp * error
 
        # Integral term
        self.integral += error
        i_term = self.ki * self.integral
 
        # Derivative term
        d_term = self.kd * (error - self.prev_error)
 
        output = p_term + i_term + d_term
        self.prev_error = error
 
        return output
    
# # Create a PID controller instance
# kp = 1.0
# ki = 0.1
# kd = 0.01
# pid = PID(kp, ki, kd)
#  
# # Set the setpoint
# setpoint = 50
#  
# # Simulate a process variable
# process_variable = 20
#  
# # Main control loop
# while True:
#     control_output = pid.update(setpoint, process_variable)
#     print(f"Control Output: {control_output}")
#     # Here you can use the control output to adjust your system
#     # For example, if it's a temperature control, you can adjust a heater
#     # For simplicity, we just simulate a change in the process variable
#     process_variable += control_output * 0.1