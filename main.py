#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import time
import webapp2
import jinja2
import logging
import json
import time
from google.appengine.ext import db

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
TEMPLATES = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                               extensions=['jinja2.ext.autoescape'],
                               autoescape=True)


# Errors
class DBNotFoundException(Exception):
    """Exception where db is not found in the Data Store"""
    api_response = {"status": "error",
                    "message": "Database Does Not Exist"}


class CreateWithoutValException(Exception):
    api_response = {"status": "error",
                    "message": "Attempted To Create Record without Value"}


class MissingEssentialFieldException(Exception):
    api_response = {"status": "error",
                    "message": "Missing a Critical Field (action, db, key...)"}


class KeyAlreadyExistsError(Exception):
    api_response = {"status": "error",
                    }



class KeyNotFoundError(Exception):
    pass


#Model
class KeyValueStore(db.Model):
    """Ths Model is designed to be a simple lookup table with a key val store
    The rec_class serves the function of a table from a standard SQL Database. A way of organizing like records together.
    The Key is designed to be unique to facilitate quick look ups.
    """

    create_date = db.DateTimeProperty(auto_now_add=True)
    epoch_time = db.StringProperty()
    rec_class = db.StringProperty(required=True)
    store_key = db.StringProperty(required=True)
    store_val = db.StringProperty(required=True)


    def json_response(self):
        response = {
            'status': 'OK',
            'created_date': str(self.create_date),
            'rec_class': self.rec_class,
            'key': self.store_key,
            'epoch_time': self.epoch_time,
            'value': self.store_val
        }
        return response


class DBStore1(KeyValueStore):
    """First Key Value Store"""
    pass


class DevStore(KeyValueStore):
    """Key Value Store for """
    pass


#Controller
DB_TO_MODEL_MAP = {'dbstore1': DBStore1,
                   'dev': DevStore}


class APIController():
    def __init__(self, action, db, rec_class="", key="", val="", offset=""):
        self.key = key
        self.rec_class = rec_class
        self.action = action
        self.val = val

        #TODO: Figure out a better way to handle this exception
        try:
            self.offset = int(offset)
        except ValueError:
            self.offset = 0

        if db in DB_TO_MODEL_MAP:
            self.db = DB_TO_MODEL_MAP[db]
        else:
            raise DBNotFoundException()

    def create(self):
        if self.val == "":
            raise CreateWithoutValException

        #TODO: Need to add a look up to see if the key already exists

        if self.db.get_by_key_name(self.key):
            raise KeyAlreadyExistsError

        time_stamp = str(int(time.time()*10000))

        rec = self.db(key_name=self.key,
                      epoch_time = time_stamp,
                      rec_class=self.rec_class,
                      store_key=self.key,
                      store_val=self.val)
        put = db.put(rec)
        return put.id_or_name()

    def read(self):
        rec = self.db.get_by_key_name(key_names=self.key)
        if not rec:
            raise KeyNotFoundError
        return rec.json_response()

    def read_rec_class(self, offset=None):
        q = db.Query(self.db)
        q.filter('rec_class =', self.rec_class)
        limit = 25

        results = q.fetch(limit=limit, offset=self.offset)

        return [r.json_response() for r in results]

    def update(self):
        pass

    def delete(self):
        pass

    def run_action(self):

        if self.action == "create":
            return self.create()

        elif self.action == "read":
            return self.read()

        elif self.action == "read_rec_class":
            return self.read_rec_class()


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
        offset = self.request.get('offset')

        #if one of the critical fields is missing then it should bypass the call to the API Controller
        if action == "" or db == "":
            self.response.write(MissingEssentialFieldException.api_response)

        API = APIController(action, db, rec_class, key, val, offset)

        try:
            api_response = API.run_action()
        except CreateWithoutValException:
            api_response = CreateWithoutValException.api_response
        except DBNotFoundException:
            api_response = DBNotFoundException.api_response
        except KeyAlreadyExistsError:
            api_response = KeyAlreadyExistsError.api_response

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(api_response, indent=4))


app = webapp2.WSGIApplication([
                                  ('/', MainHandler),
                                  ('/api', APIHandler),
                              ], debug=True)




