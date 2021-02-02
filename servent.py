# -*- coding: utf-8 -*-

import sys
import socket
import struct
import mtd_servent

porto, nome_arquivo, servents = mtd_servent.parametros_entrada(sys.argv)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Cria socket UDP
HOST = str(socket.gethostbyname(socket.gethostname()))
s.bind(('localhost',porto))

arquivo = open(nome_arquivo)
n_chaves = mtd_servent.conta_linhas(arquivo) # Salva o número de linhas contidas no arquivo
lista = [ [ 0 for i in range(3) ] for j in range(n_chaves) ] # Cria lista com tamanho exato para caber todas as chaves
c = 0 # Contador auxiliar

# Lê as chaves e os valores do arquivo:
while True:
	aux = arquivo.readline() #Lê uma linha do arquivo
	if aux == '': # Encerra o laço se chegou ao final do arquivo
		break
	chave, valor = mtd_servent.obtem_chave_valor(aux)
	# Adiciona a chave e o valor em uma lista:
	if chave != None and valor != None:
		lista, c = mtd_servent.add_lista_chave_valor(lista, c, chave, valor)
		c = c + 1
arquivo.close()

n_chaves       = c
historico_key  = []   # Inicializa lista de histórico de requisições de valores
historico_topo = []   # Inicializa lista de histórico de topologia
nseq           = None # Inicializa variável que salva número de sequência das mensagens

# Trata as mensagem recebidas:
while True:
	aux, addr = s.recvfrom(1024)
	tipo_msg  = struct.unpack('!H',aux[0:2])[0]
	if tipo_msg == 5: # KEYREQ
		nseq, chave, historico_key = mtd_servent.KEYREQ(aux, addr, s, lista, servents, historico_key)
	elif tipo_msg == 6: # TOPOREQ
		mtd_servent.TOPOREQ(aux, addr, HOST, porto, s, servents, historico_topo)
	elif tipo_msg == 7: # KEYFLOOD
		nseq, chave, historico_key, addr = mtd_servent.KEYFLOOD(aux, lista, s, historico_key, servents)
	elif tipo_msg == 8: # TOPOFLOOD
		nseq, topologia, historico_topo, addr = mtd_servent.TOPOFLOOD(aux, lista, s, historico_topo, servents, HOST, porto)
	else:
		print "ERRO!\nIdentificador TIPO não reconhecido."