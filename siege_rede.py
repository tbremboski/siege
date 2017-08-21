import sys, json, copy, time, socket, random
MAX_DEPTH = 3
UDP_IP = "127.0.0.1"
UDP_PORT_VERMELHO = 5001
UDP_PORT_AMARELO = 5002
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def envia_msg(msg, porta):
	sock.sendto(msg.encode('utf-8'), (UDP_IP, porta))

def recebe():
	while True:
		data, addr = sock.recvfrom(1024)
		print data
		if(data!='' and data!='conectado' and data!='fim' and data!='ok'):
			return decode_msg(data)
		elif(data=='fim'):
			return 'fim'
		else:
			return None

def decode_msg(mensagem):
	print "Mensagem Recebida "+str(mensagem)
	msg = mensagem.split()
	if("captura" in msg):
		return [msg[1],[msg[3],msg[5]]]
	else:
		return [msg[1],[msg[3],'']]

def formata_msg(msg):
	m = msg.split()

	

def load_map(filename):
	with open(filename) as data_file:    
		data = json.load(data_file)
	
	return data

vizinhos = load_map('vizinhos.json')
capturas = load_map('capturas.json')

def is_final(estado):
	if 'h1' in estado.pos_vermelhas:
		return True
	elif estado.pos_vermelhas.count(None) == len(estado.pos_vermelhas):
		return True
	else:
		return False

def h(estado, vermelho):
	pa = len(estado.pos_amarelas) - estado.pos_amarelas.count(None)
	pv = len(estado.pos_vermelhas) - estado.pos_vermelhas.count(None)

	sumv = 0.0
	suma = 0.0
	for pos in estado.pos_vermelhas:
		if pos is not None:
			sumv += (ord(pos[0]) - 96)
	for pos in estado.pos_amarelas:
		if pos is not None:
			suma += (ord(pos[0]) - 96)
	sumv /= pv
	suma /= pa

	if 'h1' in estado.pos_amarelas:
		h1 = 1
	else:
		h1 = 0

	ha = (pa - pv)*10.0 + h1*1.0 + suma*2.0
	hv = (pv - pa)*10.0 - h1*1.0 + sumv*2.0
	
	if vermelho:
		return hv
	else:
		return ha

def minimax(estado, depth, maximize, alpha, beta, vermelho):
	if depth == MAX_DEPTH or is_final(estado):
		return h(estado, vermelho)

	if maximize:
		best = -sys.maxint
		children = get_children(estado, vermelho)

		for child in children:
			v = minimax(child, depth+1, False, alpha, beta, vermelho)
			best = max(best, v)

			if best >= beta:
				return beta
			else:
				alpha = max(best, alpha)

	else:
		best = sys.maxint
		children = get_children(estado, not vermelho)

		for child in children:
			v = minimax(child, depth+1, True, alpha, beta, vermelho)
			best = min(best, v)

			if best <= alpha:
				return alpha
			else:
				beta = min(best, beta)

	return best

def get_children(estado, vermelho):
	r = []

	if vermelho:
		for i in range(len(estado.pos_vermelhas)):
			peca = estado.pos_vermelhas[i]
			if peca is not None:
				cap = capturas[peca]
				for c in cap:
					if c[1] in estado.pos_amarelas:
						novo_estado = copy.deepcopy(estado)
						novo_estado.pos_vermelhas[i] = c[2]
						novo_estado.pos_amarelas[novo_estado.pos_amarelas.index(c[1])] = None
						r.append(novo_estado)

				for v in vizinhos[peca]:
					if v not in estado.pos_vermelhas:
						if v not in estado.pos_amarelas:
							novo_estado = copy.deepcopy(estado)
							novo_estado.pos_vermelhas[i] = v
							r.append(novo_estado)

	else:
		for i in range(len(estado.pos_amarelas)):
			peca = estado.pos_amarelas[i]
			if peca is not None:
				cap = capturas[peca]
				for c in cap:
					if c[1] in estado.pos_vermelhas:
						novo_estado = copy.deepcopy(estado)
						novo_estado.pos_amarelas[i] = c[2]
						novo_estado.pos_vermelhas[novo_estado.pos_vermelhas.index(c[1])] = None
						r.append(novo_estado)

				for v in vizinhos[peca]:
					if v not in estado.pos_amarelas:
						if v not in estado.pos_vermelhas:
							novo_estado = copy.deepcopy(estado)
							novo_estado.pos_amarelas[i] = v
							r.append(novo_estado)

	return r

