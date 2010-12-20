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
		return self.fs.put(f, op=op, file_name=fname, killed=False, built=True)
	
	def get(self, id):
		"""
		Retrieves a file given the unique identifier id.
		"""
		return self.fs.get(self._str_to_objid(id))
	
	def killed(self, id):
		"""
		Flag a mutant as having been killed.
		"""
		self.db.fs.files.update({ "_id": self._str_to_objid(id) }, { "$set": { "killed": True } })

	def build_error(self, id):
		"""
		Flag a mutant as causing a build error and thus being invalid.
		"""
		self.db.fs.files.update({ "_id": self._str_to_objid(id) }, { "$set": { "built": False } })

	def _str_to_objid(self, id):
		"""
		If necessary, converts string to ObjectId for querying.
		"""
		if isinstance(id, str):
			return ObjectId(id)
		elif isinstance(id, ObjectId):
			return id
		else:
			raise ValueError("Can't convert to ObjectId!")
