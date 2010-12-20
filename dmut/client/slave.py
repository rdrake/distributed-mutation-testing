from json import loads
from os import chdir, getcwd
from os.path import join
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
		self.name = "61c3782c-0bd5-11e0-8872-1cc1de5b973e"#str(uuid1())
		self.hostname = hostname
		self.work_dir = "/tmp/%s" % self.name

		self._init()

		log("Waiting for work.")
	
	def test(self, id):
		"""
		Performs the testing of a particular mutant.

		Returns True if all tests pass, False if one fails.
		"""
		status = True
		test = self.fs.get(id)
		patch_file = test.read()
		log("Retrieved patch.")
		log("Executing operator %s on file %s." % (test.op, test.file_name))
		
		self._setup(patch_file)

		for test_name in self.settings["tests"]:
			if not self._run_test_case(test_name):
				print("%s failed." % test_name)
				status = False
				break

		self._teardown(patch_file)
		return status

	def _setup(self, patch_file):
		"""
		Cleans up, applies patch.
		"""
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
			raise Exception()
	
	def _run_test_case(self, test_name):
		"""
		Runs the specified test case on the current copy of the code.
		
		Returns True on success and False on failure.
		"""
		return Popen(["java", "-cp", self.settings["paths"]["classpath"], self.settings["commands"]["test"], test_name], stdin=PIPE, stdout=PIPE, stderr=PIPE).wait() == 0
	
	def _teardown(self, patch_file):
		"""
		Reverses patch.
		"""
		chdir(join(self.work_dir, self.settings["source"]["dir"]))
		reverse_patch(patch_file)
		chdir(self.work_dir)
		log("Reversed patch.")
	
	def _init(self):
		mkdir_p(self.work_dir)
		log("Created working directory.")

		# Load settings from the specified hostname.
		u = urlopen("http://%s/client.settings" % self.hostname)
		self.settings = loads(u.read().decode("utf-8"))
		log("Loaded client.settings.")

		self.fs = FileStore(self.settings["database"]["name"])
		log("Initialized storage.")

		u = urlopen(self.settings["source"]["location"])
		f = open(self.settings["source"]["name"], "wb")
		f.write(u.read())
		log("Downloaded source file.")

		z = ZipFile(self.settings["source"]["name"])
		z.extractall(self.work_dir)
		log("Extracted source file.")

		chdir(self.work_dir)
		log("Moved into work directory.")

		for cmd in self.settings["commands"]["preprocess"]:
			self._exec_command_quiet(cmd)
		log("Executed pre-processing commands.")

	def _exec_command_quiet(self, cmd):
		p = Popen(cmd, stdout=open("/dev/null"), shell=True)
		return p.wait() == 0

	def _clean(self):
		if self._exec_command_quiet(self.settings["commands"]["clean"]):
			log("Cleaned project.")
		else:
			raise Exception()
	
	def __del__(self):
		#rmtree(self.work_dir)
		pass
		#log("Removed working directory.")

if __name__ == "__main__":
	if len(sys.argv) == 2:
		s = Slave(sys.argv[1])
		s.test("4d0eb50bf7af9916ed000026")
	else:
		raise ValueError("Usage:  %s %s <hostname>" % (sys.executable, sys.argv[0]))
