import struct
import serial
import serial.tools.list_ports


class Ifc:

    def __init__(self):
        return

    def get_all_ports(self):
        all_ports = serial.tools.list_ports.comports()

        ports = []

        for port in all_ports:
            ports.append(port[0]) # Add a port to the list

        return ports



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