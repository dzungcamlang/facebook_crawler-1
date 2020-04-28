# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 12:05:34 2020

@author: nguyenquangminh3
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

from tqdm.auto import tqdm


class Main_driver():

    def __init__(self, user='dream4996@gmail.com', password='minh1234'):
        """
        initialize driver
        """
        try:
            driver = webdriver.Firefox()
            driver.set_window_size(1920, 1080)
        except:
            chrome_path = 'C:/allowApps/chromedriver_win32/chromedriver.exe'
            options = webdriver.ChromeOptions()
            #options.add_argument("--headless")
            options.add_argument("--start-maximized")
            driver = webdriver.Chrome(chrome_path, options=options)

        self.driver = driver
        self.driver.get('https://quetsodienthoai.com/')

        self.driver.find_element_by_xpath(
            '/html/body/div[1]/header/div/div/div/div/div[2]/div/ul/li[4]/a[2]'
        ).click()
        self.driver.find_element_by_xpath(
            '/html/body/div[1]/div/div/div[1]/div[2]/div/div[1]/div/form/div[1]/input[1]'
        ).send_keys(user)
        self.driver.find_element_by_xpath(
            '/html/body/div[1]/div/div/div[1]/div[2]/div/div[1]/div/form/div[1]/input[2]'
        ).send_keys(password)
        self.driver.find_element_by_xpath(
            '/html/body/div[1]/div/div/div[1]/div[2]/div/div[1]/div/form/div[2]/div/div/button'
        ).click()

        self.driver.get('https://quetsodienthoai.com/search-phone/')

        with open('keys.json', 'r') as f:
            self.keys = json.load(f)
        self.value_key = {v:k for k,v in self.keys.items()}

        self.model = load_model('model.h5')

    def _captcha_solve(self):

        capt_im = np.array([0])
        while capt_im.sum() < 1000000:
            image_bytes = WebDriverWait(self.driver, 20).until(ec.visibility_of_element_located(
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
            y_predict = self.model.predict(im)
            captcha.append(self.value_key[np.argmax(y_predict)])

        return "".join(captcha)

    def captcha_send(self):

        captcha = self._captcha_solve()
        if len(captcha) == 3:
            #print(captcha)
            self.driver.find_element_by_xpath('//*[@id="captcha"]').send_keys(captcha)
            self.driver.find_element_by_xpath(
                '/html/body/div[1]/section/div/div/div[1]/div[2]/div[2]/form/div[4]/input[1]'
            ).click()
            return True
        else:
            self.driver.refresh()
            return False

    def captcha_check(self):

        status = ''
        WebDriverWait(self.driver, 20).until(ec.visibility_of_element_located(
            (By.XPATH,
             '/html/body/div[1]/section/div/div/div[1]/div[2]/div[2]/form/div[4]/input[1]')
            )
        )
        try:
            result = WebDriverWait(self.driver, 2).until(ec.visibility_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/section/div/div/div[1]/div[2]/div[3]/h3')
                )
            ).text

            if result == 'Không tìm thấy facebook':
                status = 'not_found'
            elif result == 'Bạn chưa nhập hoặc đã nhập Sai mã bảo mật vui lòng kiểm tra lại':
                status = 'not_send'
        except:
            result = WebDriverWait(self.driver, 3).until(ec.visibility_of_element_located(
                (By.XPATH,
                 '//*[@id="computer"]'))
            ).get_attribute('href')
            status = result

        while str(status) in (['not_send', '', 'None']) :
            self.captcha_check()

        return status

    def find_fb(self, sdt='01657078968'):
        try:
            self.driver.find_element_by_xpath(
                '/html/body/div[1]/section/div/div/div[1]/div[2]/div[2]/form/div[1]/input'
            ).clear()
            self.driver.find_element_by_xpath(
                '/html/body/div[1]/section/div/div/div[1]/div[2]/div[2]/form/div[1]/input'
            ).send_keys(sdt)
            while not self.captcha_send():
                try:
                    self.captcha_send()
                except:
                    continue
            result = self.captcha_check()
            return result

        except:
            self.driver.switch_to.active_element.send_keys(Keys.ENTER)
            self.find_fb(sdt)


if __name__ == '__main__':

    start = time.time()
    main_driver = Main_driver()
    df = pd.read_csv('sample_phone.csv',
                     converters={'ACT_MOBILE':str})

    mobiles = df['ACT_MOBILE'].tolist()
    phones = mobiles[:10]
    pbar = tqdm(total=100)
    rows = len(phones)

    results = []
    for phone in phones:
        print(phone)
        if phone[:2] == '84':
            phone = '0' + phone[2:]
        results.append(main_driver.find_fb(sdt=phone))
        pbar.update(100/rows )

    facebook_df = pd.DataFrame({'phone':phones, 'facebook':results})
    facebook_df.to_csv('facebook-10000.csv', index=None)
    #facebook_df.facebook.fillna('not_found', inplace=True)
    founded = len(facebook_df[facebook_df.facebook != 'not_found'])/ len(facebook_df)

    total_time = round(time.time()/60 - start/60, 2)
    main_driver.driver.close()
    print(f'conpleted in {total_time}, find : {founded*100} %')
    with open('log.txt', 'a+') as file:
        file.write(f'conpleted in {total_time} minutes, find : {founded*100} % \n')