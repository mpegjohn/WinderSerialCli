# -*- coding: utf-8 -*-

from __future__ import print_function
import time
from winderCliLib.winderSerial import Ifc
from winderCliLib.winderJob import Job
import sys

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

def print_menu(interface):
    """This is the main menu."""

    job = Job(0.5, 500, 18.0)

    while (True):

        print("-------------------------------------")
        print("w : Set wire size %2.3f" % (job.wire_size))
        print("l : Set wire spool length %3.2f" % (job.spool_length))
        print("n : Set number of turns %8.1f" % (job.turns))
        print("r : Run")
        print("m : Manual Motor control")
        print("j : Review job")
        print("q : Quit program")
        print("-------------------------------------")

        selection = raw_input("Choose option: ")

        if (selection.lower() == 'w'):
            got_size = enter_size("Enter wire size")

            if (got_size != 'q'):
                job.wire_size = got_size
            else:
                continue
        elif (selection.lower() == 'l'):
            got_size = enter_size("Enter spool length")

            if (got_size != 'q'):
                job.spool_length = got_size
            else:
                continue
        elif (selection.lower() == 'n'):
            got_size = enter_size("Enter number of turns")

            if (got_size != 'q'):
                job.turns = got_size
            else:
                continue
        elif (selection.lower() == 'j'):
            job.calculate_stackup()
            print("\n-------------------------------------")
            print("Calculated stackup")
            print("-------------------------------------")
            print (job.__str__())
            print("-------------------------------------\n")
            continue
        elif (selection.lower() == 'm'):
            motor_control(interface)
            continue
        elif (selection.lower() == 'r'):
            job.calculate_stackup()
            print("\n-------------------------------------")
            print("Run a job with this stackup?")
            print("-------------------------------------")
            print (job.__str__())
            print("-------------------------------------\n")
            selection = raw_input("y/n: ")
            if selection.lower() == 'y':
                execute_job(job, interface)
            continue
        elif (selection.lower() == 'q'):
            exit(0)
        else:
            print("Unkown option")
            time.sleep(3)
            continue

def execute_job(job, interface):
    """Runs this job.against this interface"""
    interface.write_job(job)

    interface.get_status(job)

    interface.start()
    suffix = ("Complete [Turns: %6.1f Layer: %d Speed: %1.1f TPS]" % (job.current_turns, job.current_layer_mum, job.current_speed))

    print ("")

    printProgressBar(job.turns_progress, prefix='Progress:', suffix=suffix, bar_length=50)
    time.sleep(1)

    while(True):
        interface.get_status(job)
#       sys.stdout.write("\rTurns: %6.1f Layer: %d Speed: %1.1f TPS Progress: %3.1f%%" % (job.current_turns, job.current_layer_mum, job.current_speed, job.turns_progress))
        suffix = ("Complete [Turns: %6.1f Layer: %d Speed: %1.1f TPS]" % (job.current_turns, job.current_layer_mum, job.current_speed))
        printProgressBar(job.turns_progress, prefix='Progress:', suffix=suffix, bar_length=50)

        if not job.current_running:
            print("")
            break
        time.sleep(1)
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
        print("q : quit")
        selection = raw_input("Choose option: ")

        if selection.lower() == 'q':
            return

        if selection.lower() == 's':
            interface.toggle_motor_state('spool')
            continue

        elif selection.lower() == 'h':
            interface.toggle_motor_state('shuttle')
            continue
        else:
            print("Unkown option")
            time.sleep(3)
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

if __name__ == '__main__':
    main()
