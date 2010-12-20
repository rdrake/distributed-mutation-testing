from mpi4py import MPI

import sys

comm = MPI.COMM_SELF.Spawn(sys.executable, args=["worker.py"], maxprocs=1)


