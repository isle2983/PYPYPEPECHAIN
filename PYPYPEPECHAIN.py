#!/usr/bin/env pypy
# Copyright (c) 2017 The PYPYPEPECHAIN developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os
import json
import urllib
import hashlib
import datetime

PEPE_LIST_FILENAME = "pepelist.json"
PEPE_LIST_URL = os.path.join("http://rarepepedirectory.com/json/",
                             PEPE_LIST_FILENAME)
PEPE_DIR = "/tmp/dank/RAREPEPES"
PEPE_LIST_FILE = os.path.join(PEPE_DIR, PEPE_LIST_FILENAME)

def get_list_dict():
    if not os.path.exists(PEPE_DIR):
        os.makedirs(PEPE_DIR)
    print "downloading %s" % PEPE_LIST_FILE
    urllib.urlretrieve(PEPE_LIST_URL, PEPE_LIST_FILE)
    l = open(PEPE_LIST_FILE, 'r')
    list_dict = json.loads(l.read())
    l.close()
    return list_dict

BUF_SIZE = 65536

def get_hash(file_path):
    sha256 = hashlib.sha256()
    f = open(file_path, 'rb')
    while True:
        data = f.read(BUF_SIZE)
        if not data:
            break
        sha256.update(data)
    return sha256.hexdigest()

SKIP_DOWNLOAD_IF_EXISTS = True

def fetch_and_compute(l):
    for k, v in l.items():
        filename = v.decode('utf-8').split('/')[-1]
        extension = filename.split('.')[-1]
        file_dl_path = os.path.join(PEPE_DIR, '.'.join([k, extension]))
        if not SKIP_DOWNLOAD_IF_EXISTS or not os.path.exists(file_dl_path):
            print "downloading %s" % file_dl_path
            urllib.urlretrieve(v, file_dl_path)
        else:
            print "skipping download of %s" % file_dl_path
        yield {'symbol': k,
               'file':   file_dl_path,
               'sha256': get_hash(file_dl_path)}

if __name__ == "__main__":
    results = fetch_and_compute(get_list_dict())

    cumulative = hashlib.sha256()
    for r in sorted(results, key=lambda x: x['symbol']):
        cumulative.update(r['sha256'])
        print "%15s %s %s %s" % (r['symbol'], r['sha256'][0:20],
                                 cumulative.hexdigest()[0:20], r['file'])

    print ("----------------------------------------------------------------\n"
           "cumulative sha256: %s" % cumulative.hexdigest())
    print "current utc time is: %s" % datetime.datetime.utcnow()