def turno_maquina(estado_atual, vermelho, alpha, beta):
	values = []
	children = get_children(estado_atual, vermelho)
	for i in range(len(children)):
		values.append(minimax(children[i], 0, False, alpha, beta, vermelho))

	max_value = max(values)
	indices = [i for i, x in enumerate(values) if x == max_value]
	max_index = random.randint(0, len(indices) - 1)

	estado_atual = copy.deepcopy(children[max_index])

	msg = ''
	for i in range(len(old_list)):
		if vermelho:
			if old_list[i] != estado_atual.pos_vermelhas[i]:
				print "De: " + str(old_list[i])
				print "Para: " + str(estado_atual.pos_vermelhas[i])
				msg = str(old_list[i]) + ' ' + str(estado_atual.pos_vermelhas[i])
		else:
			if old_list[i] != estado_atual.pos_amarelas[i]:
				print "De: " + str(old_list[i])
				print "Para: " + str(estado_atual.pos_amarelas[i])
				msg = str(old_list[i]) + ' ' + str(estado_atual.pos_amarelas[i])

	return estado_atual, msg

def jogo(estado, jogador):
	alpha = -sys.maxint
	beta = sys.maxint
	vermelho = True
	estado_atual = copy.deepcopy(estado)

	while not is_final(estado_atual):
		if vermelho:
			print "\nTurno vermelho!"
		else:
			print "\nTurno amarelo!"
			
		if jogador:
			if vermelho:
				num_old = estado_atual.pos_amarelas.count(None)
				old_list = copy.deepcopy(estado_atual.pos_vermelhas)
			else:
				num_old = estado_atual.pos_vermelhas.count(None)
				old_list = copy.deepcopy(estado_atual.pos_amarelas)

			estado_atual, msg = turno_maquina(estado_atual, vermelho, alpha, beta)

			if vermelho:
				envia_msg(formata_msg(msg), UDP_PORT_VERMELHO)
			else:
				envia_msg(formata_msg(msg), UDP_PORT_AMARELO)
			recebe()

			if vermelho:
				num_new = estado_atual.pos_amarelas.count(None)
			else:
				num_new = estado_atual.pos_vermelhas.count(None)

			if num_old < num_new:
				estado_atual = massacre(estado_atual, vermelho)

			

		else:
			result = recebe()
			if result != 'fim' and result != None:
				print result
			break

		vermelho = not vermelho
		jogador = not jogador

	if vermelho:
		print "Exercito vermelho venceu!"
	else:
		print "Exercito amarelo venceu!"

def massacre(estado, vermelho):
	print "Captura realizada!"
	estado_retorno = estado
	if vermelho:
		for pv in estado_retorno.pos_vermelhas:
			if pv is not None:
				for cap in capturas[pv]:
					if cap[1] in estado_retorno.pos_amarelas:
						if cap[2] not in estado_retorno.pos_vermelhas:
							if cap[2] not in estado_retorno.pos_amarelas:
								estado_retorno.pos_amarelas[estado_retorno.pos_amarelas.index(cap[1])] = None
								estado_retorno.pos_vermelhas[estado_retorno.pos_vermelhas.index(pv)] = cap[2]
								estado_retorno = massacre(estado_retorno, vermelho)
	else:
		for pa in estado_retorno.pos_amarelas:
			if pa is not None:
				for cap in capturas[pa]:
					if cap[1] in estado_retorno.pos_vermelhas:
						if cap[2] not in estado_retorno.pos_vermelhas:
							if cap[2] not in estado_retorno.pos_amarelas:
								estado_retorno.pos_vermelhas[estado_retorno.pos_vermelhas.index(cap[1])] = None
								estado_retorno.pos_amarelas[estado_retorno.pos_amarelas.index(pa)] = cap[2]
								estado_retorno = massacre(estado_retorno, vermelho)

	return copy.deepcopy(estado_retorno)

def main(argv):
	jogador = None
	if len(argv) < 1:
		print "Informe a cor do jogador."
		sys.exit(0)
	else:
		if argv[0] == 'vermelho':
			jogador = True
		elif argv[0] == 'amarelo':
			jogador = False
		else:
			print "Informe uma cor: vermelho ou amarelo."
			sys.exit(0)
	
	# bind_sock(jogador)
	inicial = Estado(0)
	inicial.estado_inicial()

	if jogador:
		envia_msg('conecta', UDP_PORT_VERMELHO)
	else:
		envia_msg('conecta', UDP_PORT_AMARELO)
	recebe()

	jogo(inicial, jogador)

	return

class Estado:
	def __init__(self, movimentos):
		self.movimentos = movimentos
		self.pos_vermelhas = []
		self.pos_amarelas = []

	def estado_inicial(self):
		for i in range(1,17,2):
			tmp = 'd' + str(i)
			self.pos_vermelhas.append(tmp)

		for i in range(1,9):
			# tmp = 'f' + str(i)
			tmp2 = 'g' + str(i)
			# self.pos_amarelas.append(tmp)
			self.pos_amarelas.append(tmp2)

if __name__ == '__main__':
	main(sys.argv[1:])