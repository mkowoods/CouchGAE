#TODO: need to add several tests
#first is a simple create read test to confirm that the records wrote as expected
#Next is a test on limits and maybe a test on

import requests
import unittest
import sys
import getopt

class MyTests(unittest.TestCase):

    def setUp(self):
        self.url = raw_input("Enter in Host URL: ")
        self.API_KEY = 'thisisnotarealkey'
        self.r = requests.get(self.url)

    def test_serving(self):
        self.assertTrue(self.r.status_code == 200)

    def test_create_record(self):
        params = {'action': 'create', 'db': 'dev',
                  'api_key': self.API_KEY, 'table':'unit-test',
                  'store_key': 'unit-test-key', 'store_val': 'unit-test-val'}
        r = requests.get(self.url+"/api", params = params)

    def test_delete_record(self):
        pass

    def test_create_without_val(self):
        """should generate a CreateWithoutValException"""
        pass

    def test_create_existing_record(self):
        """should generate a KeyAlreadyExistsError"""
        pass

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()