from __future__ import absolute_import
import serial.tools.list_ports
import unittest
from mock import MagicMock
import winderIfc

class MyTestCase(unittest.TestCase):
    def test_ifc_instantiatio(self):
        interface = winderIfc.Ifc()

        self.assertIsInstance(interface, winderIfc.Ifc, "The interface is not an instance of ifc")


    def test_list_ports_3_ports(self):
        interface = winderIfc.Ifc()

        comports = [['/dev/ttyS0'], ['/dev/ttyS1'], ['/dev/ttyS2'],]
        serial.tools.list_ports.comports = MagicMock(return_value = comports)

        all_ports = interface.get_all_ports()

        self.assertEqual(len(all_ports), 3, ' There were not 3 ports returned')

    def test_set_port(self):
        interface = winderIfc.Ifc()

        interface.selected_port = '/dev/ttyS0'






if __name__ == '__main__':
    unittest.main()
