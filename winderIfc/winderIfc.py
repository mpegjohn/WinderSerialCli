import struct
import serial
import serial.tools.list_ports


class Ifc(object):

    def __init__(self, selected_port=None):
        self._selected_port = selected_port
        return

    def get_all_ports(self):
        all_ports = serial.tools.list_ports.comports()

        ports = []

        for port in all_ports:
            ports.append(port[0]) # Add a port to the list

        return ports

    @property
    def selected_port(self):
        return self._selected_port

    @selected_port.setter
    def selected_port(self, val):
        self._selected_port = val

    """ Writes a job to the arduino
    sends '1' for set job mode
    WS[4 bytes] - wire size
    SL[4 bytes] - spool length
    NT[4 bytes] - number of turns
    """
    def write_job(self, **kwargs):
        




#try:
#    ieee754_data = my_serial.read(4)
#    my_float = struct.unpack('f', ieee754_data)
#catch:
#    # I/O Error, or junk data
#    my_float = 0.0
#And packing:

# ieee754_data = struct.pack('f', my_float)
# try:
#     my_serial.write(ieee754_data)
# catch:
#     pass #TODO - I/O Error