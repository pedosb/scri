#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import logging
import argparse

import numpy

MAX_DIFFERENCE = 5

from util import *

def main(pythonf, javaf):
	logging.basicConfig(level=logging.DEBUG)
	while True:
		try:
			#[tempo](pythonf, javaf)
			result = []
			while True:
				try:
					result.append((get_input(pythonf), get_input(javaf)))
					time = len(result) - 1
				except InputEnd:
					logging.debug('Final do arquivo, saindo...')
					return

				if result[time][0] == None and result[time][1] == None:
					logging.critical('Os dois programas falharam')
					print 'FAIL'
				elif result[time][1] == None:
					logging.debug('Programa Java falhou')
					print result[time][0], ', 75'
				elif result[time][0] == None:
					logging.debug('Programa Python falou')
					print result[time][1], ', 30'
				else:
					print vote(result)
		except Exception, e:
			logging.exception(e)
			print 'FAIL'

def vote(result):
	"""
	Assume que nenhum dos programas falharam para o tempo atual
	"""
	time = len(result) - 1
	if abs(result[time][1] - result[time][0]) > MAX_DIFFERENCE:
		logging.debug("Diferença maior que '%s'" % MAX_DIFFERENCE)
		return result[time][0], 70
	else:
		return numpy.mean(result[time]), 97

def get_input(input_file):
	try:
		value = read_sample(input_file).strip()
	except TimeoutException:
		return value
	if value == '':
		raise InputEnd()
	elif value == 'fail':
		return None
	value = float(value)
	return value

if __name__ == '__main__':
	parser = argparse.ArgumentParser('Votador para caudal')
	parser.add_argument('-p', '--python-output', required=True,
			help='Saída do programa Python (mais confiável)')
	parser.add_argument('-j', '--java-output', required=True,
			help='Saída do programa Java (menos confiável)')

	args = parser.parse_args()

	javaf = open(args.java_output)
	pythonf = open(args.python_output)

	main(pythonf, javaf)

	javaf.close()
	pythonf.close()
