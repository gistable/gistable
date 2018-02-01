import asyncio
import json

import aiohttp


SCHOOL_URL_FMT = 'http://educacao.dadosabertosbr.com/api/escola/{}'
SEARCH_SCHOOL_URL = (
    'http://educacao.dadosabertosbr.com/api/escolas/buscaavancada?'
    'situacaoFuncionamento=1&energiaInexistente=on&aguaInexistente=on&'
    'esgotoInexistente=on'
)


@asyncio.coroutine
def get_and_parse_school_detail(school):
    url = SCHOOL_URL_FMT.format(school['cod'])
    resp = yield from aiohttp.request('GET', url)
    detail = yield from resp.json()
    return {'school': school, 'detail': detail}


@asyncio.coroutine
def get_schools():
    resp = yield from aiohttp.request('GET', SEARCH_SCHOOL_URL)
    return (yield from resp.json())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    schools_without_energy, school_list = loop.run_until_complete(
        get_schools()
    )

    print(
        'Número de Escolas em funcionamento sem energia, '
        'água e esgoto: {}'.format(schools_without_energy)
    )

    schools_detail_tasks = [
        get_and_parse_school_detail(school) for school in school_list
    ]

    wait_detail = asyncio.wait(schools_detail_tasks)
    school_detail_list, _ = loop.run_until_complete(wait_detail)

    for data in (f.result() for f in school_detail_list):
        school = data['school']
        detail = data['detail']

        print('{} - {}'.format(school['nome'], school['cod']))
        print('{} {} {}'.format(
            school['cidade'], school['estado'], school['regiao']
        ))

        if int(detail['salasExistentes']) > 1:
            print('Salas Existentes: {}'.format(detail['salasExistentes']))
            print('Funcionários: {}'.format(detail['funcionarios']))
            print('Queima Lixo: {}'.format(detail['lixoQueima']))
            print('Sanitário Fora Predio: {}'.format(
                detail['sanitarioForaPredio']
            ))

        print()

    loop.close()