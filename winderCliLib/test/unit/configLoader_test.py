from __future__ import absolute_import
import unittest
from winderCliLib.configLoader import ConfigLoader
from os import path, makedirs
import shutil

class MyTestCase(unittest.TestCase):
    def setUp(self):
        shutil.rmtree("/tmp/winder_setup_files", ignore_errors=True)


    def test_job_instance(self):
        my_config_loader = ConfigLoader()
        self.assertIsInstance(my_config_loader, ConfigLoader, "Incorrect object type")

    def test_get_config_files_none(self):
        my_config_loader = ConfigLoader("/tmp/winder_setup_files")
        if not path.exists(my_config_loader.config_dir):
            makedirs(my_config_loader.config_dir)
        files = my_config_loader.get_config_files()
        self.assertEqual(0, len(files), "Files exist")

    def test_get_config_files_one(self):
        my_config_loader = ConfigLoader("/tmp/winder_setup_files")
        if not path.exists(my_config_loader.config_dir):
            makedirs(my_config_loader.config_dir)
        shutil.copy2("PWAM01D.yaml", my_config_loader.config_dir)

    def test_get_config_parse(self):
        my_config_loader = ConfigLoader("/tmp/winder_setup_files")
        if not path.exists(my_config_loader.config_dir):
            makedirs(my_config_loader.config_dir)
        shutil.copy2("PWAM01D.yaml", my_config_loader.config_dir)
        my_config_loader.config_file = my_config_loader.get_config_files()[0]
        my_config_loader.parse_config()



    def tearDown(self):
        shutil.rmtree("/tmp/winder_setup_files", ignore_errors=True)

if __name__ == '__main__':
    unittest.main()
