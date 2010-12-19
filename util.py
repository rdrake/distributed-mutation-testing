import os, errno

# Shamelessly stolen from SO:
#  http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc:
		if exc.errn == errno.EEXIST:
			pass
		else: raise
