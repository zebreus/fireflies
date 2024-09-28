class Pulse:
    def __init__(self, sender, ago):
        # The sender usually sends the pulse a few millis after it actually pulsed
        # This field specifies how old the pulse was when it was send
        self.ago = ago
        # Unique name of the sender
        self.sender = sender

class Firefly:
    def __init__(self, name, send_pulse, preferred_pulse_length = 300, initial_time = 0):
        self.brightness = initial_time
        self.preferred_pulse_length = preferred_pulse_length
        self.pulse_progress = initial_time
        self.send_pulse = send_pulse
        self.name = name
    
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
