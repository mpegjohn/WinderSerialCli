"""
All classes that relate to the Arduino winder serial interface.
"""
from winderJob import Job
import struct
import serial
import serial.tools.list_ports
import time


class Ifc(object):
    def __init__(self, selected_port=None):
        """Constructor
        Args:
             selected_port (string) - Optional port selection.
        """
        self._selected_port = selected_port
        self.motors = {}
        self.motors['spool'] = True
        self.motors['shuttle'] = True

        self.motors['state'] = 0x03 # Both motors on

        return

    def get_all_ports(self):
        """Get all the serial ports on this machine
        Returns:
            ports {list) - List of all port names
        """
        all_ports = serial.tools.list_ports.comports()

        ports = []

        for port in all_ports:
            ports.append(port[0])  # Add a port to the list

        return ports

    @property
    def selected_port(self):
        """Sets the selected port."""
        return self._selected_port

    @selected_port.setter
    def selected_port(self, val):
        """Gets the selected port."""
        self._selected_port = val

    def setup_serial(self):
        """Sets the serial port up using the selected port."""
        self.ser = serial.Serial(baudrate=115200, port=self.selected_port, timeout=5, write_timeout=5)
        time.sleep(2)
        return

    def write_job(self, job):
        """Writes a job to the Arduino.

         Sends data in the required sequence to setup a new winding job.
         SJ = Setup Job
         WS[4 bytes] - wire size
         SL[4 bytes] - spool length
         TT[4 bytes] - number of turns
         NL[1 byte ] -- Number of whole layers
         LL[4 bytes ] -- Turns last layer
         PL(if pause after layer ==True)
         DN - Done

         Args:
             job (Job) - A job to send

         """
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

        self.send_heading('SJ')
        self.send_heading('RS') # Reset all counters
        self.send_heading('WS')
        self.send_float(job.wire_size)
        self.send_heading('TT')
        self.send_float(job.turns)
        self.send_heading('SL')
        self.send_float(job.spool_length)
        self.send_heading('TL')
        self.send_float(job.turns_per_layer)
        self.send_heading('NL')
        self.send_byte(job.whole_layers)
        self.send_heading('LL')
        self.send_float(job.turns_last_layer)

        if job.shuttle_direction == "R2L":
            self.send_heading('SR') # Shuttle reverse

        if job.spool_direction == "CW":
            self.send_heading('PR')  # Spool reverse

        if(job.pause_after_layer):
            self.send_heading('PL')

        for tap in job.taps:
            self.send_heading('AT')
            self.send_float(tap)

        self.send_heading('DN')

    def send_heading(self, heading):
        """ Sends a two byte ascii heading to the Arduino

        Args:
            heading (string) - The heading to send
        Returns:
            True if all sent OK
        Raises:
            TypeError - Non string type as argument
            BufferError - Bytes sent disparity or data disparity

        """

        if not isinstance(heading, basestring):
            raise TypeError("Heading must be a string")

        self.ser.reset_input_buffer()


        num_bytes = self.ser.write(heading)

        if num_bytes != len(heading):
            raise BufferError("Only sent %d bytes" % num_bytes)

        echo_chars = self.ser.readline()
        echo_chars = echo_chars.rstrip()

        if heading != echo_chars:
            raise BufferError("Data not received correctly sent %s got %s" % (heading, echo_chars))

        return True

    def send_byte(self, data):
        """ Sends a byte of data to the Arduino
        Args:
             data (int) - Data to send
        Returns:
            True if all OK
        Raises:
            TypeError - If data is not an int
            ValueError - if value not within byte range of 0-255
            BufferError - If data disparity
        """

        try:
            int(data)
        except ValueError:
            raise TypeError("Data must be an int")

        if data > 255:
            raise ValueError("bytes should be no greater than 255")

        if data < 0:
            raise ValueError("bytes should be unsigned")

        unsigned_byte = struct.pack('B', data)

        self.ser.reset_input_buffer()

        num_sent = self.ser.write(unsigned_byte)

        if num_sent != 1:
            raise BufferError("Didn't send 1 byte")

        echo_data = self.ser.read(1)

        if echo_data != unsigned_byte:
            BufferError("Byte sent and received don't agree")

        return True

    def send_float(self, data):
        """ Sends a float to the Arduino
        The float is converted to a 4 byte ieee754 data block and
        sent as a 4 byte bit of data.

        Args:
             data (float) - Data to send
        Returns:
            True if all OK
        Raises:
            TypeError - If data is not an float
            ValueError - if value not within byte range of 0-255
            BufferError - If data disparity

        """

        try:
            float(data)
        except ValueError:
            raise TypeError("Data must be a float")

        ieee754_data = struct.pack('f', data)

        self.ser.reset_input_buffer()

        num_sent = self.ser.write(ieee754_data)
        if num_sent != 4:
            raise BufferError("Didn't send 4 bytes")

        echo_data = self.ser.read(4)

        if echo_data != ieee754_data:
            raise BufferError("Float sent and received don't agree")

        return True

    def get_status(self, job):
        """Gets the current status from the winder."""
        self.send_heading('GS')
        layer_number_byte = self.ser.read(1)
        turns_bytes = self.ser.read(4)
        layer_turns_bytes = self.ser.read(4)
        speed_bytes = self.ser.read(4)
        direction_byte = self.ser.read(1)
        running_byte = self.ser.read(1)
        at_tap_byte = self.ser.read(1)

        layer_number = struct.unpack('B', layer_number_byte)[0]
        turns = struct.unpack('f', turns_bytes)[0]
        layer_turns = struct.unpack('f', layer_turns_bytes)[0]
        speed = struct.unpack('f', speed_bytes)[0]
        direction = struct.unpack('B', direction_byte)[0]
        running = struct.unpack('B', running_byte)[0]
        at_tap = struct.unpack('B', at_tap_byte)[0]
        done_layer = struct.unpack('B', at_tap_byte)[0]

        job.update_status(layer_num=layer_number, turns=turns, layer_turns=layer_turns, speed=speed, direction=direction, running=running, at_tap=at_tap, done_layer=done_layer )

    def add_tap(self, turn):
        self.send_heading('AT')
        self.send_float(turn)

    def toggle_motor_state(self, motor):

        if motor not in ['spool', 'shuttle']:
            raise ValueError(motor + "is not a valid motor")

        self.motors[motor] = not self.motors[motor]
        self.set_motors()

    def set_motors(self):

        byte_to_send = 0x03

        if not self.motors['spool']:
            byte_to_send &= 0x2
        if not self.motors['shuttle']:
            byte_to_send &= 0x01

        self.send_heading("SM")
        self.send_byte(byte_to_send)

        return True

    def go_home(self):
        self.send_heading("GH")

    def get_motor_status(self):
        return (self.motors['spool'], self.motors['shuttle'])

    def pause(self):
        self.send_heading("PS")

    def start(self):
        self.send_heading("GO")

    def spool_motor(self, direction, stop = False):

        if stop:
            self.send_heading("ST")
            return

        if direction == "CW":
            self.send_heading("SC")
        else:
            self.send_heading("SA")











