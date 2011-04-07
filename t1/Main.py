#!/usr/bin/env python

import sys, signal

TIMEOUT = 5 # segundos ou 0 para desativar
INTERACTIVE = False

class TimeoutException(Exception):
	pass
def timeout_handler(signum, frame):
	raise TimeoutException()

def usage(argv):
	print '%s < <sensor_file_name>' % argv[0]
	print ('<sensor_file_name> file with samples of the temperature sensors'+
			'one per line')

def calc_flow(input_file = sys.stdin):
	pass

def read_sensor_sample(input_file):
	old_handler = signal.signal(signal.SIGALRM, timeout_handler) 
	signal.alarm(TIMEOUT)
	value = None
	try: 
		if INTERACTIVE:
			print "Leitura de sensor: "
		value = input_file.readline()
	except TimeoutException:
		value = None
	finally:
		signal.signal(signal.SIGALRM, old_handler) 
	signal.alarm(0) # Desativar alarme
	return value

def parse_sensor_input(line):
	"""
	line deve ser uma string do tipo 'S_i d.ccc'
	"""
	try:
		sensor_id, value = line.strip().split()
		if sensor_id.startswith('S_'):
			d, f = value.split(',')
			if len(d) > 2:
				raise ValueError('Parte inteira maior que 2')
			if len(f) != 3:
				raise ValueError('Parte complementar maior que 3')
			if not d.isdigit() or not f.isdigit():
				raise ValueError('Valor nao composto por digitos')
			value = float('%d.%d' % (int(d),int(f)))
			min_value = 0
			max_value = 10
			if value >= min_value and value <= max_value:
				return int(sensor_id.split('_')[1]), value
			else:
				raise ValueError('Leitura fora do intervalo [%s,%s]' %
						(min_value, max_value))
	except ValueError:
		pass
	except Exception:
		pass
	return None, None

if __name__=='__main__':
	if len(sys.argv) != 1:
		usage(sys.argv)
		exit(-1)
	while True:
		value = read_sensor_sample(sys.stdin).strip()
		if value == '':
			break
		print parse_sensor_input(value)