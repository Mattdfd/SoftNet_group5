import numpy as np
import math
import random
import datetime
class DataGenerator():
    
    def __init__(self, base = 0, climb = 0, random_base = 0, random_sigma = 0, minute_sin_amplitude = 0, hour_sin_amplitude = 0) -> None:
        self.base = base
        self.climb = climb
        self.random_base = random_base
        self.random_sigma = random_sigma
        self.minute_sin_amplitude = minute_sin_amplitude
        self.hour_sin_amplitude = hour_sin_amplitude
        
    def generate_value(self) -> int:
        r1 = random.randint(1, 50)
        r2 = random.randint(1, 50)
        if r1 == r2:
            value = 7

            return value
        else:
            newValue = 0
            t = int(datetime.datetime.now().timestamp())

            sin_minute_cycle_value = self.minute_sin_amplitude * math.sin(((2 * math.pi)/(60) * t))
            random_value = random.gauss(self.random_base, self.random_sigma)

            newValue = random_value + self.base + sin_minute_cycle_value
        
            self.base = self.base + self.climb
            return newValue