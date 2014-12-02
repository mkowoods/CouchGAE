#!/usr/bin/env python


import requests
import unittest
import json

#TODO: need to add several tests
#first is a simple create read test to confirm that the records wrote as expected
#Next is a test on limits and maybe a test on


class MyTests(unittest.TestCase):

    def setUp(self):
        #self.url = raw_input("Enter in Host URL: ")
        self.url = "http://localhost:8080"
        self.db = "dev"
        self.API_KEY = "thisisnotarealkey"
        self.table = "unit-test"
        self.key = "unit-test-key"
        self.r = requests.get(self.url)

    def test0_serving(self):
        self.assertTrue(self.r.status_code == 200)

    def test1_create_record_1(self):
        params = {'action': 'create', 'db': 'dev',
                  'api_key': self.API_KEY, 'table':'unit-test',
                  'store_key': 'unit-test-key', 'store_val': 'unit-test-val'}
        r = requests.get(self.url+"/api", params = params)
        #print r.url
        #print r.text
        self.assertEqual(json.loads(r.text), self.API_KEY+"|"+params['table']+"|"+params['store_key'])

    def test1_create_record_2(self):
        params = {'action': 'create', 'db': 'dev',
                  'api_key': self.API_KEY, 'table':'unit-test',
                  'store_key': 'unit-test-key2', 'store_val': 'unit-test-val'}
        r = requests.get(self.url+"/api", params = params)
        #print r.url
        #print r.text
        self.assertEqual(json.loads(r.text), self.API_KEY+"|"+params['table']+"|"+params['store_key'])

    def test2_read_record_1(self):
        params = {'action': 'read', 'db': 'dev',
                  'api_key': self.API_KEY, 'table':'unit-test',
                  'store_key': 'unit-test-key'}
        r = requests.get(self.url+"/api", params = params)
        res = json.loads(r.text)
        self.assertEqual(res['key'], params['store_key'])


    def test2_read_record_2(self):
        params = {'action': 'read', 'db': 'dev',
                  'api_key': self.API_KEY, 'table':'unit-test',
                  'store_key': 'unit-test-key2'}
        r = requests.get(self.url+"/api", params = params)
        res = json.loads(r.text)
        self.assertEqual(res['key'], params['store_key'])

    def test2_read_records_in_table(self):
        params = {'action': 'read', 'db': 'dev',
                  'api_key': self.API_KEY, 'table':'unit-test'}
        r = requests.get(self.url+"/api", params = params)
        res = json.loads(r.text)
        self.assertEqual(len(res), 2)

    def test3_delete_record_1(self):
        params = {'action': 'delete', 'db': 'dev',
                  'api_key': self.API_KEY, 'table':'unit-test',
                  'store_key': 'unit-test-key'}
        r = requests.get(self.url+"/api", params = params)
        self.assertIsNone(json.loads(r.text))

    def test3_delete_record_2(self):
        params = {'action': 'delete', 'db': 'dev',
                  'api_key': self.API_KEY, 'table':'unit-test',
                  'store_key': 'unit-test-key2'}
        r = requests.get(self.url+"/api", params = params)
        self.assertIsNone(json.loads(r.text))

    def test4_create_without_val(self):
        """should generate a CreateWithoutValException"""
        params = {'action': 'delete', 'db': 'dev',
                  'api_key': self.API_KEY, 'table':'unit-test',
                  'store_key': 'unit-test-key', 'store_val': 'unit-test-val'}
        r = requests.get(self.url+"/api", params = params)

    def test5_create_existing_record(self):
        """should generate a KeyAlreadyExistsError"""
        pass

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main(verbosity=2)