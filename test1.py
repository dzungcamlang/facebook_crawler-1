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
import matplotlib.pyplot as plt
import json
from keras.models import load_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys

try:
    driver = webdriver.Firefox()
    driver.set_window_size(1920, 1080)
except:
    chrome_path = 'C:/allowApps/chromedriver_win32/chromedriver.exe'
    options = webdriver.ChromeOptions()
    #PROXY = "socks5://127.0.0.1:9150"
    #options.add_argument('--proxy-server=10.30.8.38:8080')
    options.add_argument("--headless")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(chrome_path,chrome_options=options)

driver.get('https://quetsodienthoai.com/')

user = 'dream4996@gmail.com'
password = 'minh1234'
sdt='01657078968'
model = load_model('model.h5')

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

with open('keys.json', 'r') as f:
    keys = json.load(f)
value_key = {v:k for k,v in keys.items()}

driver.get(f'https://quetsodienthoai.com/search-phone/?phone={sdt}')
#%%
def captcha_solve(driver):

    capt_im = np.array([0])
    while capt_im.sum() < 1000000:
        image_bytes = WebDriverWait(driver, 20).until(ec.visibility_of_element_located(
        (By.XPATH,
         '//*[@id="imgCaptcha"]')
        )
        ).screenshot_as_png
        capt_im = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), 1)

    ims = [capt_im[8:27, 33:45], capt_im[8:27, 47:59], capt_im[8:27, 61:73]]
    captcha = []
    for im in ims:
        im =cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        im = im.reshape((1, 19, 12, 1))
        y_predict = model.predict(im)
        captcha.append(value_key[np.argmax(y_predict)])

    return "".join(captcha)


captcha_solve(driver)

def captcha_send(driver):

    captcha = captcha_solve(driver)
    if len(captcha) == 3:
        #print(captcha)
        driver.find_element_by_xpath('//*[@id="captcha"]').send_keys(captcha)
        driver.find_element_by_xpath(
            '/html/body/div[1]/section/div/div/div[1]/div[2]/div[2]/form/div[4]/input[1]'
        ).click()
        return True
    else:
        driver.refresh()
        return False


def captcha_check(driver):
    status = ''
    WebDriverWait(driver, 20).until(ec.visibility_of_element_located(
        (By.XPATH,
         '/html/body/div[1]/section/div/div/div[1]/div[2]/div[2]/form/div[4]/input[1]')
        )
    )
    try:
        result = WebDriverWait(driver, 2).until(ec.visibility_of_element_located(
            (By.XPATH,
             '/html/body/div[1]/section/div/div/div[1]/div[2]/div[3]/h3')
            )
        ).text

        if result == 'Không tìm thấy facebook':
            status = 'not_found'
        elif result == 'Bạn chưa nhập hoặc đã nhập Sai mã bảo mật vui lòng kiểm tra lại':
            status = 'not_send'

    except:
        result = WebDriverWait(driver, 2).until(ec.visibility_of_element_located(
            (By.XPATH,
             '//*[@id="computer"]'))
        ).get_attribute('href')
        status = result

    while status in ('not_send', '') or status == None:
        captcha_check(driver)
    return status


def find_fb(driver, sdt='01657078968'):
    try:
        driver.find_element_by_xpath(
            '/html/body/div[1]/section/div/div/div[1]/div[2]/div[2]/form/div[1]/input'
        ).clear()
        driver.find_element_by_xpath(
            '/html/body/div[1]/section/div/div/div[1]/div[2]/div[2]/form/div[1]/input'
        ).send_keys(sdt)
        while not captcha_send(driver):
            try:
                captcha_send(driver)
            except:
                continue
        result = captcha_check(driver)

        return result
    except:
        driver.switch_to.active_element.send_keys(Keys.ENTER)



#%%

df = pd.read_csv('sample_phone.csv',
                 converters={'ACT_MOBILE':str})

mobiles = df['ACT_MOBILE'].tolist()
phones = mobiles[:100]

results = []
for phone in phones:
    print(phone)
    if phone[:2] == '84':
        phone = '0' + phone[2:]

    results.append(find_fb(driver, sdt=phone))


facebook_df = pd.DataFrame({'phone':phones,
              'facebook':results})

print(facebook_df)


