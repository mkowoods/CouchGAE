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

SUPPORTED_ACTIONS = ["read", "create", "update", "delete"]



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
                    "message": "Missing a Critical Field (action, db, key, table...)"}


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
    create_epoch = db.IntegerProperty(required=True)
    last_update_date = db.DateTimeProperty(auto_now_add=True)
    last_update_epoch = db.IntegerProperty(required=True)
    api_key = db.StringProperty(required=True)
    table = db.StringProperty(required=True)
    store_key = db.StringProperty(required=True)
    store_val = db.StringProperty(required=True)

    def json_response(self):
        response = {
            'status': 'OK',
            'created_date': str(self.create_date),
            'create_epoch': self.create_epoch,
            'last_update_date': str(self.last_update_date),
            'last_update_epoch': self.last_update_epoch,
            'api_key': self.api_key,
            'table': self.table,
            'key': self.store_key,
            'value': self.store_val
        }
        return response


class DBStore1(KeyValueStore):
    """First Key Value Store"""
    pass


class DevStore(KeyValueStore):
    """Key Value Store for """
    pass

DB_TO_MODEL_MAP = {'dbstore1': DBStore1,
                   'dev': DevStore}


#Controller

#TODO Need to define class to generate unique API Keys. Probably need to create a separate Database to store this data
class GenerateAPIKeys(object):
    pass


class APIController():

    def __init__(self, action, db, api_key, table, key, val, limit, offset):

        self.key = key
        self.table = table
        self.action = action
        self.val = val
        self.api_key = api_key

        #TODO: Figure out a better way to handle this exception
        try:
            self.offset = int(offset)
        except ValueError:
            self.offset = 0

        try:
            self.limit = int(limit)
        except ValueError:
            self.limit = 25

        if db in DB_TO_MODEL_MAP:
            self.db = DB_TO_MODEL_MAP[db]
        else:
            raise DBNotFoundException()

    def get_key_name(self):
        return '|'.join([self.api_key, self.table, self.key])

    def get_rec_by_key_name(self):

        rec = self.db.get_by_key_name(key_names=self.get_key_name())
        if not rec:
            raise KeyNotFoundError
        return rec

    @staticmethod
    def get_current_epoch_time():
        return int(time.time()*10000)

    def create(self):
        if self.val == "":
            raise CreateWithoutValException

        if self.db.get_by_key_name(key_names=self.get_key_name()):
            raise KeyAlreadyExistsError

        time_stamp = self.get_current_epoch_time()

        rec = self.db(key_name=self.get_key_name(),
                      api_key=self.api_key,
                      create_epoch=time_stamp,
                      last_update_epoch = time_stamp,
                      table=self.table,
                      store_key=self.key,
                      store_val=self.val)
        #TODO Need to handler in case put fails
        put = db.put(rec)
        return put.id_or_name()

    def read(self):

        if self.key:
            rec = self.get_rec_by_key_name()
            return rec.json_response()

        elif self.table:
            q = db.Query(self.db)
            q.filter('table =', self.table)

            results = q.fetch(limit=self.limit, offset=self.offset)

            return [r.json_response() for r in results]

        else:
            raise MissingEssentialFieldException

    def update(self):

        if self.val == "":
            raise CreateWithoutValException

        if self.key:
            rec = self.get_rec_by_key_name()
            rec.store_val = self.val
            rec.last_update_epoch = self.get_current_epoch_time()
            return rec.json_response()

        else:
            raise MissingEssentialFieldException

    def delete(self):
        rec = self.get_rec_by_key_name()
        return db.delete(rec)

    def run_action(self):

        if self.action == "create":
            return self.create()

        elif self.action == "read":
            return self.read()

        elif self.action == "delete":
            return self.delete()

        elif self.action == "update":
            return self.update()



#View

class MainHandler(webapp2.RequestHandler):
    def get(self):
        logging.info(self.request.host)
        template = TEMPLATES.get_template('index.html')
        self.response.write(template.render())





class APIHandler(webapp2.RequestHandler):
    def get(self):
        action = self.request.get('action')
        db = self.request.get('db')
        api_key = self.request.get('api_key')
        table = self.request.get('table')
        key = self.request.get('store_key')
        val = self.request.get('store_val')
        offset = self.request.get('offset')
        limit = self.request.get('limit')

        #if one of the critical fields is missing then it should bypass the call to the API Controller
        if action not in SUPPORTED_ACTIONS or db == "":
            self.response.write(MissingEssentialFieldException.api_response)


        API = APIController(action=action, db=db,
                            table=table, key=key,
                            val=val, offset=offset,
                            limit=limit, api_key=api_key)

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




