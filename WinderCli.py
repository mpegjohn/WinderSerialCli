from __future__ import print_function
import time
from winderCliLib.winderSerial import Ifc



def main():
    print("Welcome to the winder interface")

    interface = Ifc()

    port = get_port_selection(interface)
    print("Port selected: " + port)
    interface.selected_port = port

    interface.setup_serial()

    interface.write_job(0.5, 18.0, 200, 3, 22)


    print_menu()


def get_port_selection(interface):
    """Prints a list of serial ports, and allows selection of one
    Args:
        interface (WinderCli) - A winder interface object
    Returns:
        A selected port

    If q is selected program quits.
    """

    while(True):
        print("-------------------------------------")
        print("Select the correct serial port from the list")

        all_ports = interface.get_all_ports()

        selection = 0
        for port in all_ports:
            print ("(%d) %s" % (selection, port))
            selection +=1
        print("(%d) quit" % selection)
        print("-------------------------------------")

        choice = int(raw_input("Choice: "))

        if choice not in range(0,selection+1,1):
            print("Invalid choice")
            time.sleep(3)
            continue
        if choice ==  len(all_ports):
            exit(0)

        return all_ports[choice]



def print_menu(wire_size=0.0, spool_length=0.0, num_turns=0.0):
    while (True):

        print("-------------------------------------")
        print("w : Set wire size %2.3f" % (wire_size))
        print("l : Set wire spool length %2.2f" % (spool_length))
        print("n : Set number of turns %8.1f" % (num_turns))
        print("r : Run")
        print("p : Pause")
        print("j : Review job")
        print("-------------------------------------")

        selection = raw_input("Choose option: ")

        if (selection.lower() == 'w'):
            got_size = enter_size("Enter wire size")

            if (got_size != 'q'):
                wire_size = got_size
            else:
                continue
        elif (selection.lower() == 'l'):
            got_size = enter_size("Enter spool length")

            if (got_size != 'q'):
                spool_length = got_size
            else:
                continue
        elif (selection.lower() == 'n'):
            got_size = enter_size("Enter number of turns")

            if (got_size != 'q'):
                num_turns = got_size
            else:
                continue
        elif (selection.lower() == 'j'):
            return



def enter_size(descripion):
    while (True):
        size_selection = raw_input(descripion + " (q quit): ")

        if (size_selection.lower() == 'q'):
            return 'q'
        else:
            parsed_size = 0.0
            try:
                parsed_size = float(size_selection)
            except ValueError:
                print("Size should be a float\n")
                time.sleep(3)
                continue
            return parsed_size


if __name__ == '__main__':
    main()
