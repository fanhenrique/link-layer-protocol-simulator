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

import sys
import os
import argparse
import logging

TIME_FORMAT = '%Y-%m-%d,%H:%M:%S'
DEFAULT_LOG_LEVEL = logging.INFO

class TopoBasica(Topo):

	def __init__(self, bw_mbps, delay_ms, switches):
		Topo.__init__(self)

		logging.info('*** Adiciona hosts\n')
		h1 = self.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
		h2 = self.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)

		logging.info('*** Adiciona links\n')
		
		link_parametros = {'delay': '%dms' % delay_ms, 'bw': bw_mbps, 'loss': 0}
		
		logging.info('*** Adiciona switches e links\n')
		logging.info("parametros: {}".format(link_parametros))

		for i in range(1, switches+1):
			switch_atual = self.addSwitch('s%d'%i)
			print("switch_atual: {}".format(switch_atual))
			if i == 1:
				print("\t add link h1 e switch_atual=s%d" % (i))
				self.addLink(h1, switch_atual, cls=TCLink, **link_parametros)
			else:
				print("\t add link switch_anterior=s%d e switch_atual=s%d"%(i-1, i))
				self.addLink(switch_anterior, switch_atual, cls=TCLink, **link_parametros)

			if i == switches:
				print("\t add link switch_atual=s%d e h2" % (i))
				self.addLink(switch_atual, h2, cls=TCLink, **link_parametros)

			switch_anterior = switch_atual

def main():

	parser = argparse.ArgumentParser(description='laboratorio')

	parser.add_argument("--mbps", "-b", help="Bandwidth (mbps)", type=int)
	parser.add_argument("--switches", "-s", help="number of switches", type=int)
	parser.add_argument("--delay", "-d", help="deleys", type=int)
	parser.add_argument("--message", "-m", help="size message", type=int)
	parser.add_argument("--frame", "-f", help="size frame", type=int)
	parser.add_argument("--fault", "-pf", help="probability of fault", type=float)
	parser.add_argument("--loss", "-pl", help="probability of loss", type=float)


	help_msg = "Logging level (INFO=%d DEBUG=%d)" % (logging.INFO, logging.DEBUG)
	parser.add_argument("--log", "-l", help=help_msg, default=DEFAULT_LOG_LEVEL, type=int)

	args = parser.parse_args()

	if args.log == logging.DEBUG:
		logging.basicConfig(format='%(asctime)s %(levelname)s {%(module)s} [%(funcName)s] %(message)s', datefmt=TIME_FORMAT, level=args.log)
	else:
		logging.basicConfig(format='%(asctime)s %(message)s', datefmt=TIME_FORMAT, level=args.log)

	args = parser.parse_args()

	logging.info("Configurando mininet...")

	start = time()

	topo = TopoBasica(bw_mbps=args.mbps, delay_ms=args.delay, switches=args.switches)

	net = Mininet(topo=topo, host=Host, link=TCLink)

	logging.info("Iniciando rede...")
	net.start()

	h1 = net.getNodeByName('h1')
	h2 = net.getNodeByName('h2')
	

	cmd1 = 'sudo python3 server.py --fault %f &>> out_server.txt &' % args.fault
	# cmd1 = 'ifconfig &> out_server.txt'
	logging.info("H1 cmd: %s" % cmd1)
	h1.cmd(cmd1)

	cmd2 = 'sudo python3 client.py --message %d --frame %d --loss %f &>> out_client.txt' % (args.message, args.frame, args.loss)
	# cmd2 = 'ifconfig &> out_client.txt'
	logging.info("H2 cmd: %s" % cmd2)
	h2.cmd(cmd2)
			      

	# if (args.message % args.frame) == 0:
	# 	for loss in numpy.arange(0.0, 1.0, args.loss):
	# 		for i in range(args.count):
	# 			cmd1 = 'sudo python3 server.py --fault %f &>> out_server.txt &' % args.fault
	# 			# cmd1 = 'ifconfig &> out_server.txt'
	# 			logging.info("H1 cmd: %s" % cmd1)
	# 			h1.cmd(cmd1)	

	# 			cmd2 = 'sudo python3 client.py --message %d --frame %d --loss %f &>> out_%d_%d_%f.txt' % (args.message, args.message, loss, args.message, args.message, loss)
	# 			# cmd2 = 'ifconfig &> out_client.txt'
	# 			logging.info("H2 cmd: %s" % cmd2)
	# 			h2.cmd(cmd2)
		



	logging.info("Fim experimento")
	net.stop()

	

if __name__ == '__main__':
	main()