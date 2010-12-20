from pymongo import Connection
from pymongo.objectid import ObjectId

import gridfs

class FileStore:
	def __init__(self, db_name):
		self.db = Connection()[db_name]
		self.fs = gridfs.GridFS(self.db)
	
	def put(self, f, op, fname):
		"""
		Places a file f in the storage pool.  Also creates an entry in the
		database with the operator name used to create the file, and the
		original file name of the mutant's ancestor.
		"""
		return self.fs.put(f, op=op, file_name=fname, killed=False)
	
	def get(self, id):
		# Seemlessly handle string IDs.
		if isinstance(id, str):
			id = ObjectId(id)

		"""
		Retrieves a file given the unique identifier id.
		"""
		return self.fs.get(id)
