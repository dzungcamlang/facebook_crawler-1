#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 23:50:57 2020

@author: max
"""



import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.utils import np_utils
from keras.datasets import mnist
import sklearn.preprocessing
from sklearn.model_selection import train_test_split
import json
import data_prepare
#---


X, y = data_prepare.processing()
X = X.reshape(X.shape[0], X.shape[1],X.shape[2], 1)
Y = np_utils.to_categorical(y,len(np.unique(y))+2)

X_train, X_val, y_train, y_val = train_test_split(X, Y, test_size=0.15, random_state=42)

# 5. Định nghĩa model
model = Sequential()
# Thêm Convolutional layer với 36 kernel, kích thước kernel 3*3
# dùng hàm sigmoid làm activation và chỉ rõ input_shape cho layer đầu tiên
model.add(Conv2D(36, (3, 3), activation='relu', input_shape=(X.shape[1],X.shape[2],1)))
# Thêm Convolutional layer
model.add(Conv2D(36, (3, 3), activation='relu'))
# Thêm Max pooling layer
model.add(MaxPooling2D(pool_size=(2,2)))
# Flatten layer chuyển từ tensor sang vector
model.add(Flatten())
# Thêm Fully Connected layer với 128 nodes và dùng hàm sigmoid
model.add(Dense(128, activation='sigmoid'))
# Output layer với 10 node và dùng softmax function để chuyển sang xác xuất.
model.add(Dense(len(np.unique(y))+2, activation='softmax'))

    
model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])


# 7. Thực hiện train model với data
numOfEpoch = 150
H = model.fit(X_train, y_train, validation_data=(X_val, y_val),
          batch_size=600, epochs=numOfEpoch, verbose=1)

# 8. Vẽ đồ thị loss, accuracy của traning set và validation set
fig = plt.figure()

plt.plot(np.arange(0, numOfEpoch), H.history['loss'], label='training loss')
plt.plot(np.arange(0, numOfEpoch), H.history['val_loss'], label='validation loss')
plt.plot(np.arange(0, numOfEpoch), H.history['accuracy'], label='accuracy')
plt.plot(np.arange(0, numOfEpoch), H.history['val_accuracy'], label='validation accuracy')
plt.title('Accuracy and Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss|Accuracy')
plt.legend()

plt.figure()
plt.imshow(X_train[0].reshape(X.shape[1],X.shape[2]), cmap='gray')
y_predict = model.predict(X_train[0].reshape(1,X.shape[1],X.shape[2],1))

with open('keys.json', 'r') as f:
    keys = json.load(f) 
value_key = {v:k for k,v in keys.items()}

print('Giá trị dự đoán: ', np.argmax(y_predict),':', value_key[np.argmax(y_predict)])

model.save("model.h5")