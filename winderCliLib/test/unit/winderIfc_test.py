from __future__ import absolute_import
import serial.tools.list_ports
import unittest
import os
import pty
import struct

from mock import MagicMock, patch
from winderCliLib.winderSerial import Ifc


class MyTestCase(unittest.TestCase):
    def test_ifc_instantiatio(self):
        self.assertIsInstance(self.interface, Ifc, "The interface is not an instance of ifc")

    def setUp(self):
        master, slave = pty.openpty()
        self.slave_name = os.ttyname(slave)
        self.interface = Ifc(self.slave_name)

    def test_list_ports_3_ports(self):
        comports = [['/dev/ttyS0'], ['/dev/ttyS1'], ['/dev/ttyS2'], ]
        serial.tools.list_ports.comports = MagicMock(return_value=comports)
        all_ports = self.interface.get_all_ports()
        self.assertEqual(len(all_ports), 3, ' There were not 3 ports returned')

    def test_instance_with_port(self):
        self.assertEqual(self.interface.selected_port, self.slave_name, "Instance selecetd port has not been set")

    def test_selected_port(self):
        self.interface.selected_port = '/dev/ttyS0'
        self.assertEqual(self.interface.selected_port, '/dev/ttyS0', "Chosen port has not been set")

    @patch('serial.Serial.readline')
    def test_send_heading_good(self, mock_readline):
        mock_readline.return_value="SJ"
        self.interface.setup_serial()
        self.assertTrue(self.interface.send_heading("SJ"), "Start job not sent correctly")

    @patch('serial.Serial.readline')
    def test_send_heading_bad_response(self, mock_readline):
        mock_readline.return_value="SK"
        self.interface.setup_serial()
        with self.assertRaises(BufferError):
            self.interface.send_heading("SJ")

    @patch('serial.Serial.write')
    @patch('serial.Serial.readline')
    def test_send_heading_different_length_reported(self, mock_readline, mock_write):
        mock_readline.return_value="SJ"
        mock_write.return_value=1
        self.interface.setup_serial()
        with self.assertRaises(BufferError):
            self.interface.send_heading("SJ")

    def test_send_heading_wrong_type(self):
        self.interface.setup_serial()
        with self.assertRaises(TypeError) as cm:
            self.interface.send_heading(22)
        self.assertEquals("Heading must be a string", str(cm.exception))

    @patch('serial.Serial.read')
    def test_send_float_good(self, mock_read):
        ieee754_data = struct.pack('f', 123.456)
        mock_read.return_value=ieee754_data
        self.interface.setup_serial()
        self.assertTrue(self.interface.send_float(123.456))

    @patch('serial.Serial.read')
    def test_send_float_good_no_dp(self, mock_read):
        ieee754_data = struct.pack('f', 123456)
        mock_read.return_value=ieee754_data
        self.interface.setup_serial()
        self.assertTrue(self.interface.send_float(123456))

    @patch('serial.Serial.read')
    def test_send_float_non_float(self, mock_read):
        ieee754_data = struct.pack('f', 123.456)
        mock_read.return_value = ieee754_data
        self.interface.setup_serial()
        with self.assertRaises(TypeError) as cm:
            self.interface.send_float('dd')
        self.assertEquals("Data must be a float", str(cm.exception))

    @patch('serial.Serial.write')
    @patch('serial.Serial.read')
    def test_send_float_different_length_reported(self, mock_read, mock_write):
        ieee754_data = struct.pack('f', 123.456)
        mock_read.return_value = ieee754_data
        mock_write.return_value = 1
        self.interface.setup_serial()
        with self.assertRaises(BufferError):
            self.interface.send_float(123.456)

    @patch('serial.Serial.read')
    def test_send_byte_good(self, mock_read):
        byte_data = struct.pack('B', 123)
        mock_read.return_value = byte_data
        self.interface.setup_serial()
        self.assertTrue(self.interface.send_byte(123))

    def test_send_byte_gt_255(self):
        self.interface.setup_serial()
        with self.assertRaises(ValueError) as cm:
            self.interface.send_byte(12345)
        self.assertEquals("bytes should be no graeter than 255", str(cm.exception))

    def test_send_byte_lt_0(self):
        self.interface.setup_serial()
        with self.assertRaises(ValueError) as cm:
            self.interface.send_byte(-2)
        self.assertEquals("bytes should be unsigned", str(cm.exception))


if __name__ == '__main__':
    unittest.main()
