from scipy.stats import circmean
import numpy as np

class Pulse:
    def __init__(self, sender, ago):
        # The sender usually sends the pulse a few millis after it actually pulsed
        # This field specifies how old the pulse was when it was send
        self.ago = ago
        # Unique name of the sender
        self.sender = sender

# Does not work in the current implementation
# Should attempt to only synchronize the phase and assume that all fireflies want to blink at the same frequency
class Firefly:
    # These values will be set by the main loop
    name = ""
    preferred_pulse_length = 0
    send_pulse = None
    pulse_progress = 0
    dampening = 0.5

    # Value from 0 to 255. Will be read by the main loop
    brightness = 0

    time = 0
    received_pulses = []
    current_pulse_length = None

    def __init__(self):
        self.speed = 1.0
    
    def tick(self, delta):
        if self.current_pulse_length == None or self.current_pulse_length == 0:
            self.current_pulse_length = self.preferred_pulse_length
        self.time += delta
        self.pulse_progress = self.pulse_progress + delta
        if self.pulse_progress >= self.current_pulse_length:
            pulseAgo = self.pulse_progress % self.current_pulse_length
            self.send_pulse(Pulse(self.name, pulseAgo))
            self.pulse_progress = 0
            # How much time the pulse was ago
            # Reset speed

            own_offset = self.time % self.preferred_pulse_length

            rp2 = []
            for pulse in self.received_pulses:
                offset = (((self.time - pulse)) % self.preferred_pulse_length) 
                rp2.append(offset)

            if rp2 == []:
                rp2=[0]
            mean_shift = circmean(samples = rp2, low = 0.0, high = self.preferred_pulse_length)
            adjusted_pulse_length = self.preferred_pulse_length - mean_shift if mean_shift < (0.5 * self.preferred_pulse_length) else mean_shift 
            self.current_pulse_length = ((1.0 -self.dampening) * adjusted_pulse_length) + (self.dampening * self.preferred_pulse_length) 
            # self.speed = self.dampening * self.speed + (1.0 -self.dampening) * new_speed
            self.received_pulses.clear()
        self.brightness = (self.pulse_progress / self.current_pulse_length) * 255
    
    def receive_pulse(self, pulse):
        # What our own pulse progress was, when the other pulse was send
        received_at = self.time - pulse.ago
        self.received_pulses.append(received_at)
