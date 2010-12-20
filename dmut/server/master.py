from pymongo import Connection
from queue import Empty, Queue
from xmlrpc.server import SimpleXMLRPCServer

db = Connection()["mutants"]
mutants = db.fs.files

q = Queue()

for mutant in mutants.find({ "killed": False }):
	q.put(str(mutant["_id"]))

def get():
	try:
		return q.get()
	except Empty:
		return None

if __name__ == "__main__":
	server = SimpleXMLRPCServer(("", 8000))
	server.register_function(get, "get")
	server.serve_forever()
