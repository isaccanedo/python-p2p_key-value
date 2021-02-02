# -*- coding: utf-8 -*-

import sys
import socket
import struct

# parametros_entrada(argumentos_de_entrada)
# Obtém os argumentos de entrada digitados pelo usuário
# Saída: número de porto do programa, nome do arquivo de chaves e lista com endereços de servents
def parametros_entrada(argumentos):
	if len(argumentos) < 5:
		print "ERRO!\nQuantidade insuficiente de argumentos. Tente novamente."
		sys.exit(0)
	porto        = int(argumentos[2])
	nome_arquivo = argumentos[3]
	# Inicializa a lista de endereços de outros servents:
	servents = [ [ 0 for i in range(3) ] for j in range(len(argumentos) - 4) ]
	for i in range(len(argumentos) - 4): # Salva índice, IP e porto dos outros servents passados por parâmetro
		servents[i][0] = i 									  # Índice
		servents[i][1] = argumentos[i + 4].split(':')[0]      # IP
		servents[i][2] = int(argumentos[i + 4].split(':')[1]) # Porto
	return porto, nome_arquivo, servents

# obtem_chave_valor(linha_lida_do_arquivo)
# Obtém a chave e o valor de uma linha lida do arquivo
# Saída: chave e valor da linha
def obtem_chave_valor(aux):
	if aux[0] != '#' and aux != '\n':		# Salva chave contida no arquivo
		linha  = aux.split()
		chave  = linha[0]
		aux2   = aux.lstrip(linha[0])
		aux2   = aux2.replace('\n', '')
		while aux2[0] == '\t':
			aux2 = aux2.lstrip('\t')
		return chave, aux2
	else:
		return None, None

# conta_linhas(arquivo_que_contém_as_chaves_e_valores)
# Conta número de chaves contidas no arquivo
# Saída: número de chaves
def conta_linhas(arquivo):
	c = 0
	while True:
		aux = arquivo.readline()
		if aux == '':	 # Encerra se chegou ao final do arquivo
			arquivo.seek(0,0)
			return c
		elif aux[0] != '#' and aux != '\n':
			c = c + 1

# add_lista_chave_valor(lista_a_add_chave_e_valor, contador, chave, valor)
# Adiciona as chaves e valores lidos do arquivo em uma lista
# Saída: lista com chaves e valores adicionados
def add_lista_chave_valor(lista, c, chave, valor):
	for i in range(c):
		if lista[i][1] == chave: # Confere se há uma chave de mesmo nome na lista
			lista[i][1] = chave
			lista[i][2] = valor
			del lista[c]
			c = c -1
			return lista, c
	lista[c][0] = c
	lista[c][1] = chave
	lista[c][2] = valor
	return lista, c

# busca_chave(lista_de_chaves_e_valores, chave_procurada, numero_de_chaves)
# Procura se a chave procurada está na sua memória
# Saída: valor atrelado à chave procurada em caso de sucesso
def busca_chave(lista, chave_procurada):
	for i in range(len(lista)):
		if lista[i][1] == chave_procurada: # Verifica se chave foi encontrada
			print "Chave encontrada!"
			return lista[i][2]
	print "Chave não encontrada."
	return None

# alaga(tipo_de_msg, time_to_live, num_sequência, addr_do_cliente,chave_para_buscar, socket, addrs_de_servents)
# Monta mensagem de tipo KEYFLOOD e envia para todos os servents descobertos
# Saída: ---//---
def alaga(tipo, TTL, nseq, addr, chave, socket, servents):
	pack_tipo     = struct.pack('!H',tipo)
	pack_TTL      = struct.pack('!H',TTL)
	pack_nseq     = struct.pack('!I',nseq)
	aux1          = struct.pack('!B',int(addr[0].split('.')[0]))
	aux2          = struct.pack('!B',int(addr[0].split('.')[1]))
	aux3          = struct.pack('!B',int(addr[0].split('.')[2]))
	aux4          = struct.pack('!B',int(addr[0].split('.')[3]))
	pack_port_clt = struct.pack('!H',addr[1])
	mensagem = pack_tipo + pack_TTL + pack_nseq  + aux1 + aux2 + aux3 + aux4 + pack_port_clt + chave
	c = 0
	for i in servents:
		socket.sendto(mensagem, (i[1], i[2]))
		c = c + 1
	print "Mensagem alagada pelo overlay"

# KEYREQ(dados_recebidos, endereco_do_cliente, socket, lista_de_chaves, addrs_de_servents)
# Obtém o número de sequência e a chave a partir dos dados recebidos do cliente
# Saída: número de sequência e chave
def KEYREQ(dados, addr, socket, lista, servents, historico_key):
	print "KEYREQ recebido"
	nseq = struct.unpack('!I', dados[2:6])[0]
	chave = dados[6:]
	historico_key.append([addr, nseq])
	valor = busca_chave(lista, chave) 		   # Busca se a chave está em sua lista
	alaga(7, 3, nseq, addr, chave, socket, servents) # Alaga para os outros servents
	if valor != None:
		RESP(nseq, valor, addr, socket)
	return nseq, chave, historico_key

