from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.common.keys import Keys
import time

cargas = ['500', '300', '200', '150', '100', '50', '30', '20']

dict_cargas = {}
i = 0
for c in cargas:
    i += 1
    dict_cargas[c] = i

# pon tus datos aquí:    

cargale = '50' # tu carga en string (ver variable cargas)
num = '55********' # número al que le quieres hacer la carga a 10 dígitos
cc = ["****","****","****","****"] # tu tarjeta de crédito
venc = [2,2021] # fecha de vencimiento en número
cvv2 = ['***'] # el número cvv2 al reverso de tu tarjeta
email = ['your@email.mx'] # correo electrónico
cp = ['82017'] # tu código postal

def page_is_loaded(driver):
    return driver.find_element_by_tag_name("body") != None
def form_is_loaded(driver):
    return driver.find_element_by_tag_name("form") != None
def list_is_loaded(driver):
    return driver.find_element_by_xpath("//input[@type='text']") != None

driver = webdriver.Chrome()
driver.get("https://mitelcel1.recarga.telcel.com/MiTelcelMXExternalWebAnonymous/enter.do?anonymous=true")

wait = ui.WebDriverWait(driver, 10)
wait.until(page_is_loaded)
wait.until(form_is_loaded)

# Primera sección - validación del teléfono

tel = driver.find_element_by_id("mdn")
tel.click()
tel.send_keys(num)
tel.send_keys(Keys.ENTER)
time.sleep(1)

telConf = driver.find_element_by_id("mdnConfirm")
telConf.send_keys(num)
telConf.send_keys(Keys.ENTER)
time.sleep(1)

wait.until(list_is_loaded)
driver.find_element_by_xpath("//a[@class='chosen-single']").click()

wAmount = driver.find_element_by_xpath("//li[@data-option-array-index='{}']".format(dict_cargas[cargale]))
wAmount.click()

driver.find_element_by_id("continue_button").click()

wait.until(page_is_loaded)
driver.find_element_by_id("submit_button").click()

wait.until(page_is_loaded)

i = 0
for c in cc:
    i += 1
    driver.find_element_by_name("num_card{}".format(i)).send_keys(c)

driver.find_element_by_xpath("(//*[@class='chosen-single'])[1]").click()
driver.find_element_by_xpath("(//*[@data-option-array-index='{}'])[1]".format(venc[0])).click()

driver.find_element_by_xpath("(//*[@class='chosen-single'])[2]").click()
driver.find_element_by_xpath("(//*[@data-option-array-index='{}'])[2]".format(venc[1] - 2015)).click()

driver.find_element_by_name("chargeCVN").send_keys(cvv2)
driver.find_element_by_name("postalCode").send_keys(cp)
driver.find_element_by_name("emailAddress").send_keys(email)

driver.find_element_by_id("continue_button").click()

driver.find_element_by_tag_name("body").send_keys(Keys.TAB)

driver.find_element_by_id("acheckbox").click()

goNext = driver.find_element_by_id("submit_button")
#goNext.click()

