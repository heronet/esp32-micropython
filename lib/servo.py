from machine import Pin, PWM
from time import sleep

class Servo:
    def __init__(self, pin, min_duty=40, max_duty=115, freq=50):
        """
        Initialize the servo motor.
        
        :param pin: GPIO pin number (e.g., 13).
        :param min_duty: Minimum duty cycle for 0 degrees (default: 40).
        :param max_duty: Maximum duty cycle for 180 degrees (default: 115).
        :param freq: PWM frequency (default: 50Hz).
        """
        self.pwm = PWM(Pin(pin), freq=freq)
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.current_angle = 0  # Track the current angle

    def set_angle(self, angle):
        """
        Set the servo to a specific angle.
        
        :param angle: Desired angle (0 to 180 degrees).
        """
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180
        
        # Map the angle to a duty cycle value
        duty = int(self.min_duty + (angle / 180) * (self.max_duty - self.min_duty))
        self.pwm.duty(duty)
        self.current_angle = angle  # Update the current angle
        sleep(0.1)  # Allow time for the servo to move

    def get_angle(self):
        """
        Get the current angle of the servo.
        
        :return: Current angle (0 to 180 degrees).
        """
        return self.current_angle

    def deinit(self):
        """
        Deinitialize the PWM pin to release the servo.
        """
        self.pwm.deinit()
