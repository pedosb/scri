#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import logging
import argparse

import numpy

MAX_DIFFERENCE = 5

from util import *

def main(pythonf, javaf, suppress_confidence=False, verbose=False):
	if verbose:
		logging.basicConfig(level=logging.DEBUG)
	else:
		logging.basicConfig(filename='/dev/null')
	while True:
		try:
			#[tempo](pythonf, javaf)
			result = []
			conf = []
			while True:
				try:
					value = get_input(pythonf, True)
					pp = value[0]
					conf.append(value[1])
				except InputEnd:
					logging.debug('Final do arquivo Python, saindo...')
					return
				try:
					pj = get_input(javaf)[0]
				except InputEnd:
					logging.debug('Final do arquivo Java, saindo...')
					return
				result.append((pp, pj))
				time = len(result) - 1

				if result[time][0] == None and result[time][1] == None:
					logging.critical('Os dois programas falharam')
					print 'FAIL'
				elif result[time][1] == None:
					logging.debug('Programa Java falhou')
					print_caudal(result[time][0], get_confidence(75, conf[time]), suppress_confidence)
				elif result[time][0] == None:
					logging.debug('Programa Python falou')
					print_caudal(result[time][1], 30, suppress_confidence)
				else:
					print_caudal(*vote(result, conf), suppress_confidence=suppress_confidence)
		except Exception, e:
			logging.exception(e)
			print 'FAIL'

def get_confidence(voter, python):
	return voter * 0.65 + python * 0.35

def vote(result, conf):
	"""
	Assume que nenhum dos programas falharam para o tempo atual
	"""
	time = len(result) - 1
	if abs(result[time][1] - result[time][0]) > MAX_DIFFERENCE:
		logging.debug("Diferença maior que '%s'" % MAX_DIFFERENCE)
		return result[time][0], get_confidence(70,  conf[time])
	else:
		return numpy.mean(result[time]), get_confidence(97, conf[time])

def get_input(input_file, with_conf=False):
	try:
		value = read_sample(input_file).strip()
	except TimeoutException:
		return value, None
	if value == '':
		raise InputEnd()
	elif value == 'fail':
		return None, None
	if with_conf:
		value = value.split(',')
		return float(value[0]), float(value[1])
	else:
		value = float(value)
	return value, None

if __name__ == '__main__':
	parser = argparse.ArgumentParser('Votador para caudal')
	parser.add_argument('-p', '--python-output', required=True,
			help='Saída do programa Python (mais confiável)')
	parser.add_argument('-j', '--java-output', required=True,
			help='Saída do programa Java (menos confiável)')
	parser.add_argument('-s', '--suppress-confidence', action='store_true',
			help='Não mostrar a confiança na saída do votador')
	parser.add_argument('-v', '--verbose', action='store_true',
			help='Show log when running')

	args = parser.parse_args()

	javaf = open(args.java_output)
	pythonf = open(args.python_output)

	main(pythonf, javaf, args.suppress_confidence, args.verbose)

	javaf.close()
	pythonf.close()
