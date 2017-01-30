from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from __future__ import print_function

import time


def main():
    print("Welcome to the winder interface")

    print_menu()


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
        elif (selection.lower() == 'r'):



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
