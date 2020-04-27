#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 19:53:51 2020

@author: max
"""



import os
import time 
import cv2 
import numpy as np
import pandas as pd
import pytesseract
import matplotlib.pyplot as plt

from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys

driver = webdriver.Firefox()
driver.set_window_size(1920, 1080)
driver.get('https://quetsodienthoai.com/')

user = 'dream4996@gmail.com'
password = 'minh1234'


driver.find_element_by_xpath(
    '/html/body/div[1]/header/div/div/div/div/div[2]/div/ul/li[4]/a[2]'
).click()

driver.find_element_by_xpath(
    '/html/body/div[1]/div/div/div[1]/div[2]/div/div[1]/div/form/div[1]/input[1]'
).send_keys(user)

driver.find_element_by_xpath(
    '/html/body/div[1]/div/div/div[1]/div[2]/div/div[1]/div/form/div[1]/input[2]'
).send_keys(password)


driver.find_element_by_xpath(
    '/html/body/div[1]/div/div/div[1]/div[2]/div/div[1]/div/form/div[2]/div/div/button'
).click()
 

sdt='01657078968'
driver.get(f'https://quetsodienthoai.com/search-phone/?phone={sdt}')


for i in range(500):
    image_bytes = WebDriverWait(driver, 20).until(ec.visibility_of_element_located(
        (By.XPATH,
         '//*[@id="imgCaptcha"]')
        )
    ).screenshot_as_png
    capt_im = cv2.imdecode(np.fromstring(image_bytes, dtype=np.uint8), 1)
    text = pytesseract.image_to_string(capt_im[8:27,32:73]) 
    texts = ''.join([t for t in text])
            
    if len(texts) == 3:
        print(texts)
        texts = texts.lower()
        ims = [capt_im[8:27, 33:45], capt_im[8:27, 47:59], capt_im[8:27, 61:73]]
        """
        plt.figure()
        plt.imshow(capt_im[8:27,32:73])
        plt.title(text)
        """
        for j, im in enumerate(ims):
            cv2.imwrite(f'single_capt/{texts[j]}_{i}.jpg', im)
            
    driver.refresh()


import string
alphabet = [str(i) for i in range(0,10)] + list(string.ascii_lowercase)


main_path = os.path.dirname(os.path.realpath(__file__))
print(main_path)

import shutil
import os 

for file in sorted(os.listdir(f'{main_path}/single_capt/')):
    if file[0] in alphabet and file[-3:] == 'jpg':
        if os.path.exists(f'{main_path}/single_capt/{file[0]}'):
            shutil.move(main_path+'/single_capt/'+file, f'{main_path}/single_capt/{file[0]}/{file}')
        else:
            os.mkdir(main_path+f'/single_capt/{file[0]}/')
            time.sleep(3)
            shutil.move(main_path+'/single_capt/'+file, f'{main_path}/single_capt/{file[0]}/{file}')
            
            
            
            
            

    
    
    