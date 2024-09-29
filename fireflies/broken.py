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

    def __init__(self):
        self.speed = 1.0
    
    def tick(self, delta):
        new_pulse_progress = self.pulse_progress + (delta * self.speed)
        if (new_pulse_progress) >= self.preferred_pulse_length:
            # How much time the pulse was ago
            pulseAgo = ((new_pulse_progress) % self.preferred_pulse_length) / self.speed
            # Reset speed
            # self.speed = 1.0
            self.send_pulse(Pulse(self.name, pulseAgo))
        self.pulse_progress = (new_pulse_progress) % self.preferred_pulse_length
        self.brightness = (self.pulse_progress / self.preferred_pulse_length) * 255
    
    def receive_pulse(self, pulse):
        # What our own pulse progress was, when the other pulse was send
        received_at = self.pulse_progress - pulse.ago
        # received_at = 0.90% => speed = 1.25
        received_at_percentage = received_at / self.preferred_pulse_length
        if received_at_percentage > 0.5 and received_at_percentage < 0.99:
            self.pulse_progress = self.preferred_pulse_length - 1
        if received_at_percentage > 0.01 and received_at_percentage <= 0.50:
            self.pulse_progress = self.preferred_pulse_length - 1
