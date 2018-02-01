import sys
import argparse
from getpass import getpass

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def navigate(card_number, user_name, passkey):
    try:
        browser = webdriver.Firefox()
        browser.get('https://www.itau.com.br/cartoes/')
        card = browser.find_element_by_id('campo_cartao_credito')
        card.send_keys(card_number)
        card.send_keys(Keys.RETURN)

        user = browser.find_element_by_link_text(user_name)
        user.click()

        buttons = browser.find_elements_by_class_name('TextoTecladoVar')
        password = {n:b.find_element_by_tag_name('a') for b in buttons for n in b.text.split(' ou ')}
        for c in passkey:
            password[c].click()
        ok = browser.find_element_by_css_selector('a[onmousemove="status=\'Envia\'"]')
        ok.click()

        query = browser.find_element_by_class_name('HOlnk01')
        query.click()


        table = browser.find_element_by_xpath("//td[@class='EXTlinhaImpar']/../..")
        result = [[td.text.strip() for td in tr.find_elements_by_tag_name('td')]
                  for tr in table.find_elements_by_tag_name('tr')]

        top = browser.find_element_by_xpath("//td[3]/a")
        top.click()
        table = browser.find_element_by_xpath("//td[@class='EXTlinhaImpar']/../..")
        result += [[td.text.strip() for td in tr.find_elements_by_tag_name('td')]
                  for tr in table.find_elements_by_tag_name('tr')]


        data = [(transaction[:2], transaction[3:5], transaction[8:], credit, debit)
                for transaction, credit, debit in result]

        return data
    finally:
        browser.close()


def show(data):
    months = set(row[1] for row in data)
    print('---------------')
    for i, row in enumerate(data):
        print('{} - {}'.format(i, ' '.join(row)))
    print('---------------')


if __name__ == '__main__':
    USER_NAME = 'Primeiro nome (letras maiusculas, como aparece no site)'
    CARD_NUMBER = 'Numero do cartao'
    PASSWORD = 'Senha'
    parser = argparse.ArgumentParser(description='Scrap Itaucard')
    parser.add_argument('-n', '--name', help=USER_NAME)
    parser.add_argument('-c', '--card', help=CARD_NUMBER)
    parser.add_argument('-p', '--password', help=PASSWORD)
    args = parser.parse_args()
    if not args.name:
        args.name = input(USER_NAME+': ')
    if not args.card:
        args.card = input(CARD_NUMBER+': ')
    if not args.password:
        args.password = getpass(PASSWORD+': ')

    data = navigate(args.card, args.name, args.password)
    show(data)
