"""Job is a utility object that describes a winder job."""
from math import modf

class Job(object):

    def __init__(self, wire_size, turns, spool_length):
        self.wire_size = wire_size
        self.turns = turns
        self.spool_length = spool_length

    def calculate_stackup(self):
        """Calculates the stackup for this job
        Using the turns, wire size and spool length calculate the
        turns per layer, number of layers and the last turns.

        """
        self.turns_per_layer = int(self.spool_length/self.wire_size)

        layers = self.turns/float(self.turns_per_layer)

        (fractional_part, integer_part) = modf(layers)

        self.whole_layers = int(integer_part)
        self.turns_last_layer = fractional_part * float(self.turns_per_layer)
        self.turns_last_layer = round(self.turns_last_layer)

    def update_status(self, layer_num, turns, layer_turns, speed, direction, running):
        """Updates the status of the winding
        Calculates the percent complete.
        """
        self.current_layer_mum = layer_num
        self.current_turns = turns
        self.current_layer_turns = layer_turns
        self.current_speed = speed

        self.current_direction = "L to R"

        if direction:
            self.current_direction = "R to L"

        self.current_running = False
        if running:
            self.current_running = True

        self.turns_progress = (self.current_turns / self.turns) * 100




