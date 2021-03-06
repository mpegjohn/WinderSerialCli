# -*- coding: utf-8 -*-

from time import sleep
from time import time
from winderCliLib.winderSerial import Ifc
from winderCliLib.winderJob import Job
from winderCliLib.configLoader import ConfigLoader
import sys
import select
import argparse


def main():
    print("Welcome to the winder interface")

    parser = argparse.ArgumentParser(description='The Winder interface')
    parser.add_argument('--noifc', help='enable this if you just want the front end', action='store_true', default=False)
    args = parser.parse_args()

    if not args.noifc:

        interface = Ifc()

        port = get_port_selection(interface)
        print("Port selected: " + port)
        interface.selected_port = port

        interface.setup_serial()
        print_menu(interface)
    else:
        print_menu(None)


def get_port_selection(interface):
    """Prints a list of serial ports, and allows selection of one
    Args:
        interface (WinderCli) - A winder interface object
    Returns:
        A selected port

    If q is selected program quits.
    """

    while True:
        print("-------------------------------------")
        print("Select the correct serial port from the list")

        all_ports = interface.get_all_ports()

        for selection, port in enumerate(all_ports):
            print ("(%d) %s" % (selection, port))
            selection +=1
        print("(%d) quit" % selection)
        print("-------------------------------------")

        try:
            choice = int(input("Choice: "))
        except ValueError:
            print("Must be an integer")
            continue

        if choice not in range(selection):
            print("Invalid choice")
            sleep(3)
            continue
        if choice ==  len(all_ports):
            exit(0)

        return all_ports[choice]


def print_menu(interface):
    """This is the main menu."""

    job = Job(0.5, 500, 18.0)

    while True:

        print("-------------------------------------")
        print("w : Set wire size %2.3f" % job.wire_size)
        print("l : Set wire spool length %3.2f" % job.spool_length)
        print("n : Set number of turns %8.1f" % job.turns)
        print("t : Taps %s" % job.taps_as_list())
        print("p : Pause after every layer %s" % job.pause_after_layer)
        print("d : Directions Spool: %s, Shuttle: %s" % (job.spool_direction, job.shuttle_direction))
        print("r : Run")
        print("m : Manual Motor control")
        print("j : Review job")
        print("h : Shuttle go home")
        print("f : Load setup from file..")
        print("q : Quit program")
        print("-------------------------------------")

        selection = input("Choose option: ").lower()

        if selection == 'w':
            got_size = enter_size("Enter wire size")

            if got_size != 'q':
                job.wire_size = got_size
            else:
                continue
        elif selection == 'l':
            got_size = enter_size("Enter spool length")

            if got_size != 'q':
                job.spool_length = got_size
            else:
                continue
        elif selection == 'p':
            job.pause_after_layer = not job.pause_after_layer
        elif selection == 'd':
            set_directions(job)
            continue
        elif selection == 'n':
            got_size = enter_size("Enter number of turns")

            if got_size != 'q':
                job.turns = got_size
            else:
                continue
        elif selection == 'h':
            interface.go_home()
        elif selection == 'f':
            my_config = ConfigLoader()
            if not my_config.set_yaml_config():
                continue
            my_config.parse_config()
            my_config.list_windings()
            if not my_config.get_winding_selection():
                continue

            job.wire_size = float(my_config.selected_winding['wire size'])
            job.spool_length = float(my_config.selected_winding['length'])
            job.turns = float(my_config.selected_winding['turns'])

            if 'taps' in my_config.selected_winding:
                for tap in my_config.selected_winding['taps']:
                    job.add_tap(float(tap['turns']))
            continue

        elif selection == 'j':
            job.calculate_stackup()
            print("\n-------------------------------------")
            print("Calculated stackup")
            print("-------------------------------------")
            print (job.__str__())
            print("-------------------------------------")
            input("Hit enter to continue")
            continue
        elif selection == 't':
            taps(job)
            continue
        elif selection == 'm':
            motor_control(interface)
            continue
        elif selection == 'r':
            job.calculate_stackup()
            print("\n-------------------------------------")
            print("Run a job with this stackup?")
            print("-------------------------------------")
            print (job.__str__())
            print ("Taps %s" % job.taps_as_list())
            print("-------------------------------------")
            selection = input("y/n: ").lower()
            if selection == 'y':
                execute_job(job, interface)
            continue
        elif selection == 'q':
            exit(0)
        else:
            print("Unkown option")
            sleep(3)
            continue


def set_directions(job):

    while True :
        print("-------------------------------------")
        print("s: Spool direction %s" % job.spool_direction)
        print("h: shuttle direction %s" % job.shuttle_direction)
        print("q: Quit menu")

        selection = input("Enter selection: ").lower()

        if selection == 'q':
            return
        elif selection == 's':
            if job.spool_direction == "ACW":
                job.spool_direction = "CW"
            else:
                job.spool_direction = "ACW"
            continue
        elif selection == 'h':
            if job.shuttle_direction == "L2R":
                job.shuttle_direction = "R2L"
            else:
                job.shuttle_direction = "L2R"
            continue
        else:
            print("Unknown selection")
            sleep(3)
            continue


