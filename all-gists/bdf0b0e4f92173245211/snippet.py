def gera_boleto():
    import datetime
    import pyboleto
    from pyboleto.bank.caixa import BoletoCaixa
    from pyboleto.pdf import BoletoPDF
    import os
  
    listaDadosCaixa = []
    for i in range(2):
        d = BoletoCaixa()
        d.carteira = 'SR'  
        d.cedente = 'Empresa ACME LTDA'
        d.cedente_documento = "102.323.777-01"
        d.cedente_endereco = "Rua Acme, 123 - Centro - Sao Paulo/SP - CEP: 12345-678"
        d.agencia_cedente = '1565'
        d.conta_cedente = '414-3'

        d.data_vencimento = datetime.date(2010, 3, 27)
        d.data_documento = datetime.date(2010, 2, 12)
        d.data_processamento = datetime.date(2010, 2, 12)

        d.instrucoes = [
            "- Linha 1",
            "- Sr Caixa, cobrar multa de 2% após o vencimento",
            "- Receber até 10 dias após o vencimento",
            ]
        d.demonstrativo = [
            "- Serviço Teste R$ 5,00",
            "- Total R$ 5,00",
            ]
        d.valor_documento = 255.00

        d.nosso_numero = "8019525086"
        d.numero_documento = "8019525086"
        d.sacado = [
            "Cliente Teste %d" % (i + 1),
            "Rua Desconhecida, 00/0000 - Não Sei - Cidade - Cep. 00000-000",
            ""
            ]
        listaDadosCaixa.append(d)


    boleto_arq = 'Boleto.pdf'

    boleto = BoletoPDF(boleto_arq)
    for i in range(len(listaDadosCaixa)):
        boleto.drawBoleto(listaDadosCaixa[i])
        boleto.nextPage()
    boleto.save()

    abre_boleto = open(boleto_arq,"rb").read()
    os.unlink(boleto_arq)
    response.headers['Content-Type']='application/pdf'
    
    return abre_boleto