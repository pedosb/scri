#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import sys, signal, math
import scipy.integrate
import logging

TIMEOUT = 5 # segundos ou 0 para desativar
INTERACTIVE = False
#Não pode mudar pois os coeficientes de get_ts dependem dele
N_SENSORS = 2

#http://programming-guides.com/python/timeout-a-function
class TimeoutException(Exception):
	pass
def timeout_handler(signum, frame):
	raise TimeoutException()
# Chamada quando a entrada acaba
class InputEnd(Exception):
	pass

class SensorOutOfOrder(Exception):
	"""
	Ocorre quando o sensor lido após o sensor i não é o sensor i+1
	"""
	pass

def usage(argv):
	print '%s < <sensor_file_name>' % argv[0]
	print ('<sensor_file_name> file with samples of the temperature sensors'+
			'one per line')

def calc_flow(input_file = sys.stdin):
	logging.basicConfig(level=logging.WARNING)
	i=0
	#Para reset
	while True:
		#[t][sensor_id] = value
		sensors_value = []
		ts_value = []
		n_sensors = N_SENSORS
		i = i +1
		if i == 10:
			break
		try:
			while True:
				t = len(sensors_value)
				value = 10
				try:
					value = read_sensors(input_file, n_sensors)
				except SensorOutOfOrder, e:
					#reset
					logging.critical(e)
					logging.critical('Reiniciando...')
					print 'fail'
					break
				except InputEnd:
					logging.critical('Fim do arquivo de entrada saindo...')
					exit(0)
				else:
					sensors_value.append(value)
				try:
					ts_value.append(convert_volt_to_degree(get_ts(sensors_value[t])))
				# Nenhum sensor lido
				except ValueError, e:
					logging.critical(e)
					print 'fail'
					break
				print get_caudal(ts_value)
		except Exception, e:
			logging.exception(e)
			print 'fail'

def read_sensors(input_file, n_sensors):
	"""
	Retorna uma lista com os sensores lidos onde o index é o sensor_id
	Uma leitura None representa um valor omisso (timeout)
	Lança SensorOurOfOrder se:
		O sensor lido não for o esperado, caso o id não possa ser identificado
		assume-se que esse está "certo" e retorna None como leitura.
	Lança InputEnd se:
		A entrada for ''
	"""
	sensors_value_t = ([None for i in range(n_sensors)])
	for si in range(len(sensors_value_t)+1)[1:]:
		try:
			value = read_sensor_sample(input_file)
		# Ignora a "entrada" do sensor
		except TimeoutException:
			read_si = si
			value = None
		else:
			# No final do arquivo retorna '' se for uma avaria retornaria '\n'
			if value == '':
				raise InputEnd()
			try:
				err = False
				read_si, value = parse_sensor_input(value)
			except ValueError, e:
				logging.critical(e)
				err = True
			except SyntaxError, e:
				logging.critical(e)
				err = True
			finally:
				# Se algum erro de sintaxe consideramos a entrada do sensor na ordem
				if err:
					read_si = si
					value = None
		# Quando o sensor 'None' é lido será considerada uma avaria e seu valor
		#também deverá ser 'None'
		if read_si == None:
			value = None
		# Sensor lido não é o esperado
		elif read_si != si:
			raise SensorOutOfOrder("Esperando sensor '%s' porém o sensor" % si +
					" '%s' foi encontrado" % read_si)
		sensors_value_t[si-1] = value
	return sensors_value_t

def read_sensor_sample(input_file):
	"""
	Lê uma linha de input_file e a retorna.
	Lança TimeoutException caso a leitura exceda TIMEOUT.
	"""
	old_handler = signal.signal(signal.SIGALRM, timeout_handler) 
	signal.alarm(TIMEOUT)
	value = None
	try: 
		if INTERACTIVE:
			print "Leitura de sensor: "
		value = input_file.readline()
	finally:
		signal.signal(signal.SIGALRM, old_handler) 
	signal.alarm(0) # Desativar alarme
	return value

