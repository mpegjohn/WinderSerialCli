# -*- coding: utf-8 -*-

from __future__ import print_function
from time import sleep
from time import time
from winderCliLib.winderSerial import Ifc
from winderCliLib.winderJob import Job
import sys
import select

def main():
    print("Welcome to the winder interface")

    interface = Ifc()

    port = get_port_selection(interface)
    print("Port selected: " + port)
    interface.selected_port = port

    interface.setup_serial()
    print_menu(interface)


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

        for selection, port in enumerate(all_ports):
            print ("(%d) %s" % (selection, port))
            selection +=1
        print("(%d) quit" % selection)
        print("-------------------------------------")

        try:
            choice = int(raw_input("Choice: "))
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

    while (True):

        print("-------------------------------------")
        print("w : Set wire size %2.3f" % (job.wire_size))
        print("l : Set wire spool length %3.2f" % (job.spool_length))
        print("n : Set number of turns %8.1f" % (job.turns))
        print("t : Taps")
        print("p : Pause after every layer")
        print("r : Run")
        print("m : Manual Motor control")
        print("j : Review job")
        print("q : Quit program")
        print("-------------------------------------")

        selection = raw_input("Choose option: ").lower()

        if (selection == 'w'):
            got_size = enter_size("Enter wire size")

            if (got_size != 'q'):
                job.wire_size = got_size
            else:
                continue
        elif selection == 'l':
            got_size = enter_size("Enter spool length")

            if (got_size != 'q'):
                job.spool_length = got_size
            else:
                continue
        elif (selection == 'p'):
            job.pause_after_layer = True
        elif (selection == 'n'):
            got_size = enter_size("Enter number of turns")

            if (got_size != 'q'):
                job.turns = got_size
            else:
                continue
        elif (selection == 'j'):
            job.calculate_stackup()
            print("\n-------------------------------------")
            print("Calculated stackup")
            print("-------------------------------------")
            print (job.__str__())
            print("-------------------------------------")
            raw_input("Hit enter to continue")
            continue
        elif (selection == 't'):
            taps(job)
            continue
        elif (selection == 'm'):
            motor_control(interface)
            continue
        elif (selection == 'r'):
            job.calculate_stackup()
            print("\n-------------------------------------")
            print("Run a job with this stackup?")
            print("-------------------------------------")
            print (job.__str__())
            print("-------------------------------------")
            selection = raw_input("y/n: ").lower()
            if selection == 'y':
                execute_job(job, interface)
            continue
        elif selection == 'q':
            exit(0)
        else:
            print("Unkown option")
            sleep(3)
            continue


def taps(job):

    while(True):
        print("-------------------------------------")
        print("a: Add a tap")
        print("d: delete a tap")
        print("l: List all taps")
        print("q: Quit manu")

        selection = raw_input("Enter selection: ").lower()

        if selection == 'q':
            return
        elif selection == 'a':
            tap_turns = enter_size("Enter turns for tap: ")

            if not job.add_tap(tap_turns):
                print("Unable to add this tap\n")
            else:
                print("Added Tap at %8.1f" % tap_turns)
            sleep(3)
            continue
        elif selection == 'l':

            if not print_taps(job):
                continue

            raw_input("Hit enter to continue")
            continue
        elif selection == 'd':

            num_taps = print_taps(job)
            if num_taps == 0:
                continue

            while(True):
                index = raw_input("Enter index of tap to delete (q quit manu): ")

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

    while(True):
        interface.get_status(job)
#       sys.stdout.write("\rTurns: %6.1f Layer: %d Speed: %1.1f TPS Progress: %3.1f%%" % (job.current_turns, job.current_layer_mum, job.current_speed, job.turns_progress))
        now = time() - start
        suffix = ("[Turns: %6.1f Layer: %d Speed: %1.1f T/S Time: %d s]" % (job.current_turns, job.current_layer_mum, job.current_speed, now))
        sys.stdout.write("\r" + suffix)
        sys.stdout.flush()
#       printProgressBar(job.turns_progress, prefix='Progress:', suffix=suffix, bar_length=50)

        if heardEnter(1.5):
            interface.pause()
            while(True):
                print("\n-------------------------------------")
                print("Winder is PAUSED")
                print("-------------------------------------")
                print("c : Continue job")
                print("q : Quit job")

                input = raw_input("Make a selection: ").lower()

                if input == 'q':
                    return
                elif input == 'c':
                    interface.start()
                    sleep(0.2)
                    break
                else:
                    print("Unkown option")
                    sleep(3)
                    continue

        if job.at_tap:
            interface.get_status(job)
            raw_input("\nAt tap %3.1f, press any key" % job.current_turns)
            interface.start()

        if job.done_layer:
            interface.get_status(job)
            raw_input("\nDone layer %3.1f, press any key" % job.current_turns)
            interface.start()

        if not job.current_running:
            print("")
            break
        sleep(1)
    return

def enter_size(descripion):
    while (True):
        size_selection = raw_input(descripion + " (q quit): ").lower()

        if (size_selection == 'q'):
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
    """Manu motor control menu"""
    while(True):
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
        selection = raw_input("Choose option: ").lower()

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

            raw_input("Hit enter to stop")
            interface.spool_motor(" ", stop= True)
            continue
        else:
            print("Unkown option")
            sleep(3)
            continue

# From Gist https://gist.github.com/aubricus/f91fb55dc6ba5557fbab06119420dd6a
def printProgressBar(progress, prefix='', suffix='', decimals=1, bar_length=100):
    """Print Progress in bar form
    Call in a loop to create terminal progress bar
    @params:
        progreaa    - Required  : Progress to be represented in %
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

def heardEnter(timeout):
    i,o,e = select.select([sys.stdin],[],[],timeout)
    for s in i:
        if s == sys.stdin:
            sys.stdin.readline()
            return True
    return False

if __name__ == '__main__':
    main()
