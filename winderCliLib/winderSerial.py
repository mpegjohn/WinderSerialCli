"""
All classes that relate to the arduino winder serial interface.
"""

import struct
import serial
import serial.tools.list_ports


class Ifc(object):
    def __init__(self, selected_port=None):
        """Construvtor
        Args:
             selected_port (string) - Optional port selelection.
        """
        self._selected_port = selected_port
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
        self.ser = serial.Serial(self.selected_port)
        return

    def write_job(self, wire_size, spool_length, turns, num_layers, last_turns):
        """Writes a job to the arduino.

         Sends data in the required sequence to setup a new winding job.
         SJ = Setup Job
         WS[4 bytes] - wire size
         SL[4 bytes] - spool length
         TT[4 bytes] - number of turns
         NL[1 byte ] -- Number of whole layers
         LL[4 bytes ] -- Turns last layer
         DN - Done

         Args:
             wire_size (float) - The wire diameter in mm
             spool_length (float) - The spool length in mm
             turns (float) - Total number of turns
             num_layers (int) - The number of layers
             last_turns (float) - The number of turns on the last layer

         """
        self.send_heading('SJ')
        self.send_heading('WS')
        self.send_float(wire_size)
        self.send_heading('SL')
        self.send_float(spool_length)
        self.send_heading('TT')
        self.send_float(turns)
        self.send_heading('NL')
        self.send_byte(num_layers)
        self.send_heading('LL')
        self.send_float(last_turns)
        self.send_heading('DN')

    def send_heading(self, heading):
        """ Sends a two byte ascii heading to the arduino

        Args:
            heading (string) - The heading to send
        Returns:
            True if all sent OK
        Raises:
            TypeError - Non string type as argument
            BufferError - Bytes sent diaparity or data disparity

        """
        if not isinstance(heading, basestring):
            raise TypeError("Heading must be a string")

        num_bytes = self.ser.write(heading)

        if (num_bytes != len(heading)):
            raise BufferError("Only sent %d bytes" % num_bytes)

        echo_chars = self.ser.readline()
        echo_chars = echo_chars.rstrip()

        if (heading != echo_chars):
            raise BufferError("Data not received correctly sent %s got %s" % (heading, echo_chars))

        return True

    def send_byte(self, data):
        """ Sends a byte of data to the arduino
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
            raise ValueError("bytes should be no graeter than 255")

        if data < 0:
            raise ValueError("bytes should be unsigned")

        usigned_byte = struct.pack('B', data);

        num_sent = self.ser.write(usigned_byte)

        if num_sent != 1:
            raise BufferError("Didn't send 1 byte")

        echo_data = self.ser.read(1)

        if echo_data != usigned_byte:
            BufferError("Byte sent and recieved don't agree")

        return True

    def send_float(self, data):
        """ Sends a float to the arduino
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

        num_sent = self.ser.write(ieee754_data)
        if num_sent != 4:
            raise BufferError("Didn't send 4 bytes")

        echo_data = self.ser.read(4)

        my_float = struct.unpack('f', echo_data)

        if echo_data != ieee754_data:
            raise BufferError("Float sent and recieved don't agree")

        return True
