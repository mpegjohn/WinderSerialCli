"""Job is a utility object that describes a winder job."""
from math import modf

class Job(object):

    def __init__(self, wire_size, turns, spool_length):
        self.wire_size = wire_size
        self.turns = turns
        self.spool_length = spool_length
        self.pause_after_layer = False
        self.taps = []
        self.shuttle_direction = "L2R"
        self.spool_direction = "ACW"

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

    def update_status(self, layer_num, turns, layer_turns, speed, direction, running, at_tap, done_layer):
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

        self.at_tap = False
        if at_tap:
            self.at_tap = True

        self.done_layer = False
        if done_layer:
            self.done_layer = True

        self.turns_progress = (self.current_turns / self.turns) * 100

    def add_tap(self, turn):

        if(turn > self.turns):
            return False

        if(turn < 0.5):
            return False

        for tap in self.taps:
            if turn < tap + 0.4 and turn > tap - 0.4:
                return False
        self.taps.append(turn)
        self.taps.sort()
        return True

    def delete_tap(self, index):
        del self.taps[index]
        self.taps.sort()

    def taps_as_list(self):
        strtaps = [str(t) for t in self.taps]
        the_list = ",".join(strtaps)

        tap_list = "[" + the_list + "]"
        return tap_list



    def __str__(self):
        turns_repr =  "Number of Turns: %8.1f\n" % self.turns
        wire_repr =  "Wire Size: %2.3f mm\n" % self.wire_size
        spool_repr = "Spool length: %3.2f mm\n" % self.spool_length
        turns_per_layer_repr = "Turns per layer %4.1f\n" % self.turns_per_layer
        whole_layers_repr = "Number of whole layers: %d\n" % self.whole_layers
        last_layer_turns_repr = "Number of turns last layer: %4.1f\n" % self.turns_last_layer
        pause_after_layer_repr = "Pause at layer: %s\n" % self.pause_after_layer

        return turns_repr + wire_repr + spool_repr + turns_per_layer_repr + whole_layers_repr + last_layer_turns_repr \
                + pause_after_layer_repr

