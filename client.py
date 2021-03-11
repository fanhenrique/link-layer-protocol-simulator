import socket
import sys
import hashlib
import random
import argparse
import logging

import datetime
import time
import os

ENCODE = 'utf-8'
HOST = '10.0.0.2'
HOST_SERVER = '10.0.0.1'
PORT = 65432

TIME_FORMAT = '%Y-%m-%d,%H:%M:%S'
DEFAULT_LOG_LEVEL = logging.INFO

def frameCurrent(indexcurrent, date, tamFrame):
	msg = ''
	for i in range(tamFrame):
		if(indexcurrent+i < len(date)):
			msg += date[indexcurrent+i]

	return msg

def createError(tam):
	msg = ''
	for i in range(tam):
		msg += '*'
	return msg

def createMsg(tam):
	msg = ''
	for i in range(tam):
		msg += chr(random.randint(65, 90))

	return msg

def main():

	parser = argparse.ArgumentParser(description='laboratorio')

	parser.add_argument("--message", "-m", help="size message", type=int)
	parser.add_argument("--frame", "-f", help="size frame", type=int)
	parser.add_argument("--loss", "-pl", help="probability of loss", type=float)


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
	s.connect((HOST_SERVER, PORT))

	data = createMsg(args.message)
	error = createError(args.frame)

	logging.error('Enviado: {}'.format(data))

	countFrame = 0
	i = 0

	dirs1 = 'times_messages_'+str(args.message)
	
	if not os.path.exists(dirs1):
		os.makedirs(dirs1)

	dirs2 = 'frame_'+str(args.frame)

	if not os.path.exists(dirs1+'/'+dirs2):
		os.makedirs(dirs1+'/'+dirs2)		

	sFile = 'loss_'+str(args.loss)+'.txt'
	file = open(dirs1+'/'+dirs2+'/'+sFile, 'a+')

	time.sleep(1)

	time_begin = datetime.datetime.now()
	while i < len(data):

		frame = frameCurrent(i, data, args.frame)

		h = hashlib.md5(bytes(frame, ENCODE)).hexdigest()

		if random.random() < args.loss: # porcentagem de erro
			s.settimeout(None)
			
			logging.info('{} --- {:05d}'.format(error, countFrame, end=''))
			
			msg = h + '#' + error + '#' + '%05d'%countFrame
			s.send(bytes(msg, ENCODE))
		else:
			s.settimeout(None)

			logging.info('{} --- {:05d}'.format(frame, countFrame, end=''))
			
			msg = h + '#' + frame + '#' + '%05d'%countFrame
			s.send(bytes(msg, ENCODE))

		s.settimeout(1)	
		try:
			recv = s.recv(1024).decode(ENCODE)

			response, seq = recv.split('#')

			logging.info('{} {}'.format(response, seq))

			if response == 'nack':
				continue

			i += args.frame
			countFrame = int(seq) + 1
																																																																																																																																																																														
		except Exception as e:
			logging.info('exception: {}'.format(e))
			continue	

	s.send(b'')
	time_end = datetime.datetime.now()

	time_diff = (time_end - time_begin)
	time_diff_seconds = time_diff.seconds + (time_diff.microseconds/1000000.0)
	

	responseServer = s.recv(1024).decode(ENCODE)
	logging.info('Recebido: {}'.format(responseServer))

	file.write(str(args.frame)+' '+str(args.loss)+' '+str(time_diff_seconds)+'\n')

	logging.info("tempo_diferenca: {} [{}] seconds".format(time_diff, time_diff_seconds))

	s.close()

if __name__ == '__main__':
	main()