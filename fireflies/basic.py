class Pulse:
    def __init__(self, sender, ago):
        # The sender usually sends the pulse a few millis after it actually pulsed
        # This field specifies how old the pulse was when it was send
        self.ago = ago
        # Unique name of the sender
        self.sender = sender

class Firefly:
    # These values will be set by the main loop
    name = ""
    preferred_pulse_length = 0
    send_pulse = None
    pulse_progress = 0
    dampening = 0.5

    # Value from 0 to 255. Will be read by the main loop
    brightness = 0

    def tick(self, delta):
        if (self.pulse_progress + delta) >= self.preferred_pulse_length:
            # How much time the pulse was ago
            pulseAgo = (self.pulse_progress + delta) % self.preferred_pulse_length
            self.send_pulse(Pulse(self.name, pulseAgo))
        self.pulse_progress = (self.pulse_progress + delta) % self.preferred_pulse_length
        self.brightness = (self.pulse_progress / self.preferred_pulse_length) * 255
    
    def receive_pulse(self, pulse):
        # TODO: Implement
        1+1
