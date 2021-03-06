from __future__ import absolute_import
import unittest
from winderCliLib.winderJob import Job



class MyTestCase(unittest.TestCase):

    def test_job_instance(self):
        my_job = Job(0.5, 1250, 18.0)
        self.assertIsInstance(my_job, Job, "Incorrect object type")

    def test_job_params(self):
        my_job = Job(0.5, 1250, 18.0)
        self.assertEqual(my_job.wire_size, 0.5, "Wire size not set correctly")
        self.assertEquals(my_job.spool_length, 18.0, "Spool length not set correctly")
        self.assertEqual(my_job.turns, 1250, "Turns not set correctly")

    def test_job_calculate_stackup(self):
        my_job = Job(0.5, 1250, 18.0)
        my_job.calculate_stackup()
        self.assertEqual(my_job.whole_layers, 34, "Incorrect whole layers")
        self.assertEqual(my_job.turns_per_layer, 36.0, "Incorrect turns per layer")
        self.assertEqual(my_job.turns_last_layer, 26.0, "Incorrect turns last layer")

    def test_job_calculate_stackup_no_last_layer(self):
        my_job = Job(0.5, 36, 18.0)
        my_job.calculate_stackup()
        self.assertEqual(my_job.whole_layers, 1, "Incorrect whole layers")
        self.assertEqual(my_job.turns_per_layer, 36.0, "Incorrect turns per layer")
        self.assertEqual(my_job.turns_last_layer, 0, "Incorrect turns last layer")

    def test_job_calculate_stackup_half_layer(self):
        my_job = Job(0.5, 18, 18.0)
        my_job.calculate_stackup()
        self.assertEqual(my_job.whole_layers, 0, "Incorrect whole layers")
        self.assertEqual(my_job.turns_per_layer, 36.0, "Incorrect turns per layer")
        self.assertEqual(my_job.turns_last_layer, 18, "Incorrect turns last layer")


    def test_add_tap(self):
        my_job = Job(0.5, 1250, 18.0)
        self.assertTrue(my_job.add_tap(123.0), "Failed to add Tap")

    def test_add_tap_past_turns(self):
        my_job = Job(0.5, 1250, 18.0)
        self.assertFalse(my_job.add_tap(1260), "Managed to add tap past the end of the turns")

    def test_add_tap_twice(self):
        my_job = Job(0.5, 1250, 18.0)
        my_job.add_tap(123.0)
        self.assertFalse(my_job.add_tap(123.0), "Managed to add tap twice")
        self.assertFalse(my_job.add_tap(123.3), "Managed to add tap twice on upper limit")
        self.assertFalse(my_job.add_tap(122.7), "Managed to add tap twice on lower limit")

    def test_add_tap_at_zero(self):
        my_job = Job(0.5, 1250, 18.0)
        self.assertFalse(my_job.add_tap(0), "Managed to add tap at zero")


if __name__ == '__main__':
    unittest.main()
