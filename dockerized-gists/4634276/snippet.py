# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import mechanize

class SomfyException(Exception):
    def __init__(self, value):
        Exception.__init__(self, value)
        self.value = value

    def __str__(self):
        return repr(self.value)

class Somfy:
    def __init__(self, config):
        self.config = config
        self.browser = mechanize.Browser()

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, type, value, traceback):
        self.logout()

    def login(self):
        login_response = self.browser.open(self.config.get('somfy', 'url') + "/m_login.htm")
        login_html = login_response.read()

        login_soup = self._beautiful_it_and_check_error(login_html)
        authentication_code = login_soup.find('form').find('table').findAll('tr')[5].findAll('b')[0].find(text=True)

        self.browser.select_form(nr=0)
        self.browser["password"] = self.config.get('somfy', 'password')
        self.browser["key"] = self.config.get('somfy', 'key_%s' % authentication_code)

        self.browser.submit()

    def logout(self):
        self.browser.open(self.config.get('somfy', 'url') + "/m_logout.htm")

    def set_zone_a(self):
        self.browser.open(self.config.get('somfy', 'url') + "/mu_pilotage.htm")
        self.browser.select_form(nr = 0)
        self.browser.submit()

    def set_zone_b(self):
        self.browser.open(self.config.get('somfy', 'url') + "/mu_pilotage.htm")
        self.browser.select_form(nr = 1)
        self.browser.submit()

    def set_zone_c(self):
        self.browser.open(self.config.get('somfy', 'url') + "/mu_pilotage.htm")
        self.browser.select_form(nr = 2)
        self.browser.submit()

    def set_all_zone(self):
        self.browser.open(self.config.get('somfy', 'url') + "/mu_pilotage.htm")
        self.browser.select_form(nr =3)
        self.browser.submit()

    def unset_all_zone(self):
        self.browser.open(self.config.get('somfy', 'url') + "/mu_pilotage.htm")
        self.browser.select_form(nr =4)
        self.browser.submit()

    def get_state(self):
        state_response = self.browser.open(self.config.get('somfy', 'url') + "/mu_etat.htm")
        state_html = state_response.read()

        state_soup = self._beautiful_it_and_check_error(state_html)
        result = self.get_general_state(state_soup.findAll('table')[0])
        result.update(self.get_zone_state(state_soup.findAll('table')[0]))

        return result

    def get_zone_state(self, state_soup):
        zone_state = state_soup.findAll('table')[2].findAll('tr')

        def get_zone_a():
            return { "zone_a" : zone_state[0].find(text=True) }

        def get_zone_b():
            return { "zone_b" : zone_state[1].find(text=True) }

        def get_zone_c():
            return { "zone_c" : zone_state[2].find(text=True) }

        result = get_zone_a()
        result.update(get_zone_b())
        result.update(get_zone_c())

        return result

    def get_general_state(self, state_soup):
        general_state = state_soup.findAll('table')[1].findAll('tr')

        def get_battery_state():
            return { "battery" : general_state[0].find(text=True) }

        def get_communication_state():
            return { "communication" : general_state[1].find(text=True) }

        def get_door_state():
            return { u"door" : general_state[2].find(text=True) }

        def get_alarm_state():
            return { "alarm" : general_state[4].find(text=True) }

        def get_material_state():
            return { "material" : general_state[6].find(text=True) }

        result = get_battery_state()
        result.update(get_communication_state())
        result.update(get_door_state())
        result.update(get_alarm_state())
        result.update(get_material_state())

        return result

    def _beautiful_it_and_check_error(self, html):
        soup = BeautifulSoup(''.join(html))
        self._check_error(soup)
        return soup

    def _check_error(self, soup):
        if soup.find("div", {"class": "error"}):
            error_code = soup.find('div').findAll('b')[0].find(text=True)
            if '(0x0904)' == error_code:
                raise SomfyException("Nombre d'essais maximum atteint")
            if '(0x1100)' == error_code:
                raise SomfyException("Code errone")
            if '(0x0902)' == error_code:
                raise SomfyException("Session deja ouverte")
            if '(0x0812)' == error_code:
                raise SomfyException("Mauvais login/password")
            if '(0x0903)' == error_code:
                raise SomfyException("Droit d'acces insuffisant")