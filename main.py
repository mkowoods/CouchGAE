#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
import logging
#import time
from google.appengine.ext import db

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
TEMPLATES = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                                extensions=['jinja2.ext.autoescape'],
                                autoescape=True)



#Errors
class dbNotFoundException(Exception):
    """Exception where db is not found in the Data Store"""
    api_response = '{"status": "error", \
                    "message": "Database Does Not Exist"}'

class CreateWithoutValException(Exception):

    api_response = '{"status": "error", \
                    "message": "Attempted To Create Record without Value"}'

class MissingEssentialFieldException(Exception):

    api_response = '{"status": "error", \
                    "message": "Missing a Critical Field (action, db, key...)"}'

class KeyAlreadyExistsError(Exception):
    pass


#Model
class KeyValueStore(db.Model):
    """Ths Model is designed to be a simple lookup table with a key val store
    The rec_class serves the function of a table from a standard SQL Database. A way of organizing like records together.
    The Key is designed to be unique to facilitate quick look ups.
    """
    create_date = db.DateTimeProperty(auto_now_add = True)
    rec_class = db.StringProperty(required = True)
    store_key = db.StringProperty(required = True)
    store_val = db.StringProperty(required = True)


class DBStore1(KeyValueStore):
    """First Key Value Store"""
    pass

class DevStore(KeyValueStore):
    "Key Value Store for "
    pass



#Controller
DB_TO_MODEL_MAP = {'dbstore1': DBStore1,
                   'dev': DevStore}

class APIController():

    def __init__(self, action, db, rec_class = "", key = "", val = ""):
        self.key = key
        self.rec_class = rec_class
        self.action = action
        self.val = val

        if db in DB_TO_MODEL_MAP:
            self.db = DB_TO_MODEL_MAP[db]
        else:
            raise dbNotFoundException()


    def create(self):
        if self.val == "":
            raise CreateWithoutValException

        #TODO: Need to add a look up to see if the key already exists
        
        if self.db.get_by_key_name(self.key):
            raise KeyAlreadyExistsError
        rec = self.db(key_name = self.key, rec_class = self.rec_class, store_key = self.key, store_val = self.val)
        put = db.put(rec)
        return put

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass


    def run_action(self):

        if self.action == "create":
            return self.create()


#View
class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = TEMPLATES.get_template('index.html')
        self.response.write(template.render())



class APIHandler(webapp2.RequestHandler):
    def get(self):
        action = self.request.get('action')
        db = self.request.get('db')
        rec_class = self.request.get('rec_class')
        key = self.request.get('store_key')
        val = self.request.get('store_val')

        #if one of the critical fields is missing then it should bypass the call to the API Controller
        if action == "" or db == "" or key == "":
            self.response.write(MissingEssentialFieldException.api_response)

        API =  APIController(action, db, rec_class, key, val)

        try:
            api_response = API.run_action()
        except CreateWithoutValException:
            api_response = CreateWithoutValException.api_response
        except dbNotFoundException:
            api_response = dbNotFoundException.api_response

        self.response.write(api_response)






app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/api', APIHandler),
], debug=True)




