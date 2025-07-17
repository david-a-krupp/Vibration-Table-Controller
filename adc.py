import numpy as np
import time
import random

def read_acceleration():
    return np.sin(2 * np.pi * 2 * time.time()) + random.uniform(-0.05, 0.05)