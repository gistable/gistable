from selenium import webdriver
from time import sleep
d = webdriver.Chrome()
d.get('http://mrcoles.com/piano/')
sleep(2)
d.execute_script('document.querySelector(\'.keys\').style.width=\'791px\' ; var es = document.querySelectorAll(\'.black\') ; for (var e = 0 ; e < es.length ; ++e) { es[e].style.width = \'1px\'; }')

keymap = {'a': [-3, 9], 'a#': [-2, 10], 'bb': [-2, 10], 'b': [-1, 11], 'c': [-12, 0, 12], 'c#': [-11, 1], 'd': [-10, 2], 'd#': [-9, 3], 'eb': [-9, 3], 'e': [-8, 4], 'f': [-7, 5], 'f#': [-6, 6], 'g': [-5, 7], 'g#': [-4, 8]}

def key(letter, pos):
  return 'div[data-key="%s"]' % keymap[letter][pos]

def press(letter, pos):
  d.find_element_by_css_selector(key(letter, pos)).click()

mult = 1

def minim(letter, pos):
  press(letter, pos) ; sleep(mult * 0.35)

def dotted_crotchet(letter, pos):
  press(letter, pos) ; sleep(0.31)

def crotchet(letter, pos):
  press(letter, pos) ; sleep(mult * 0.22)

def quaver(letter, pos):
  press(letter, pos) ; sleep(0.17)

m = minim
dc = dotted_crotchet
c = crotchet
q = quaver

press('d', 1) ; q('f', 1), q('e', 1) ; sleep(0.1) ; c('d', 1) ; sleep(0.1) ; q('c#', 1) ; q('d', 1) ; c('e', 1) ; sleep(0.1) ; dc('d', 1)# ; sleep(0.2)

q('e', 1) ; q('d', 1) ; q('e', 1) ; c('f', 1) ; sleep(0.1) ; c('f', 1) ; sleep(0.1) ; c('f', 1) ; sleep(0.08) ; q('e', 1) ; q('d', 1) ; m('c#', 1) ; sleep(0.18)

q('b', 0) ; sleep(0.08) ; q('c#', 1) ; c('d', 1) ; sleep(0.1) ; c('d', 1) ; q('f', 1) ; q('e', 1) ; c('d', 1) ; sleep(0.15) ; q('c#', 1) ; q('d', 1) ; c('e', 1) ; sleep(0.1) ; m('d', 1) ; sleep(0.18)

c('g', 1) ; c('f', 1) ; c('e', 1) ; c('d', 1) ; m('e', 1) ; sleep(0.1) ; q('d', 1) ; q('c#', 1) ; q('b', 0) ; q('c#', 1) ; q('d', 1) ; m('e', 1) ; sleep(0.2)

c('eb', 1) ; dc('d', 1) ; q('c', 1) ; q('bb', 0) ; q('c', 1) ; c('d', 1) ; c('e', 1) ; sleep(0.1) ; c('f', 1) ; m('eb', 1) ; dc('d', 1) ; q('c', 1) ; q('bb', 0) ; q('c', 1) ; c('d', 1) ; q('e', 1) ; q('g', 1) ; c('f', 1) ; dc('f#', 1) ; q('a', 1) ; m('g', 1) ; c('g#', 1) ; q('bb', 1) ; m('a', 1) ; c('a', 1) ; q('g', 1) ; q('a', 1) ; q('c', 2) ; m('bb', 1)

c('a', 1) ; c('g', 1) ; q('f', 1) ; q('e', 1) ; m('d', 1)

m('a', 1) ; c('g', 1) ; c('f', 1) ; q('e', 1) ; q('f', 1) ; c('d', 1)

c('g', 1) ; c('f', 1) ; c('e', 1) ; c('d', 1)

mult = 1.25 #rit

m('f', 1) ; m('e', 1) ; m('eb', 1) ; c('d', 1) ; m('d', 1) ; sleep(0.35) ; c('c#', 1) ; sleep(0.2) ; c('d', 1)