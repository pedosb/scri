#!/usr/bin/env python

import sys, signal, math
import scipy.integrate

TIMEOUT = 5 # segundos ou 0 para desativar
INTERACTIVE = False

#http://programming-guides.com/python/timeout-a-function
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

def convert_volt_to_degree(volts):
	w = 456.0
	s = volts
	y = 0.104
	z = 0.01
	k = 5.21
	t = -w * math.log(1 - (s*y-z) / k)
	return t

def get_ts(t1, t2):
	if t1 == None:
		return t2
	elif t2 == None:
		return t1
	p1 = 0.978
	p2 = 1.013
	return (t1*p1 + t2*p2) / (p1+p2)

def get_caudal(ts):
	e = [float(45) - tsi for tsi in ts]
	kc = 0.495
	ti = float(117)
	c = float(500) * kc * ( e[len(e)-1] + (1/ti) * scipy.integrate.trapz(e) )
	return c

if __name__=='__main__':
	if len(sys.argv) != 1:
		usage(sys.argv)
		exit(-1)
#	print get_ts(1,1)
#	print get_ts(10,0)
#	print get_ts(0,10)
#	print get_ts(None,9)
#	print get_ts(8,None)
	print \
	get_caudal([1,2,3,4,3,2,3,2,3,4,20,39,10,45,46,45,45,46,46,45,45,45,45,45,45,45,45,45,45,45,45,45,40,40,40,40,40,40,40,40,40,40,40,40,40])
	while True:
		value = read_sensor_sample(sys.stdin).strip()
		if value == '':
			break
		volts = parse_sensor_input(value)
		if volts[0] != None:
			print volts, convert_volt_to_degree(volts[1])
