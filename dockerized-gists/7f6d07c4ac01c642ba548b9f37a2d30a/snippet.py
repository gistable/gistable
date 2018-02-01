#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:15:44 2017
@author: avsthiago, asales, rtibola
"""

"""
Problema Original
http://www.inf.pucrs.br/~emoreno/undergraduate/CC/sisop/sem12.1/material/trabalhos/TP2.pdf

Especificação do problema
Um bar resolveu liberar um número específico de rodadas grátis para seus n 
clientes presentes no estabelecimento. Esse bar possui x garçons. Cada garçom 
consegue atender a um número limitado (C) de clientes por vez. Como essas 
rodadas são liberadas, cada garçom somente vai para a copa para buscar o pedido 
quando todos os C clientes que ele pode atender tiverem feito o pedido ou não 
houver mais clientes a serem atendidos. Após ter seu pedido atendido, um cliente
pode fazer um novo pedido após consumir sua bebida (o que leva um tempo 
aleatório) e a definição de uma nova rodada liberada. Uma nova rodada somente 
pode ocorrer quando foram atendidos todos os clientes que fizeram pedidos. 
Por definição, nem todos os clientes precisam pedir uma bebida a cada rodada.

Construção da solução
Implemente uma solução que permita a passagem por parâmetro (i) o número de
clientes presentes no estabelecimento, (ii) o número de garçons que estão 
trabalhando, (iii) a capacidade de atendimento dos garçons e (iv) o número de 
rodadas que serão liberadas no bar. Cada garçom e cada cliente devem ser 
representados por threads.

- A ordem de chegada dos pedidos dos clientes na fila de pedidos de cada garçom
  deve ser respeitada.
- A solução não deve permitir que clientes furem essa fila.
- O garçom só pode ir para a copa quando tiver recebido seus C pedidos.
- O programa deve mostrar a evolução, portanto planeje bem o que será 
  apresentado. Deve ficar claro acontecendo no bar a cada rodada. Os pedidos dos 
  clientes, os atendimentos pelos garçons, os deslocamentos para o pedido, a 
  garantia de ordem de atendimento, etc.
