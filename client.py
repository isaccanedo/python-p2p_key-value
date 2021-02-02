# -*- coding: utf-8 -*-

import sys
import socket
import struct

if len(sys.argv) != 3:
	print "ERRO!\nTente novamente com dois argumentos: IP PORTO"
	sys.exit(0)

ip = sys.argv[1]			#Inserir ip do servent no terminal
port = int(sys.argv[2])		#Inserir porto do servent no terminal
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Socket UDP
dest = (ip, port)			#Servent como destino
n_seq = 0					#Número de sequência das mensagens global

def lista_comandos():
	print "------------------COMANDOS---------------------"
	print "? + Chave : Manda uma solicitação de valor"
	print "T : Manda uma solicitação de topologia da rede"
	print "H : Imprime a lista de comandos novamente"	
	print "Q : Sair do programa"
	print "-----------------------------------------------"
def digita_mensagem():		#Função que faz o cliente digitar alguma mensagem no terminal
    buf = sys.stdin.readline()
    mensagem = buf.replace("\n","")
    return mensagem


#Função responsável por fazer o requerimento com a chave, manda para 
#o servent associado, que por sua vez retorna o valor associado
def req_valor(chave):
	global n_seq  				#Usa a variável global do número de sequência
	recebeu = False				#Lógica, se recebeu mensagem 
	tipo = struct.pack('!H',5)	#Define o tipo de mensagem
	num_seq = struct.pack('!I',n_seq)	#Número de sequencia da mensagem
	KEYREQ = tipo + num_seq + chave 	#Monta a mensagem de requerimento
	udp.sendto(KEYREQ,dest)				#Envia para o servent
	n_seq = n_seq + 1					#Incrementa o número de sequência
	udp.settimeout(4)					#Define o tempo de expirar
	while True:
		try:
			resp,address = udp.recvfrom(1024)	#Espera receber mensagem de volta
			if resp:
				recebeu = True	#Se receber na primeira tentativa, a variável lógica fica verdadeira 
				if struct.unpack('!H',resp[0:2])[0] == 9:		#Se a mensagem for do tipo RESP
					if struct.unpack('!I',resp[2:6])[0] == n_seq - 1:	#Se for o mesmo número de seq
						print resp[6:] + " " + str(address[0]) + ":" + str(address[1]) 
						#Printa o valor e o endereço ip e porto de quem enviou
					else:
						print "Mensagem incorreta recebida de:" + address
		except socket.timeout: #Caso o tempo ultrapasse
			if recebeu == False: #Caso não tiver recebido nada ainda
				try:
					num_seq = struct.pack('!I',n_seq)		#Atualiza numero de sequencia
					KEYREQ = tipo + num_seq + chave 		#Monta nova mensagem
					udp.sendto(KEYREQ,dest) 				#Manda novamente para servent
					n_seq = n_seq + 1						#Incrementa numero de seq
					resp,address = udp.recvfrom(1024)		#Espera receber resposta
					if resp:
						recebeu = True						#Se recebeu muda variável lógica
						if struct.unpack('!H',resp[0:2])[0] == 9:		#Verificar RESP
							if struct.unpack('!I',resp[2:6])[0] == n_seq - 1:		#Verificar num seq
								print resp[6:] + " " + str(address[0]) + ":" + str(address[1]) #Printa
							else:
								print "Mensagem incorreta recebida de:" + address

				except socket.timeout:	#Caso ainda não tiver recebido nada
					print "Nenhuma resposta recebida" #Avisa que não teve resposta
					break	#Fecha função
			else:
				break	#Caso não tenha nenhuma mais mensagem depois dos 4s fechar função


#Função responsável por fazer o requerimento da topologia da rede, e retornarem os 
#endereços que estiverem nela
def req_topologia():
	global n_seq 	#Usa a variável global do número de sequência
	recebeu = False	#Lógica, se recebeu mensagem 
	tipo = struct.pack('!H', 6)	#Define o tipo de mensagem
	num_seq = struct.pack('!I',n_seq)	#Número de sequencia da mensagem
	TOPOREQ = tipo + num_seq			#Monta a mensagem de requerimento
	udp.sendto(TOPOREQ,dest)			#Envia para o servent
	n_seq = n_seq + 1					#Incrementa o número de sequência
	udp.settimeout(4)					#Define o tempo de expirar
	while True:
		try:
			resp,address = udp.recvfrom(1024)	#Espera receber mensagem de volta
			if resp:	
				recebeu = True	#Se receber na primeira tentativa, a variável lógica fica verdadeira 
				if struct.unpack('!H',resp[0:2])[0] == 9:	#Se a mensagem for do tipo RESP
					if struct.unpack('!I',resp[2:6])[0] == n_seq - 1:	#Se for o mesmo número de seq
						print resp[6:] #Printa a topologia de rede
					else:
						print "Mensagem incorreta recebida de:" + address

		except socket.timeout: #Caso o tempo ultrapasse
			if recebeu == False:  #Caso não tiver recebido nada ainda
				try:
					num_seq = struct.pack('!I',n_seq)	#Atualiza numero de sequencia
					TOPOREQ = tipo + num_seq			#Monta nova mensagem
					udp.sendto(TOPOREQ,dest)			#Manda novamente para servent
					n_seq = n_seq + 1					#Incrementa numero de seq
					resp,address = udp.recvfrom(1024)	#Espera receber resposta
					if resp:
						recebeu = True					#Se recebeu muda variável lógica
						if struct.unpack('!H',resp[0:2])[0] == 9:	#Verificar RESP
							if struct.unpack('!I',resp[2:6])[0] == n_seq - 1:	#Verificar num seq
								print resp[6:]	#Printa topologia de rede
							else:
								print "Mensagem incorreta recebida de:" + address


				except socket.timeout: #Caso ainda não tiver recebido nada
					print "Nenhuma resposta recebida"	 #Avisa que não teve resposta
					break	#Fecha função
			else:
				break	#Caso não tenha nenhuma mais mensagem depois dos 4s fechar função


def client():
	print("-----------------CLIENTE v1.0------------------")
	print("Por Bhryan Henderson e Rafael Santos de Almeida")
	lista_comandos()	#Imprime lista de comandos
	sys.stdout.write("-> "); sys.stdout.flush()

	while True:
		mensagem = digita_mensagem()	#Espera usuário digitar algo
		if mensagem[0] == "?" and len(mensagem) < 3:
			print "ERRO!\nDigite ? e a chave a ser pesquisada:"
		if mensagem[0] == "?" and len(mensagem) >= 3:			#Se for do tipo requisição de valor
			chave = mensagem[1:]		#Separa chave da mensagem
			while (chave[0] == '\t') or (chave[0] == ' '):	#Tirar tabulações e espaços
				if chave[0] == '\t':
					chave = chave.lstrip('\t')
				elif chave[0] == ' ':
					chave = chave.lstrip(' ')

			req_valor(chave)	#Chama função com a chave como parâmetro			

		elif mensagem[0].upper() == "T":	#Se for do tipo requisição de topologia da rede
			req_topologia()			#Chama função

		elif mensagem[0].upper() == "Q":	#Se for do tipo solicitar sair
			udp.close()				#Fecha socket
			break					#Sai do while

		elif mensagem[0].upper() == "H":	#Se for do tipo Ajuda
			lista_comandos()		#Imprime novamente a lista de comandos

		else:						#Caso não for mensagem válida
			print "ERRO!\nComando inválido, tente novamente!"
		sys.stdout.write("-> "); sys.stdout.flush()

if __name__ == "__main__": #inicio do programa

    sys.exit(client()) #chama a funcao e sai
