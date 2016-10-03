# -*- coding: utf-8 -*-
import couchdb
import json
from ocds.storage.exceptions import ReleaseExistsError
from couchdb.design import ViewDefinition
from .design.releases import views
from ocds.storage.helpers import get_db_url
from ocds.export.helpers import encoder, decoder
from couchdb.json import use


use(decode=decoder, encode=encoder)


class CouchStorage(object):

    def __init__(self, config):
        url = get_db_url(
            config.get('username'),
            config.get('password'),
            config.get('host'),
            config.get('port'),
        )
        db_name = config.get('name')
        server = couchdb.client.Server(url)
        if db_name not in server:
            server.create(db_name)
        self.db = server[db_name]
        ViewDefinition.sync_many(self.db, views)

    def get(self, doc_id):
        return self.db.get(doc_id)

    def save(self, doc):
        if '_id' not in doc:
            doc['_id'] = doc['id']
        self.db.save(doc)

    def __contains__(self, key):
        #resp = self.db.view('releases/ocid', key=key)
        return key in self.db

    def get_last(self, key):
        resp = self.db.view('releases/ocid', key=key, descending=True)
        return resp[0]['value']

    def get_releases(self, ocid):
        resp = self.db.view('releases/ocid', key=ocid)
        return [r['value'] for r in resp]

    def get_tags(self, ocid):
        resp = self.db.view('releases/tags', key=ocid)
        return set([x['value'] for x in resp])
