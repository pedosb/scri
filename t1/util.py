# vim: set fileencoding=utf-8 :
import signal

INTERACTIVE = False
TIMEOUT = 5 # segundos ou 0 para desativar

#http://programming-guides.com/python/timeout-a-function
class TimeoutException(Exception):
	pass
def timeout_handler(signum, frame):
	raise TimeoutException()

# Chamada quando a entrada acaba
class InputEnd(Exception):
	pass

def read_sample(input_file):
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

def print_caudal(caudal, conf, suppress_confidence=False):
	if suppress_confidence:
		print '%f' % (caudal)
	else:
		print '%f, %f' % (caudal, conf)
