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