def taps(job):

    while True:
        print("-------------------------------------")
        print("a: Add a tap")
        print("d: delete a tap")
        print("l: List all taps")
        print("q: Quit menu")

        selection = input("Enter selection: ").lower()

        if selection == 'q':
            return
        elif selection == 'a':
            tap_turns = enter_size("Enter turns for tap: ")

            if not job.add_tap(tap_turns):
                print("Unable to add this tap\n")
            else:
                print("Added Tap at %8.1f" % tap_turns)
            sleep(2)
            continue
        elif selection == 'l':

            if not print_taps(job):
                continue

            input("Hit enter to continue")
            continue
        elif selection == 'd':

            num_taps = print_taps(job)
            if num_taps == 0:
                continue

            while True:
                index = input("Enter index of tap to delete (q quit menu): ")

                tap_range = range(num_taps)

                if index.lower() == 'q':
                    break

                try:
                    index = int(index)
                except ValueError:
                    print("Enter an integer value")
                    sleep(3)
                    continue

                if index not in tap_range:
                    print("Index not in range")
                    sleep(3)
                    continue
                else:
                    job.delete_tap(index)
                    break
        else:
            print("Unknown selection")
            sleep(3)
            continue


def print_taps(job):
    if len(job.taps) == 0:
        print("No Taps are set")
        sleep(3)
        return 0
    print("-------------------------------------")
    print("Taps")
    print("-------------------------------------")

    for i, tap in enumerate(job.taps):
        print("(%d) at %8.1f" % (i, tap))
        i += 1
    return i


def execute_job(job, interface):
    """Runs this job.against this interface"""
    interface.write_job(job)

    interface.get_status(job)

    interface.start()

    start = time()
    now = time() - start

    suffix = ("[Turns: %6.1f Layer: %d Speed: %1.1f T/S Time: %d s]" % (job.current_turns, job.current_layer_mum, job.current_speed, now))

    print ("")
    sys.stdout.write("\r" + suffix)
    sys.stdout.flush()
#    printProgressBar(job.turns_progress, prefix='Progress:', suffix=suffix, bar_length=50)
    sleep(1)

    while True:
        interface.get_status(job)
#       sys.stdout.write("\rTurns: %6.1f Layer: %d Speed: %1.1f TPS Progress: %3.1f%%" % (job.current_turns, job.current_layer_mum, job.current_speed, job.turns_progress))
        now = time() - start
        suffix = ("[Turns: %6.1f Layer: %d Speed: %1.1f T/S Time: %d s]" % (job.current_turns, job.current_layer_mum, job.current_speed, now))
        sys.stdout.write("\r" + suffix)
        sys.stdout.flush()
#       printProgressBar(job.turns_progress, prefix='Progress:', suffix=suffix, bar_length=50)

        if heard_enter(1.5):
            interface.pause()
            while True:
                print("\n-------------------------------------")
                print("Winder is PAUSED")
                print("-------------------------------------")
                print("c : Continue job")
                print("q : Quit job")

                input_value = input("Make a selection: ").lower()

                if input_value == 'q':
                    return
                elif input_value == 'c':
                    interface.start()
                    sleep(0.2)
                    break
                else:
                    print("Unknown option")
                    sleep(1)
                    continue

        if job.at_tap:
            interface.get_status(job)
            input("\nAt tap %3.1f, press any key" % job.current_turns)
            interface.start()

        #if job.done_layer:
        #    interface.get_status(job)
        #    input("\nDone layer %3.1f, press any key" % job.current_turns)
        #    interface.start()

        if not job.current_running:
            print("")
            break
        sleep(1)
    return


def enter_size(description):
    while True:
        size_selection = input(description + " (q quit): ").lower()

        if size_selection == 'q':
            return 'q'
        else:
            try:
                parsed_size = float(size_selection)
            except ValueError:
                print("Size should be a float\n")
                sleep(3)
                continue
            return parsed_size


def motor_control(interface):
    """Menu motor control menu"""
    while True:
        (spool, shuttle) = interface.get_motor_status()
        print("\n-------------------------------------")
        print("Motor control")
        print("-------------------------------------")

        spool_state = "Disabled"
        if spool:
            spool_state =  "Enabled"
        shuttle_state = "Disabled"
        if shuttle:
            shuttle_state =  "Enabled"

        print("s : Toggle spool (%s)" % spool_state)
        print("h : Toggle shuttle (%s)" % shuttle_state)
        print("c : Turn spool clockwise")
        print("a : Turn spool anti- clockwise")
        print("q : quit")
        selection = input("Choose option: ").lower()

        if selection == 'q':
            return

        if selection == 's':
            interface.toggle_motor_state('spool')
            continue
        elif selection == 'h':
            interface.toggle_motor_state('shuttle')
            continue
        elif selection == "c" or selection == "a":
            if selection == "c":
                interface.spool_motor("CW")
            else:
                interface.spool_motor("CC")

            input("Hit enter to stop")
            interface.spool_motor(" ", stop= True)
            continue
        else:
            print("Unkown option")
            sleep(3)
            continue


# From Gist https://gist.github.com/aubricus/f91fb55dc6ba5557fbab06119420dd6a
def print_progress_bar(progress, prefix='', suffix='', decimals=1, bar_length=100):
    """Print Progress in bar form
    Call in a loop to create terminal progress bar
    @params:
        progress    - Required  : Progress to be represented in %
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(progress)
    filled_length = int(round(bar_length * progress/100.0))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    sys.stdout.flush()


def heard_enter(timeout):
    i, o, e = select.select([sys.stdin],[],[],timeout)
    for s in i:
        if s == sys.stdin:
            sys.stdin.readline()
            return True
    return False


if __name__ == '__main__':
    main()