"""

import threading
import time
import random
import collections
import logging
import argparse

# Configuraçoes do log
logging.basicConfig(level=logging.DEBUG, format='%(message)s',)


class Cliente(threading.Thread):
    """Classe Cliente do tipo Thread"""
    def __init__(self, nome, gerenciador):
        threading.Thread.__init__(self)
        self.nome = nome
        # gerenciador compartilhado
        self.gerenciador = gerenciador
        # quando der self.e_esperar.wait() a thread espera receber o pedido
        self.e_esperar = threading.Event()
        self.beber = True

    def continuar(self):
        # o garçon utiliza esse metodo para acordar o cliente
        self.e_esperar.set()

    def faz_ped(self):
        """75% de chance do cliente beber"""
        chance = random.randint(0, 3)
        if chance == 3:
            # se nao quiser beber fala para o gerente que nao bebera e
            # o garcom ira o acordar e em seguida esperara a prox. rodada
            self.beber = False
            self.gerenciador.nao_quer_beber(self)
            self.e_esperar.wait()
            # habilita o lock interno do e_esperar para poder dar wait (again)
            self.e_esperar.clear()
            logging.info(" ".join(["Cliente",
                                   str(self.nome),
                                   "NAO vai beber"]))
            # espera a proxima rodada
            self.gerenciador.espera_beberem()
        else:
            self.beber = True
            # se coloca para ser atendido
            self.gerenciador.pedir(self)

    def espera_ped(self):
        """Espera o garcom acordar ele e
           depois libera o cliente para poder esperar novamente (.clear())"""
        self.e_esperar.wait()
        self.e_esperar.clear()

    def recebe_ped(self):
        """Tempo random para ele pegar o pedido do garcom antes de beber"""
        tempo = random.randint(1, 3)
        time.sleep(tempo)
        logging.info(" ".join(["Cliente",
                     str(self.nome),
                     "bebendo"]))

    def consome_ped(self):
        """Toma em um tempo random e espera todos tomarem para iniciar
            a proxima rodada"""
        tempo = random.randint(1, 3)
        time.sleep(tempo)
        logging.info(" ".join(["Cliente",
                     str(self.nome),
                     "bebeu"]))
        self.gerenciador.espera_beberem()

    def run(self):
        """Enquanto o bar nao fechar, testa se o cliente bebera
           se sim, faz o pedido, espera e consome"""
        while not self.gerenciador.fechou():
            self.faz_ped()
            if self.beber:
                self.espera_ped()
                self.recebe_ped()
                self.consome_ped()


class Garcom(threading.Thread):
    """Classe garcom do tipo thread"""
    def __init__(self, max_cli, nome, gerenciador):
        threading.Thread.__init__(self)
        self.nome = nome
        # gerenciador compartilhado
        self.gerenciador = gerenciador
        # maximo de clientes que ele pode atender
        self.max_cli = max_cli
        # lista de clientes que o garcom anotou
        self.anotados = []

    def recebe_max_ped(self):
        """Disputa com os garcons os clientes ate alcançar seu maximo de
           pedidos ou nao ter mais clientes para atender na rodada"""
        while len(self.anotados) < self.max_cli:
            cliente_atual = self.gerenciador.anotar_pedido(self)
            # verifica se ainda tem clientes para serem atendidos na rodada
            # if cliente_atual != -1:
            if cliente_atual is not None:
                if cliente_atual.beber:
                    self.anotados.append(cliente_atual)
                    logging.info(" ".join(["garcom",
                                 str(self.nome),
                                 "recebeu o pedido do Cliente",
                                 str(cliente_atual.nome)]))
                else:
                    # se o cliente nao quiser beber deixa ele esperar prox. rod
                    cliente_atual.continuar()
            else:
                # nao existem mais clientes para serem atendidos na rodada
                break

    def registra_ped(self):
        """Leva os pedidos para o balcao, o garcom tiver algum pedido"""
        if len(self.anotados) > 0:
            # randomiza um tempo que ele leva para ir ate a copa
            tempo = random.randint(1, 3)
            time.sleep(tempo)
            logging.info(" ".join(["garcom",
                         str(self.nome),
                         "registrou os pedidos dos clientes",
                         str([i.nome for i in self.anotados])]))

    def entrega_ped(self):
        """Vai de cliente em cliente da lista e entrega o pedido do garcom"""
        for i in self.anotados:
            # acorda a thread do cliente para ele poder receber e beber
            i.continuar()  # e_esperar.set()
            logging.info(" ".join(["garcom",
                         str(self.nome),
                         "entregou para o Cliente",
                         str(i.nome)]))

        # limpa a lista de pedidos do garcom
        self.anotados.clear()

    def run(self):
        """Enquanto o bar nao fechar o garcom pega o maximo
        de pedidos que conseguir e os entrega"""
        while not self.gerenciador.fechou():
            self.recebe_max_ped()
            self.registra_ped()
            self.entrega_ped()


class Gerenciador():
    """Permite exclusao mutua entre as threads e bloqueia açoes ate
       certas condicoes serem satisfeitas"""
    def __init__(self, n_clientes, tot_rodada):
        # lugar do cliente que quer beber e do que nao quer no prod. consumidor
        self.buff_quer = collections.deque([], 1)
        self.buff_n_quer = collections.deque([], 1)
        # lock que impede que garcons e cluentes acessem as listas acima juntos
        self.lock = threading.Condition()
        # clientes podem entrar na area critica
        self.vazio = threading.Semaphore(1)
        # garcons podem entrar na area critica
        self.cheio = threading.Semaphore(0)

        # numero de clientes que o bar possui
        self.n_clientes = n_clientes
        # quantidade de rodadas que ocorrerao
        self.tot_rodada = tot_rodada

        # total de pedidos entregues na rodada
        self.tot_entregue = 0
        # total de pedidos anotados e de clientes que nao querem beber na rod.
        self.tot_anotado = 0
        # numero da rodada atual
        self.rodada = 0
        # numero de clientes que precisam terminar de beber para a prox. rod.
        self.falta_beber = n_clientes

        # condicoes que permitem exclusao mutua
        self.lock_espera_todos_beberem = threading.Condition()
        self.lock_anotacao = threading.Condition()

    def espera_beberem(self):
        """Espera todos beberem para comecar a nova rodada"""
        with self.lock_espera_todos_beberem:
            # um cliente entra aqui por vez se ele for o ultimo libera todos
            if self.falta_beber - 1 == 0:
                # reinicia o numero de pessoas que faltam beber
                self.falta_beber = self.n_clientes
                self.rodada += 1
                # zera o numero de total de anotados para iniciar a prox rodada
                """self.muda_tot_anotado(False)"""

                if self.rodada == self.tot_rodada:
                    logging.info("\nACABOU GALERA!!!")
                else:
                    self.tot_anotado = 0
                    logging.info(" ".join(["\nJA ESTAMOS NA RODADA",
                                           str(self.rodada + 1)]))
                # libera todos os clientes para voltarem a pedir
                self.lock_espera_todos_beberem.notifyAll()
            else:
                self.falta_beber -= 1
                # trava o cliente que esta nessa area ate o ultimo destravar
                # todos os que estiverem aqui (o wait libera o lock)
                self.lock_espera_todos_beberem.wait()

    def fechou(self):
        """O bar fecha quando a rodada atual for igual o maximo de rodadas"""
        return self.tot_rodada == self.rodada

    def pedir(self, cliente):
        """Adiciona o cliente (que bebera) para ser atendido"""
        self.vazio.acquire()
        with self.lock:
            self.buff_quer.append(cliente)
        self.cheio.release()

    def nao_quer_beber(self, cliente):
        """Adiciona o cliente (que nao bebera) para ser atendido"""
        self.vazio.acquire()
        with self.lock:
            self.buff_n_quer.append(cliente)
        # libera lara um garcom retira-lo
        self.cheio.release()

    def anotar_pedido(self, garcom):
        """Consome o primeiro cliente que pedir (estiver no produtor consu.)"""
        with self.lock_anotacao:
            # verifica se todos ja foram atendidos
            if self.tot_anotado < self.n_clientes:
                self.cheio.acquire()
                with self.lock:
                    # verifica se o cliente adicionado bebera ou nao
                    if len(self.buff_quer) == 1:
                        cliente_atendido = self.buff_quer.popleft()
                    else:
                        cliente_atendido = self.buff_n_quer.popleft()

                    # libera para um novo cliente ser adicionado
                    self.vazio.release()
                    self.tot_anotado += 1
                    # retorna o cliente que foi atendido
                    return cliente_atendido
            else:
                # retornando None o garcom sabera que todos da rod. foram atend
                return None


def parse_argumentos():
    """Faz o parse dos argumentos"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_clientes',
                        help='Numero de Clientes. [3]',
                        type=int,
                        default=3)
    parser.add_argument('--n_garcons',
                        help='Numero de garcons. [2]',
                        type=int,
                        default=2)
    parser.add_argument('--cap_garcons',
                        help='Capacidade dos garcons. [2]',
                        type=int,
                        default=2)
    parser.add_argument('--n_rodadas',
                        help='Numero de rodadas. [4]',
                        type=int,
                        default=4)
    return parser.parse_args()


