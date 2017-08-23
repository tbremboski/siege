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
		return [msg[1],msg[3],msg[5]]
	else:
		return [msg[1],msg[3]]

def formata_msg(msg):
	new_msg = ''
	m = msg.split()
	if len(m) > 2:
		new_msg = 'De ' + m[0] + ' para ' + m[1] + ' captura ' + m[2]
	else:
		new_msg = 'De ' + m[0] + ' para ' + m[1]

	return new_msg
	

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

def h(estado, vermelho, depth):
	md = MAX_DEPTH+1
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
	sumv /= (pv+1)
	suma /= (pa+1)

	if 'h1' in estado.pos_amarelas:
		h1_a = 1
	else:
		h1_a = 0

	if 'h1' in estado.pos_vermelhas:
		h1_v = 1
	else:
		h1_v = 0

	ha = (pa - pv)*200.0 + h1_a*5.0 + suma - h1_v*10000.0 + (md-depth)*1000 + (8-pv)*100
	hv = (pv - pa)*200.0 - h1_a*5.0 + sumv + h1_v*10000.0 + (md-depth)*1000
	
	if vermelho:
		# print "sumv: " + str(sumv)
		# print "h1: " + str(h1*1.0)
		# print "pecas: " + str((pv-pa)*10.0)
		# print "hv: " + str(hv)
		return hv
	else:
		# print "suma: " + str(suma)
		# print "h1: " + str(h1*1.0)
		# print "pecas: " + str((pa-pv)*10.0)
		# print "ha: " + str(ha)
		return ha

def minimax(estado, depth, maximize, alpha, beta, vermelho):
	if depth == MAX_DEPTH or is_final(estado[-1]):
		return h(estado[-1], vermelho, depth)

	if maximize:
		best = -sys.maxint
		children = get_children(estado[-1], vermelho)

		for child in children:
			v = minimax(child, depth+1, False, alpha, beta, vermelho)
			best = max(best, v)
			alpha = max(best, alpha)

			if beta <= alpha:
				break

		return best

	else:
		best = sys.maxint
		children = get_children(estado[-1], not vermelho)

		for child in children:
			v = minimax(child, depth+1, True, alpha, beta, vermelho)
			best = min(best, v)
			beta = min(best, beta)

			if beta <= alpha:
				break

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
						if c[2] not in estado.pos_vermelhas:
							if c[2] not in estado.pos_amarelas:
								tmp = []
								novo_estado = copy.deepcopy(estado)
								novo_estado.pos_vermelhas[i] = c[2]
								novo_estado.pos_amarelas[novo_estado.pos_amarelas.index(c[1])] = None
								tmp.append(novo_estado)
								n_e, _ = massacre(novo_estado, vermelho)
								tmp.extend(n_e)
								r.append(tmp)

				for v in vizinhos[peca]:
					if v not in estado.pos_vermelhas:
						if v not in estado.pos_amarelas:
							novo_estado = copy.deepcopy(estado)
							novo_estado.pos_vermelhas[i] = v
							r.append([novo_estado])

	else:
		for i in range(len(estado.pos_amarelas)):
			peca = estado.pos_amarelas[i]
			if peca is not None:
				cap = capturas[peca]
				for c in cap:
					if c[1] in estado.pos_vermelhas:
						if c[2] not in estado.pos_vermelhas:
							if c[2] not in estado.pos_amarelas:
								tmp = []
								novo_estado = copy.deepcopy(estado)
								novo_estado.pos_amarelas[i] = c[2]
								novo_estado.pos_vermelhas[novo_estado.pos_vermelhas.index(c[1])] = None
								tmp.append(novo_estado)
								n_e, _ = massacre(novo_estado, vermelho)
								tmp.extend(n_e)
								r.append(tmp)

				for v in vizinhos[peca]:
					if v not in estado.pos_amarelas:
						if v not in estado.pos_vermelhas:
							novo_estado = copy.deepcopy(estado)
							novo_estado.pos_amarelas[i] = v
							r.append([novo_estado])

	return r

