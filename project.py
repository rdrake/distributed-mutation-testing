from os import walk, sep
from os.path import join, splitext, relpath, pathsep

class Project:
	def __init__(self, source_path, test_path, mutants=None):
		self.source_path = source_path
		self.test_path = test_path
		self.tests = []

		# Too long to put in the __init__ arguments.
		if not mutants:
			self.mutants = {
				"ASK": True,
				"ASTK": True,
				"EAN": True,
				"EELO": True,
				"ELPA": True,
				"ESP": True,
				"EXCR": True,
				"MBR": True,
				"MSF": True,
				"MSP": True,
				"MXC": True,
				"MXT": True,
				"RCXC": True,
				"RFU": True,
				"RJS": True,
				"RNA": True,
				"RSB": True,
				"RSK": True,
				"RSTK": True,
				"RTXC": True,
				"RVK": True,
				"RXO": True,
				"SHCR": True,
				"SKCR": True,
				"SPCR": True
			}
		else:
			self.mutants = mutants
	
	def source_files(self):
		"""
		Finds all source files ending in .java.
		"""
		for (dirpath, dirnames, filenames) in walk(self.source_path):
			for filename in filenames:
				if splitext(filename)[-1] == ".java":
					print(join(dirpath, filename))
	
	def test_names(self):
		"""
		Finds all test cases within the specified test path.  It does this by
		looking for .class files, and massaging the absolute path into the
		relative java.path.style.
		"""
		self.tests = []

		for (dirpath, dirnames, filenames) in walk(self.test_path):
			for filename in filenames:
				split = splitext(filename)

				if split[-1] == ".class":
					abs_path = join(dirpath, split[0])

					if "$" in abs_path: continue

					rel_path = abs_path.replace(self.test_path, "")
					test_name = rel_path.replace(sep, ".")

					if test_name in self.tests: continue

					yield(test_name)

if __name__ == "__main__":
	p = Project("/home/rdrake/workspace/junit/src/main/java/", "/home/rdrake/workspace/junit/target/test/java/")
	
	for test_name in p.test_names():
		print(test_name)
