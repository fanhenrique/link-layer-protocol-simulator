import socket
import sys
import hashlib
import random
import logging
import argparse

ENCODE = 'utf-8'
HOST = '10.0.0.1'
HOST_CLIENT = '10.0.0.2'
PORT = 65432

TIME_FORMAT = '%Y-%m-%d,%H:%M:%S'
DEFAULT_LOG_LEVEL = logging.INFO

def main():
	
	parser = argparse.ArgumentParser(description='laboratorio')

	parser.add_argument("--fault", "-pf", help="probability of fault", type=float)
	
	help_msg = "Logging level (INFO=%d DEBUG=%d)" % (logging.INFO, logging.DEBUG)
	parser.add_argument("--log", "-l", help=help_msg, default=DEFAULT_LOG_LEVEL, type=int)

	args = parser.parse_args()

	if args.log == logging.DEBUG:
		logging.basicConfig(format='%(asctime)s %(levelname)s {%(module)s} [%(funcName)s] %(message)s', datefmt=TIME_FORMAT, level=args.log)
	else:
		logging.basicConfig(format='%(asctime)s %(message)s', datefmt=TIME_FORMAT, level=args.log)

	args = parser.parse_args()

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	s.bind((HOST, PORT))
	s.connect((HOST_CLIENT, PORT))

	logging.info('Recebido:')

	data = ''
	while True:
		
		recv  = s.recv(1024).decode(ENCODE)

		if not recv:
			break

		h, frame, seq = recv.split('#')

		if random.random() < args.fault: # chance de não responder
			continue
		else:

			hFrame = hashlib.md5(str(frame).encode(ENCODE)).hexdigest()
			
			if h == hFrame:
				logging.info('{} == {} {} {}'.format(h, hFrame, frame , seq))

				data += frame	
				s.send(bytes('ack#'+str(seq), ENCODE))
			else:
				logging.info('{} != {} {} {}'.format(h, hFrame, frame , seq))
				s.send(bytes('nack#'+str(seq), ENCODE))	


	logging.info('Enviado: {}'.format(data))

	s.send(bytes(data, ENCODE))

	s.close()

if __name__ == '__main__':
	main()