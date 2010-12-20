from pymongo import Connection
from queue import Empty, Queue
from time import time
from xmlrpc.server import SimpleXMLRPCServer

import os
import sys

sys.path.append(os.getcwd())

from dmut.common.util import log

db = Connection()["mutants"]
mutants = db.fs.files

q = Queue()

log("Populating queue with mutants.")

for mutant in mutants.find({ "killed": False }):
	q.put(str(mutant["_id"]))

log("Queue populated.  Ready to serve.")

start = time()

def get():
	try:
		return q.get()
	except Empty:
		log("Completed in %.02f." % (time() - start))
		return None

if __name__ == "__main__":
	server = SimpleXMLRPCServer(("", 8000))
	server.register_function(get, "get")
	server.serve_forever()
