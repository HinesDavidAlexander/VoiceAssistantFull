import time

class Timer:
    def __init__(self, timeout):
        self.timeout = timeout
        self.start_time = time.time()

    def has_expired(self):
        return (time.time() - self.start_time) >= self.timeout

    def reset(self):
        self.start_time = time.time()
    
    def time_remaining(self):
        return self.timeout - (time.time() - self.start_time)
    
    def set_time_remaining(self, time_remaining):
        self.start_time = time.time() - (self.timeout - time_remaining)