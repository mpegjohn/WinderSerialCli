import unittest
import WinderCli

class dummy_interface:

    def __init__(self):
        return

    def get_all_ports(self):

        ports = ['/dev/ttyS0', '/dev/ttyS1']
        return ports


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def setUp(self):
        self.interface = dummy_interface()

    def test_get_port_selection(self):
        ports = WinderCli.get_port_selection(self.interface)



if __name__ == '__main__':
    unittest.main()
