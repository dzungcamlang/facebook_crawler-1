#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 11:25:07 2020

@author: max
"""

import os
import time 
import cv2 
import numpy as np
import pandas as pd
import pytesseract
import matplotlib.pyplot as plt

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys

driver = webdriver.Firefox()
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


#%%
def captcha_solve(driver):
    try:
        image_bytes = WebDriverWait(driver, 20).until(ec.visibility_of_element_located(
            (By.XPATH,
             '//*[@id="imgCaptcha"]')
            )
        ).screenshot_as_png
        capt_im = cv2.imdecode(np.fromstring(image_bytes, dtype=np.uint8), 1)
        text = pytesseract.image_to_string(capt_im[8:27,32:73]) 
        texts = ''.join([t for t in text if t.isupper()])
        
        if len(texts) == 3:
            return texts.lower()
        else:
            return ''
    except:
        return ''

def captcha_send(driver):
    captcha = captcha_solve(driver)
    if len(captcha) == 3:
        driver.find_element_by_xpath('//*[@id="captcha"]').send_keys(captcha)
        driver.find_element_by_xpath(
            '/html/body/div[1]/section/div/div/div[1]/div[2]/div[2]/form/div[4]/input[1]'
        ).click()
        return True
    else:
        driver.refresh()
        return False


def captcha_check(driver):
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located(
        (By.XPATH,
         '/html/body/div[1]/section/div/div/div[1]/div[2]/div[2]/form/div[4]/input[1]')
        )
    )
    print('loaded')
    try:
        result = WebDriverWait(driver, 2).until(ec.visibility_of_element_located(
            (By.XPATH,
             '/html/body/div[1]/section/div/div/div[1]/div[2]/div[3]/h3')
            )
        ).text
    
        if result == 'Không tìm thấy facebook':
            return 'not_found'
        elif result == 'Bạn chưa nhập hoặc đã nhập Sai mã bảo mật vui lòng kiểm tra lại':
            return 'not_send'

    except:
        result = WebDriverWait(driver, 2).until(ec.visibility_of_element_located(
            (By.XPATH,
             '//*[@id="computer"]'))
        ).get_attribute('href')
        
        return result
        

    
def find_fb(driver, sdt='01657078968'):
    
    driver.get(f'https://quetsodienthoai.com/search-phone/?phone={sdt}')
    
    while not captcha_send(driver):
        captcha_send(driver)

    result = captcha_check(driver)
    #if result == 'not_send':
    
    print(result)

#%%

df = pd.read_csv('https://raw.githubusercontent.com/minmax49/MongoDB/master/sample_phone.csv',
                 converters={'ACT_MOBILE':str})

mobiles = df['ACT_MOBILE'].tolist()


results = []
for phone in mobiles[:5]:
    print(phone)
    if phone[:2] == '84':
        phone = '0' + phone[2:]
    
    results.append(find_fb(driver, sdt=phone))  






