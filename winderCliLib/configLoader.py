import yaml
import glob
from os.path import expanduser, join
from time import sleep

class ConfigLoader(object):

    def __init__(self, path='HOME'):
        if path == 'HOME':
            self.home_dir = expanduser("~")
            self.config_dir = join(self.home_dir, "winder_setup_files")
        else:
            self.config_dir = path

    def set_yaml_config(self):

        while(True):
            print("-------------------------------------")
            print("Selected file = None")
            print("s: select a file")
            print("q: Quit menu")

            selection = raw_input("Enter selection: ").lower()

            if selection == 'q':
                return False
            elif selection == 's':
                files = self.get_config_files()

                if files.__len__() == 0:
                    while(True):
                        print("There are no config files")
                        raw_input("\npress any key")
                        break
                    continue
                else:
                    print("-------------------------------------")
                    print("Config files found:")
                    num_files = 0
                    for i, file in enumerate(files):
                        print "%s %s" % (i, file)
                        num_files = i+1

                    while(True):
                        index = raw_input("Enter index of file (q quit manu): ")

                        file_range = range(num_files)

                        if index.lower() == 'q':
                            break

                        try:
                            index = int(index)
                        except ValueError:
                            print("Enter an integer value")
                            sleep(3)
                            continue

                        if index not in file_range:
                            print("Index not in range")
                            sleep(3)
                            continue
                        else:
                            self.config_file = files[index]
                            return True

    def parse_config(self):
        with open(self.config_file, 'r') as stream:
            try:
                self.yaml_object = yaml.load(stream)
            except yaml.YAMLError as exc:
                print ("Unable to load file")
                print (exc.message)
                return

    def list_windings(self):
        for i, winding in enumerate(self.yaml_object['windings']):
            name = winding['name']
            turns = winding['turns']
            wire = winding['wire size']
            length = winding['length']
            print("%s: Winding %s:" % (i, name))
            if 'voltage' in winding:
                voltage = winding['voltage']
                print("\tVoltage %s" % voltage)
            print("\tTurns %s" % turns)
            print("\tWire size %s" % wire)
            print("\tLength %s" % length)
            if 'taps' in winding:
                print("\tThis winding also has taps:")
                taps = winding['taps']
                for tap in taps:
                    voltage = tap['voltage']
                    turns = tap['turns']
                    print("\t\tTap at %s turns, voltage %s" % (turns, voltage))
            self.winding_range = i + 1

    def get_winding_selection(self):
        while(True):
            index = raw_input("Enter index of winding to load (q quit manu): ")

            sel_range = range(self.winding_range)

            if index.lower() == 'q':
                return False

            try:
                index = int(index)
            except ValueError:
                print("Enter an integer value")
                sleep(3)
                continue

            if index not in sel_range:
                print("Index not in range")
                sleep(3)
                continue
            else:
                self.selected_winding = self.yaml_object['windings'][index]
                return True

    def get_config_files(self):
        files = glob.glob(join(self.config_dir, "*.yaml"))
        return files