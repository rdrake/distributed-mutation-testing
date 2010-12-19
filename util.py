import os, errno

from os import walk
from os.path import join
from subprocess import Popen, PIPE
from zipfile import ZipFile, ZIP_DEFLATED

# Shamelessly stolen from SO:
#  http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc:
		if exc.errn == errno.EEXIST:
			pass
		else: raise

def zip(name, src_path):
	with ZipFile(name, "w", ZIP_DEFLATED) as z:
		for (dirpath, dirnames, filenames) in walk(src_path):
			for filename in filenames:
				full_path = join(dirpath, filename)
				rel_path = full_path.replace(src_path, "")
				z.write(full_path, rel_path)

def unzip(name, dest_path):
	with ZipFile(name, "r", ZIP_DEFLATED) as z:
		z.extractall(dest_path)

def diff(fst_file, snd_file):
	"""
	Executes the 'diff' command and captures the output.
	"""
	p = Popen(["diff", "-uwB", "--speed-large-files", fst_file, snd_file],
		stdin=PIPE, stdout=PIPE)
	return p.communicate()[0]
	#return [str(x) for x in p.stdout.readlines()]

def patch(patch_file):
	return _patch(patch_file, ["patch", "-p0"])

def reverse_patch(patch_file):
	return _patch(patch_file, ["patch", "-R", "-p0"])

def _patch(patch_file, args):
	"""
	Patches a file given the appropriate arguments.
	"""
	p = Popen(args, stdin=PIPE, stdout=PIPE)
	return p.communicate(input=patch_file)[1] is None

if __name__ == "__main__":
	print(patch(diff("junit/framework/TestResult.java.a", "junit/framework/TestResult.java.b")))
