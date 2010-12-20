from os.path import dirname, join, relpath
from subprocess import Popen, PIPE
from time import time

from project import Project
from storage import FileStore
from util import diff, mkdir_p

out_dir = "/home/rdrake/workspace/distributed-mutation-testing/build"

class Mutator:
	"""
	Generates all possible combinations of mutants.
	"""
	def __init__(self, project):
		self.project = project
		self.store = FileStore("mutants")
	
	def mutate(self):
		"""
		Performs the mutation.  Applies mutation operator to each source file,
		then stores a diff between the original and mutated file.

		# mutants = # source files x # mutation operators
		"""
		count = 0
		start = time()

		for src_file in self.project.source_files():
			original_path = join(self.project.settings["source_path"], src_file)
			mutant_path = join(out_dir, src_file)
			mkdir_p(dirname(mutant_path))

			for (op, invoke) in self.project.settings["mutants"].items():
				if invoke:
					p = Popen(["txl", original_path, join("vendor", "conman", "%s.Txl" % op)], stdout=open(mutant_path, "w"), stderr=open("/dev/null"))
					self.store.put(diff(relpath(original_path), relpath(mutant_path)), op, src_file)
					count += 1

					if count % 1000 == 0:
						print("Generated %d mutants.  Elapsed time %.02f seconds." % (count, (time() - start)))

		stop = time()
		print("Generated %d mutants in %d seconds." % (count, (stop - start)))

if __name__ == "__main__":
	p = Project("junit.settings")
	m = Mutator(p)
	m.mutate()
