#!/usr/local/bin/python
# -*- coding: utf-8 -*-

""" Um cliente python para a API Olho Vivo """

import requests


class SPTransClient(object):
    """ Um cliente python para a API Olho Vivo """

    session = requests.Session()
    url = 'http://api.olhovivo.sptrans.com.br/v0/'

    def auth(self, token):

        """
        Para autenticar-se no serviço de API do Olho Vivo
        é necessário efetuar uma chamada prévia utilizando
        o método http POST informando seu token de acesso.
        Essa chamada irá retornar true quando a autenticação
        for realizada com sucesso e false em caso de erros.
        """

        method = 'Login/Autenticar?token=%s' % token
        response = self.session.post(self.url + method)

        if response.cookies:
            return True

        return False

    def _get(self, path):

        """ HTTP GET comum para os demais métodos """

        response = self.session.get(self.url + path)
        data = response.json()
        return data

    def search_by_bus(self, term):

        """
        Realiza uma busca das linhas do sistema com base no
        parâmetro informado. Se a linha não é encontrada então
        é realizada uma busca fonetizada na denominação das linhas.
        """

        return self._get('Linha/Buscar?termosBusca=%s' % term)

    def get_bus_detail(self, uid):

        """
        Retorna as informações cadastrais de uma determinada linha.
        Caso o parâmetro seja omitido são retornados os dados de todas
        as linhas do sistema.
        """

        return self._get('Linha/CarregarDetalhes?codigoLinha=%s' % uid)

    def search_by_stops(self, term):

        """
        Realiza uma busca fonética das paradas de ônibus do sistema
        com base no parâmetro informado. A consulta é realizada no nome
        da parada e também no seu endereço de localização.
        """

        return self._get('Parada/Buscar?termosBusca=%s' % term)

    def search_stops_by_bus(self, uid):

        """
        Realiza uma busca por todos os pontos de parada atendidos por
        uma determinada linha.
        """

        return self._get('Parada/BuscarParadasPorLinha?codigoLinha=%s' % uid)

    def get_bus_position(self, uid):

        """
        Retorna uma lista com todos os veículos de uma determinada linha
        com suas devidas posições.
        """

        return self._get('Posicao?codigoLinha=%s' % uid)

    def get_next_bus(self, stop_id, bus_id):

        """
        Retorna uma lista com a previsão de chegada dos veículos da linha
        informada que atende ao ponto de parada informado.
        """

        return self._get('Previsao?codigoParada=%s&codigoLinha=%s' % (stop_id,
                                                                      bus_id))

    def get_next_bus_in_stop(self, stop_id):

        """
        Retorna uma lista com a previsão de chegada dos veículos de cada uma
        das linhas que atendem ao ponto de parada informado.
        """

        return self._get('Previsao/Parada?codigoParada=%s' % stop_id)