from json import load
from os import sep, walk
from os.path import basename, join, splitext, relpath

class Project:
	def __init__(self, settings_path):
		self.name = basename(settings_path)

		with open(settings_path, "r", encoding="utf-8") as settings_file:
			self.settings = load(settings_file)

	def source_files(self):
		"""
		Finds all source files ending in .java.
		"""
		for (dirpath, dirnames, filenames) in walk(self.settings["source_path"]):
			for filename in filenames:
				if splitext(filename)[-1] == ".java":
					yield(join(dirpath, filename).replace(self.settings["source_path"], ""))
	
	def test_names(self):
		"""
		Finds all test cases within the specified test path.  It does this by
		looking for .class files, and massaging the absolute path into the
		relative java.path.style.
		"""
		self.tests = []

		for (dirpath, dirnames, filenames) in walk(self.settings["test_path"]):
			for filename in filenames:
				split = splitext(filename)

				if split[-1] == ".class":
					abs_path = join(dirpath, split[0])

					# Remove inner classes from the list of tests.
					if "$" in abs_path: continue

					rel_path = abs_path.replace(self.settings["test_path"], "")
					test_name = rel_path.replace(sep, ".")

					if test_name in self.tests: continue

					yield(test_name)

if __name__ == "__main__":
	p = Project("junit.settings")
	
	for test_name in p.test_names():
		print(test_name)
	
	for source_file in p.source_files():
		print(source_file)