def parse_sensor_input(line):
	"""
	<line> deve ser uma string do tipo 'S_i d.ccc'
	Retorna 'None, None' se:
	(Lança ValueError)
		'd.ccc' não estiver prorpiamente formatado ou fora do intervalo válido
	(Lança SyntaxError)
		'S_i' não estiver prorpriamente formatado
		Um erro qualquer que impessa a interpretação de <line> aconteça
	"""
	try:
		try:
			sensor_id_str, value = line.strip().split()
		# Tentar detectar uma entrada nula
		except ValueError:
			sensor_id_str = line.strip()
			value = None
		if sensor_id_str.startswith('S_'):
			try:
				sensor_id = int(sensor_id_str.split('_')[1])
			except Exception, e:
				raise SyntaxError('Não foi possível indentificar o <sensor_id> ' +
						"na entrada '%s'" % line)

			try:
				d, f = value.split(',')
			except AttributeError, e:
				logging.debug("Sensor '%s' não apresentou entrada" % sensor_id)
				return sensor_id, None
			except ValueError, e:
				raise ValueError("Valor do sensor '%s' não está " % sensor_id +
				'propriamente formatado')

			if len(d) > 2:
				raise ValueError("Parte inteira do sensor '%s' maior que 2" %
						sensor_id)
			if len(f) != 3:
				raise ValueError("Parte complementar do sensor '%s' maior que 3"
							% sensor_id)

			if not d.isdigit() or not f.isdigit():
				raise ValueError("Valor do sensor '%s' não composto por digitos"
						% sensor_id)
			value = float('%d.%d' % (int(d),int(f)))
			min_value = 0
			max_value = 10
			if value >= min_value and value <= max_value:
				return sensor_id, value
			else:
				raise ValueError("Leitura do sensor '%s' fora do intervalo [%s,%s]" %
						(sensor_id, min_value, max_value))
		else:
			raise Exception()
	except ValueError, e:
		raise e
	except SyntaxError, e:
		raise e
	except Exception, e:
		logging.exception(e)
		raise SyntaxError('Leitura do sensor não está propriamente formatada')
	return None, None

def convert_volt_to_degree(volts):
	w = 456.0
	s = volts
	y = 0.104
	z = 0.01
	k = 5.21
	t = -w * math.log(1 - (s*y-z) / k)
	return t

def get_ts(temp):
	"""
	t must have lenght 2
	Lança ValueError
	"""
	if temp == [None for i in range(len(temp))]:
		raise ValueError('Nehum sensor pode ser lido')
	if len(temp) != 2:
		raise ValueError("Menos de um sesnor para obter 'ts'")
	t1 = temp[0]
	t2 = temp[1]
	if t1 == None:
		return t2
	elif t2 == None:
		return t1
	p1 = 0.978
	p2 = 1.013
	return (t1*p1 + t2*p2) / (p1+p2)

def get_caudal(ts):
	"""
	Lança ValueError se:
		ts não tiver nenhum valor
	"""
	if len(ts) < 1:
		raise ValueError("'ts' deve conter pelo menos um valor")
	e = [float(45) - tsi for tsi in ts]
	kc = 0.495
	ti = float(117)
	c = float(500) * kc * ( e[len(e)-1] + (scipy.integrate.trapz(e, dx=3)/ti) )
	return c

if __name__=='__main__':
	if len(sys.argv) != 1:
		usage(sys.argv)
		exit(-1)
	calc_flow()
	exit(0)
#	print get_ts(1,1)
#	print get_ts(10,0)
#	print get_ts(0,10)
#	print get_ts(None,9)
#	print get_ts(8,None)
	print \
#	get_caudal([1,2,3,4,3,2,3,2,3,4,20,39,10,45,46,45,45,46,46,45,45,45,45,45,45,45,45,45,45,45,45,45,40,40,40,40,40,40,40,40,40,40,40,40,40])
#	while True:
#		value = read_sensor_sample(sys.stdin).strip()
#		if value == '':
#			break
#		volts = parse_sensor_input(value)
#		if volts[0] != None:
#			print volts, convert_volt_to_degree(volts[1])