# KEYFLOOD(dados_recebidos, lista_de_chaves, socket, historico_de_requisições, lista_de_servents)
# Obtém as informações do KEYFLOOD a partir do payload recebido, responde o cliente e encaminha KEYFLOOD
# Saída: Número de sequência, chave da requisição, histórico de requisições atualizado, addr do cliente
def KEYFLOOD(dados, lista, socket, historico_key, servents):
	print "KEYFLOOD recebido:"
	TTL            = struct.unpack('!H', dados[2:4])[0]
	nseq           = struct.unpack('!I', dados[4:8])[0]
	IP_cliente     = str(struct.unpack('!B', dados[8:12][0])[0])
	for i in range(3):
		IP_cliente = IP_cliente + "." + str(struct.unpack('!B', dados[8:12][i + 1])[0])
	porto_cliente  = struct.unpack('!H', dados[12:14])[0]
	chave          = dados[14:]
	addr 		   = (IP_cliente, porto_cliente)
	if not ja_recebeu(addr, nseq, historico_key):
		historico_key.append([addr, nseq])
		valor = busca_chave(lista, chave)
		if TTL > 0:		  # Alaga o overlay caso TTL não seja 0
			TTL = TTL -1
			alaga(7, TTL, nseq, addr, chave, socket, servents)
			if valor != None: # Envia resposta para o cliente caso tenha achado a chave
				RESP(nseq, valor, addr, socket)
		return nseq, chave, historico_key, addr
	else:
		return nseq, chave, historico_key, addr

# TOPOREQ(dados_recebidos, endereco_do_cliente, socket, lista_de_chaves, histórico_de_requisições)
# Obtém núm. seq. enviado pelo cliente e encaminha para enviar TOPOFLOOD e resposta ao cliente
# Saída: ---//---
def TOPOREQ(dados, addr_cliente, addr_servent, porto, s, servents, historico_topo):
	print "TOPOREQ recebido"
	nseq = struct.unpack('!I', dados[2:6])[0] # Obtém núm. sequência a partir do pacote recebido
	historico_topo.append([addr_cliente, nseq])		  # Adiciona a mensagem vista ao histórico
	RESP(nseq, str(addr_servent) + ":" + str(porto), addr_cliente, s)
	alaga(8, 3, nseq, addr_cliente, str(addr_servent) + ":" + str(porto), s, servents)

# TOPOFLOOD(dados_recebidos, lista_de_chaves, socket, historico_de_requisições, lista_de_servents)
# Obtém as informações do TOPOFLOOD a partir do payload recebido, responde o cliente e encaminha TOPOFLOOD
# Saída: Número de sequência, topologia da rede, histórico de requisições atualizado, addr do cliente
def TOPOFLOOD(dados, lista, socket, historico_topo, servents, addr_servent, porto_servent):
	print "TOPOFLOOD recebido"
	TTL            = struct.unpack('!H', dados[2:4])[0]
	nseq           = struct.unpack('!I', dados[4:8])[0]
	IP_cliente     = str(struct.unpack('!B', dados[8:12][0])[0])
	for i in range(3):
		IP_cliente = IP_cliente + "." + str(struct.unpack('!B', dados[8:12][i + 1])[0])
	porto_cliente  = struct.unpack('!H', dados[12:14])[0]
	topologia      = dados[14:]
	topologia	   = topologia + " " + addr_servent + ":" + str(porto_servent)
	addr_cliente   = (IP_cliente, porto_cliente)
	if not ja_recebeu(addr_cliente, nseq, historico_topo):
		historico_topo.append([addr_cliente, nseq])
		if TTL > 0:		  # Alaga o overlay caso TTL não seja 0
			TTL = TTL -1
			alaga(8, TTL, nseq, addr_cliente, topologia, socket, servents)
			RESP(nseq, topologia, addr_cliente, socket)
		return nseq, topologia, historico_topo, addr_cliente
	else:
		return nseq, topologia, historico_topo, addr_cliente

# ja_recebeu(addr_do_cliente, num_sequencia, historico_de_requisições)
# Confere se requisição de KEYFLOOD de um nseq, de um mesmo addr já foi recebido antes
# Saída: True em caso afirmativo, False em caso negativo
def ja_recebeu(addr, nseq, historico):
	if historico == []: # Se histórico está vazio, nenhuma requis. foi recebida.
		return False
	else:
		for i in range(len(historico)):
			if historico[i][0] == addr and historico[i][1] == nseq: # Verifica se chave foi encontrada
				return True
		return False

# RESP(num_sequência, valor, endereço_do_cliente, socket)
# Envia resposta para o cliente no formato do protocolo
# Saída: ---//---
def RESP(nseq, valor, addr, socket):
	pack_tipo = struct.pack('!H',9)
	pack_nseq = struct.pack('!I',nseq)
	socket.sendto(pack_tipo + pack_nseq + valor, addr)