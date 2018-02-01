from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import requests
import os


def download_all_papers(base_url, save_dir, driver_path):
    driver = webdriver.Chrome(driver_path)
    driver.get(base_url)

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # wait for the select element to become visible
    wait = WebDriverWait(driver, 10)
    res = wait.until(EC.presence_of_element_located((By.ID, "notes")))
    print("Successful load the website!")
    # parse the results
    divs = driver.find_elements_by_class_name('title_pdf_row')
    num_papers = len(divs)
    for index, paper in enumerate(divs):
        name = paper.find_element_by_class_name('note_content_title').text
        link = paper.find_element_by_class_name('note_content_pdf').get_attribute('href')
        print('Downloading paper {}/{}: {}'.format(index+1, num_papers, name))
        download_pdf(link, os.path.join(save_dir, name))
    driver.close()


def download_pdf(url, name):
    r = requests.get(url, stream=True)

    with open('%s.pdf' % name, 'wb') as f:
        for chunck in r.iter_content(1024):
            f.write(chunck)
    r.close()


if __name__ == '__main__':
    NIPS = 'https://openreview.net/group?id=NIPS.cc/2016/Deep_Learning_Symposium'
    ICLR = 'https://openreview.net/group?id=ICLR.cc/2017/conference'
    driver_path = '/Users/JunhongXu/Desktop/chromedriver'
    save_dir_nips = '/Users/JunhongXu/Desktop/papers/nips'
    save_dir_iclr = '/Users/JunhongXu/Desktop/papers/iclr'

    download_all_papers(NIPS, save_dir_nips, driver_path)
    download_all_papers(ICLR, save_dir_iclr, driver_path)
