import serial
import struct






def print_menu(wire_size = 0.0, spool_length = 0.0, num_turns = 0.0):


    while(True):

        print "-------------------------------------"
        print "w : Set wire size %2.3f" % (wire_size)
        print "l : Set wire spool length %2.2f" % (spool_length)
        print "t : Set number of turns %8.1f" % (num_turns)
        print "g : Run"
        print "p : Pause"
        print "r : Review job"
        print "-------------------------------------"

        selection = raw_input("Choose option: ")

        if (selection.lower() == 'w'):
            wire_size_selection = raw_input("Wire diameter in mm (q=cancel): ")

            if (wire_size_selection.lower() == 'q'):
                continue
            else:
                parsed_wire_size = 0.0
                try:
                    parsed_wire_size = float(wire_size_selection)
                except ValueError:
                    print "wire size should be a float\n"
                    continue


def main():

    print "Welcome to the winder interface"

    print_menu()


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



if __name__ == '__main__':
    main()