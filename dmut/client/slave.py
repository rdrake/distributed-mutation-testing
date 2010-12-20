from json import loads
from os import chdir, getcwd
from os.path import exists, join
from shutil import rmtree
from subprocess import Popen, PIPE
from urllib.request import urlopen
from uuid import uuid1
from zipfile import ZipFile

import sys

sys.path.append(getcwd() + "/distributed-mutation-testing")

from dmut.common.storage import FileStore
from dmut.common.util import log, mkdir_p, patch, reverse_patch

class Slave:
	def __init__(self, hostname):
		self.name = str(uuid1())
		self.hostname = hostname
		self.download_dir = "/tmp/dmut"
		self.work_dir = "/tmp/%s" % self.name

		self._init()

		log("Waiting for work.")
	
	def __enter__(self):
		return self

	def test(self, id):
		"""
		Performs the testing of a particular mutant.

		Returns True if all tests pass, False if one fails.
		"""
		self.id = id
		status = True
		test = self.fs.get(self.id)
		patch_file = test.read()
		log("Retrieved patch.")
		log("Executing operator %s on file %s." % (test.op, test.file_name))
		
		self._setup(patch_file)

		for test_name in self.settings["tests"]:
			if not self._run_test_case(test_name):
				log("%s failed." % test_name)
				status = False
				break

		self._teardown()
		
		if not status:
			self.fs.killed(self.id)

	def _setup(self, patch_file):
		"""
		Cleans up, applies patch.
		"""
		z = ZipFile(self.source_path)
		z.extractall(self.work_dir)
		log("Extracted source file.")

		for cmd in self.settings["commands"]["preprocess"]:
			self._exec_command_quiet(cmd)
		log("Executed pre-processing commands.")

		self._clean()
		log("Cleaned working directory.")

		chdir(join(self.work_dir, self.settings["source"]["dir"]))
		patch(patch_file)
		chdir(self.work_dir)
		log("Applied patch.")
		
		log("Building code.  This may take a while.")
		if self._exec_command_quiet(self.settings["commands"]["build"]):
			log("Built current code.")
		else:
			self.fs.build_error(self.id)
			raise Exception()
	
	def _run_test_case(self, test_name):
		"""
		Runs the specified test case on the current copy of the code.
		
		Returns True on success and False on failure.
		"""
		return Popen(["java", "-cp", self.settings["paths"]["classpath"], self.settings["commands"]["test"], test_name], stdin=PIPE, stdout=PIPE, stderr=PIPE).wait() == 0
	
	def _teardown(self):
		"""
		Removes old mutated code.
		"""
		rmtree(join(self.work_dir, "*"), True)
		log("Removed working directory.")
	
	def _init(self):
		mkdir_p(self.download_dir)
		mkdir_p(self.work_dir)

		# Load settings from the specified hostname.
		u = urlopen("http://%s/client.settings" % self.hostname)
		self.settings = loads(u.read().decode("utf-8"))
		log("Loaded client.settings.")

		self.fs = FileStore(self.settings["database"]["name"])
		log("Initialized storage.")

		self.source_path = join(self.download_dir, self.settings["source"]["name"])

		if not exists(self.source_path):
			u = urlopen(self.settings["source"]["location"])
			f = open(self.source_path, "wb")
			f.write(u.read())
			log("Downloaded source file.")

		chdir(self.work_dir)
		log("Moved into work directory.")

	def _exec_command_quiet(self, cmd):
		p = Popen(cmd, stdout=open("/dev/null"), shell=True)
		return p.wait() == 0

	def _clean(self):
		if self._exec_command_quiet(self.settings["commands"]["clean"]):
			log("Cleaned project.")
		else:
			raise Exception()
	
	def __exit__(self, type, value, traceback):
		"""
		Remove the working directory completely.  Ignore any warnings about
		it still containing files.
		"""
		rmtree(self.work_dir, True)
		log("Removed working directory.")

if __name__ == "__main__":
	from xmlrpc.client import ServerProxy

	if len(sys.argv) == 3:
		http_hostname = sys.argv[1]
		master_hostname = sys.argv[2]

		master = ServerProxy("http://%s" % master_hostname)

		with Slave(http_hostname) as s:
			while True:
				id = master.get()
				
				if not id:
					log("No more work.  Terminating.")
					break

				try:
					s.test(id)
				except:
					log("*** ERROR ***:  Something went wrong with the test.")
		
	else:
		raise ValueError("Usage:  %s %s <http hostname> <master hostname>" % (sys.executable, sys.argv[0]))
