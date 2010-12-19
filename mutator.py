from os.path import dirname, join, relpath
from subprocess import Popen, PIPE

from project import Project
from storage import FileStore
from util import diff, mkdir_p

out_dir = "/home/rdrake/workspace/distributed-mutation-testing/build"

class Mutator:
	def __init__(self, project):
		self.project = project
		self.store = FileStore("mutants")
	
	def mutate(self):
		for src_file in self.project.source_files():
			original_path = join(self.project.settings["source_path"], src_file)
			mutant_path = join(out_dir, src_file)
			mkdir_p(dirname(mutant_path))

			for (op, invoke) in self.project.settings["mutants"].items():
				if invoke:
					p = Popen(["txl", original_path, join("vendor", "conman", "%s.Txl" % op)], stdout=open(mutant_path, "w"), stderr=open("/dev/null"))

					print(self.store.put(diff(relpath(original_path), relpath(mutant_path)), op, src_file))

if __name__ == "__main__":
	p = Project("junit.settings")
	m = Mutator(p)
	m.mutate()