def main():
    # faz o parse dos argumentos recebidos
    args = parse_argumentos()

    logging.info(" ".join(["\nO Gerente ficou MALUCOOO e mandou todos os",
                           str(args.n_garcons),
                           "garcons distribuirem",
                           str(args.n_rodadas),
                           "rodadas para voces",
                           str(args.n_clientes),
                           "clientes, \nmas eles somente pegarao",
                           str(args.cap_garcons),
                           "pedidos por vez"]))
    logging.info("\nQUE COMECE A PRIMEIRA RODADA!!!")

    # verifica se o bar possui clientes
    if args.n_clientes > 0:
        # Cria o objeto gerente que sera passado aos garcons e clientes
        geren = Gerenciador(args.n_clientes, args.n_rodadas)

        # Cria n_garcons garcons atribuindo i como o nome deles
        l_garcons = [Garcom(args.cap_garcons, i, geren)
                     for i in range(args.n_garcons)]
        # Cria n_clientes Clientes atribuindo i como o nome deles
        l_clientes = [Cliente(i, geren) for i in range(args.n_clientes)]

        # inicia os garcons e clientes
        for i in l_garcons:
            i.start()
        for i in l_clientes:
            i.start()

        for i in l_clientes:
            i.join()
        logging.info("\nClientes sairam.")
        for i in l_garcons:
            i.join()
    logging.info("\ngarcons param de servir.")

if __name__ == '__main__':
    main()
