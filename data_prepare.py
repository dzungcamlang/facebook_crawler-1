#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 23:51:36 2020

@author: max
"""


import os
import cv2
import numpy as np
import json

main_path = os.path.dirname(os.path.realpath('__file__'))
files = sorted([f for f in os.listdir(f'{main_path}/single_capt') if len(f) ==1])
keys = {k: i+1 for i, k in enumerate(files)}
files = sorted([f for f in os.listdir(f'{main_path}/single_capt') if len(f) ==1])


def processing():
    datax = []
    datay = []
    path = 'single_capt/'
    file_chils = []
    labels = []
    for file in os.listdir(path) :
        file_chil = path + file +'/'
        labels.append(file)
        file_chils.append(file_chil)

        if len(os.listdir(file_chil)) > 4 :
            for sg_capt in os.listdir(file_chil):
                if sg_capt[-3:] == 'jpg':
                    img = cv2.imread(file_chil+sg_capt, cv2.CV_8UC1)
                    try:
                        datax.append(img.astype(float))
                        datay.append(file)
                    except:
                        pass
    datax = np.array(datax)
    datay = np.array(datay)
    datay = np.array([keys[j] for j in datay])
    return datax, datay

processing()


with open('keys.json', 'w') as f:
    json.dump(keys, f)
with open('keys.json', 'r') as f:
    keys = json.load(f)
