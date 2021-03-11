from mininet.topo import Topo
from mininet.node import Host
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
import shlex

import sys
import os
import argparse
import logging
import subprocess
import numpy as np

DEFAULT_COUNT = 1
DEFAULT_BW_MBPS = 1
DEFAULT_SIZE_MESSAGE = [10]
DEFAULT_SIZE_FRAME = [2]
DEFAULT_PF = 0.0 #falha
DEFAULT_PL = 0.0 #perda 	


DEFAULT_SWITCHES = 1
DEFAULT_DELAYS = 0

TIME_FORMAT = '%Y-%m-%d,%H:%M:%S'
DEFAULT_LOG_LEVEL = logging.INFO


def main():

	parser = argparse.ArgumentParser(description='laboratorio')

	parser.add_argument("--count", "-c", help="number of executions", default=DEFAULT_COUNT, type=int)
	parser.add_argument("--mbps", "-b", help="Bandwidth (mbps)", default=DEFAULT_BW_MBPS, type=int)
	parser.add_argument("--switches", "-s", help="number of switches", default=DEFAULT_SWITCHES, type=int)
	parser.add_argument("--delays", "-d", help="list of deleys", default=DEFAULT_DELAYS, type=int)
	parser.add_argument("--listmessages", "-lm", nargs='+', help="list size message", default=DEFAULT_SIZE_MESSAGE, type=int)
	parser.add_argument("--listframes", "-lf", nargs='+', help="list size frame", default=DEFAULT_SIZE_FRAME, type=int)
	parser.add_argument("--fault", "-pf", help="probability of fault", default=DEFAULT_PF, type=float)
	parser.add_argument("--loss", "-pl", help="probability of loss", default=DEFAULT_PL, type=float)

	args = parser.parse_args()
	
	help_msg = "Logging level (INFO=%d DEBUG=%d)" % (logging.INFO, logging.DEBUG)
	parser.add_argument("--log", "-l", help=help_msg,  default=DEFAULT_LOG_LEVEL, type=int)

	args = parser.parse_args()

	
	if args.log == logging.DEBUG:
		logging.basicConfig(format='%(asctime)s %(levelname)s {%(module)s} [%(funcName)s] %(message)s', datefmt=TIME_FORMAT, level=args.log)

	else:
		logging.basicConfig(format='%(asctime)s %(message)s', datefmt=TIME_FORMAT, level=args.log)

	args = parser.parse_args()


	for m in args.listmessages:
		for f in args.listframes:
			for loss in np.arange(0.0, 1.0, args.loss):
				for i in range(args.count):
					cmd = 'sudo python3 experimento.py --mbps %d --delay %d --switches %d --message %d --frame %d --fault %f --loss %f' % (args.mbps, args.delays, args.switches, m, f, args.fault, loss)
					param = shlex.split(cmd)
					logging.info("Param: {}".format(" ".join(param)))
					subprocess.call(param)


if __name__ == '__main__':
	main()