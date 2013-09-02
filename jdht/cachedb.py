import logging
import hashlib
import random
import cPickle as pickle

from datetime import datetime
from config import KEY, ADDRESS_SPACE
from blowfish import Blowfish

from virtual_co import WriteWait, ReadWait


def get_hash(data):
    return int(hashlib.sha1(data).hexdigest(), 20)


def random_id(seed=None):
    if seed:
        random.seed(seed)

    return random.randint(0, (2 ** ADDRESS_SPACE) - 1)


# get_index = lambda d1, d2: i = floor(log(d1 ^ d2))
# depracated?
def get_index(value1, value2): 
    distance = value1 ^ value2
    length = -1
    while (distance):
        distance >>= 1
        length += 1
    return max(0, length)


from config import ADDRESS_SPACE, K
class kBucket(object):

    _instance = None

    def __init__(self, addr, port, uuid):
        self.addr, self.port, self.uuid = addr, port, uuid
        self.buckets = [[] for _ in range(ADDRESS_SPACE)]

    def __new__(self, *args, **kwargs):
        if not self._instance:
            self._instance = super(kBucket, self).__new__(self, *args, **kwargs)
        return self._instance

    def insert(self, addr, port, uuid):
        if self.uuid != uuid:
            bucket = self.buckets[self._get_index(uuid)]
            if (addr, port, uuid) in bucket:
                bucket.pop(bucket.index((addr, port, uuid)))
            elif len(bucket) >= K:
                bucket.pop(0)
            logging.debug("kBucket.inserting({0}, {1}, {2})".format(addr, port, uuid))
            bucket.append((addr, port, uuid))
            
    def _get_index(self, uuid):
        distance = self.uuid ^ uuid
        length = -1
        while (distance):
            distance >>= 1
            length += 1
        return max(0, length)

    def get_nearest_nodes(self, key, limit=None):
        sol_num = limit if limit else K
        all_nodes = (node for bucket in self.buckets for node in bucket)
        return sorted(all_nodes, key=lambda node: key ^ node[2])[:sol_num]


class DB(object):

    _instance = None
    
    def __init__(self, cipher=Blowfish(KEY), filename=".cdb"):
        self.docs = {}
        self.cipher = cipher
        self.filename = filename
        

    def __new__(self, *args, **kwargs):
        if not self._instance:
            self._instance = super(DB, self).__new__(self, *args, **kwargs)
        return self._instance


    def add(self, key, doc):
        self.docs[key] = doc


    def __setitem__(self, key, value):
        self.docs[key] = value
        logging.debug("Saving self.docs[{0}] = {1}".format(key, value))


    def remove(self, key):
        if self.docs.pop(key, 0):
            return True
        else:
            return False

            
    def get(self, key):
        if key in self.docs:
            return self.docs[key]
        else:
            return None


    def __getitem__(self, key):
        return self.get(key)


    def get_all(self):
        return self.docs


    def save(self):
        self.cipher.initCTR()
        with open(self.filename, "wb+") as f:
            yield WriteWait(f)
            f.write(
                self.cipher.encryptCTR(
                    pickle.dumps(self.docs)))


    def load(self):
        self.cipher.initCTR()
        try:
            with open(self.filename, "rb") as f:
                yield ReadWait(f)
                self.docs = pickle.loads(
                    self.cipher.decryptCTR(f.read()))
                logging.debug("Database successfully loaded.")
                yield self.docs
        except Exception, e:
            logging.error("Error loading DB file: {0}".format(e))