def turno_maquina(estado_atual, vermelho, alpha, beta):
	values = []
	captura = False
	children = get_children(estado_atual, vermelho)
	for i in range(len(children)):
		values.append(minimax(children[i], 0, False, alpha, beta, vermelho))

	print "Valores: " + str(values)
	max_value = max(values)
	print "Heuristica: " + str(max_value)
	indices = [i for i, x in enumerate(values) if x == max_value]
	max_index = random.randint(0, len(indices) - 1)
	print "Indice: " + str(indices[max_index])

	if vermelho:
		num_old = estado_atual.pos_amarelas.count(None)
		old_list = copy.deepcopy(estado_atual.pos_vermelhas)
	else:
		num_old = estado_atual.pos_vermelhas.count(None)
		old_list = copy.deepcopy(estado_atual.pos_amarelas)

	estado_atual = copy.deepcopy(children[indices[max_index]][0])

	if vermelho:
		num_new = estado_atual.pos_amarelas.count(None)
	else:
		num_new = estado_atual.pos_vermelhas.count(None)

	if num_old < num_new:
		captura = True
	else:
		captura = False

	for i in range(len(old_list)):
		if vermelho:
			if old_list[i] != estado_atual.pos_vermelhas[i]:
				print "De: " + str(old_list[i])
				print "Para: " + str(estado_atual.pos_vermelhas[i])
				msg = str(old_list[i]) + ' ' + str(estado_atual.pos_vermelhas[i])
				if captura:
					for c in capturas[old_list[i]]:
						if estado_atual.pos_vermelhas[i] in c:
							print "Captura: " + c[1]
							msg = msg + ' ' + c[1]
		else:
			if old_list[i] != estado_atual.pos_amarelas[i]:
				print "De: " + str(old_list[i])
				print "Para: " + str(estado_atual.pos_amarelas[i])
				msg = str(old_list[i]) + ' ' + str(estado_atual.pos_amarelas[i])
				if captura:
					for c in capturas[old_list[i]]:
						if estado_atual.pos_amarelas[i] in c:
							print "Captura: " + c[1]
							msg = msg + ' ' + c[1]

	if vermelho:
		envia_msg(formata_msg(msg), UDP_PORT_VERMELHO)
	else:
		envia_msg(formata_msg(msg), UDP_PORT_AMARELO)
	recebe()

	if captura:
		ests, movs = massacre(estado_atual, vermelho)
	else:
		ests = []
		movs = []

	if vermelho:
		for m in movs:
			envia_msg(formata_msg(m), UDP_PORT_VERMELHO)
			recebe()
		envia_msg('fim', UDP_PORT_VERMELHO)
	else:
		for m in movs:
			envia_msg(formata_msg(m), UDP_PORT_AMARELO)
			recebe()
		envia_msg('fim', UDP_PORT_AMARELO)
	
	if len(ests) > 0:
		estado_atual = ests[-1]

	return estado_atual

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
			print estado_atual.pos_vermelhas if vermelho else estado_atual.pos_amarelas
			estado_atual = turno_maquina(estado_atual, vermelho, alpha, beta)
			# raw_input("Aperte enter")

		else:
			result = recebe()
			while result != 'fim' and result != None:
				if vermelho:
					estado_atual.pos_vermelhas[estado_atual.pos_vermelhas.index(result[0])] = result[1]
					if len(result) > 2:
						estado_atual.pos_amarelas[estado_atual.pos_amarelas.index(result[2])] = None
				else:
					estado_atual.pos_amarelas[estado_atual.pos_amarelas.index(result[0])] = result[1]
					if len(result) > 2:
						estado_atual.pos_vermelhas[estado_atual.pos_vermelhas.index(result[2])] = None
				result = recebe()

		vermelho = not vermelho
		jogador = not jogador

	if vermelho:
		print "Exercito amarelo venceu!"
	else:
		print "Exercito vermelho venceu!"

def massacre(estado, vermelho):
	# print "Captura realizada!"
	r = []
	mov = []
	comeu = False
	estado_retorno = copy.deepcopy(estado)
	if not is_final(estado_retorno):
		if vermelho:
			for pv in estado_retorno.pos_vermelhas:
				if pv is not None:
					for cap in capturas[pv]:
						if cap[1] in estado_retorno.pos_amarelas:
							if cap[2] not in estado_retorno.pos_vermelhas:
								if cap[2] not in estado_retorno.pos_amarelas:
									estado_retorno.pos_amarelas[estado_retorno.pos_amarelas.index(cap[1])] = None
									estado_retorno.pos_vermelhas[estado_retorno.pos_vermelhas.index(pv)] = cap[2]
									r.append(estado_retorno)
									msg = cap[0] + ' ' + cap[2] + ' ' + cap[1]
									mov.append(msg)
									e, m = massacre(estado_retorno, vermelho)
									r.extend(e)
									mov.extend(m)
									comeu = True
									break
				if comeu:
					break
		else:
			for pa in estado_retorno.pos_amarelas:
				if pa is not None:
					for cap in capturas[pa]:
						if cap[1] in estado_retorno.pos_vermelhas:
							if cap[2] not in estado_retorno.pos_vermelhas:
								if cap[2] not in estado_retorno.pos_amarelas:
									estado_retorno.pos_vermelhas[estado_retorno.pos_vermelhas.index(cap[1])] = None
									estado_retorno.pos_amarelas[estado_retorno.pos_amarelas.index(pa)] = cap[2]
									r.append(estado_retorno)
									msg = cap[0] + ' ' + cap[2] + ' ' + cap[1]
									mov.append(msg)
									e, m = massacre(estado_retorno, vermelho)
									r.extend(e)
									mov.extend(m)
									comeu = True
									break
				if comeu:
					break

	# print r, mov
	return r, mov

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
	
	# print capturas['d1']
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