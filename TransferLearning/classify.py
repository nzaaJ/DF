from __future__ import print_function
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
from keras.layers import Dense, Activation, Flatten, Dropout
from keras import backend as K
from keras import optimizers
from keras import losses
from paramiko import WarningPolicy
from tensorflow.keras.optimizers import SGD, Adam
from keras.models import Sequential, Model
from keras.callbacks import ModelCheckpoint, LearningRateScheduler
from keras.models import load_model
import matplotlib.pyplot as plt
import numpy as np
import argparse
import random, glob
import os, sys, csv
import cv2
import time, datetime
import utils

ModelUsed = "ResNet50"

if ModelUsed == "VGG16":
    from keras.applications.vgg16 import VGG16
    from keras.applications.vgg16 import preprocess_input
    preprocessing_function = preprocess_input
    base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
elif ModelUsed == "ResNet50":
    from keras.applications.resnet import ResNet50
    from keras.applications.resnet import preprocess_input
    preprocessing_function = preprocess_input
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
elif ModelUsed == "InceptionV3":
    from keras.applications.inception_v3 import InceptionV3
    from keras.applications.inception_v3 import preprocess_input
    preprocessing_function = preprocess_input
    base_model = InceptionV3(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
elif ModelUsed == "MobileNet":
    from keras.applications.mobilenet import MobileNet
    from keras.applications.mobilenet import preprocess_input
    preprocessing_function = preprocess_input
    base_model = MobileNet(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

class_list_file = "./checkpoints/" + ModelUsed + ".txt"
class_list = utils.load_class_list(class_list_file)

finetune_model = utils.build_finetune_model(base_model, dropout=1e-3, fc_layers=[1024,1024], num_classes=len(class_list))
finetune_model.load_weights("./checkpoints/" + ModelUsed + ".h5")

def classifyImage(Image_Path):
    global class_list, finetune_model
    image = cv2.imread(Image_Path,-1)
    save_image = image
    image = np.float32(cv2.resize(image, (224, 224)))
    image = preprocessing_function(image.reshape(1, 224, 224, 3))
    
    st = time.time()
    out = finetune_model.predict(image)

    confidence = out[0]
    class_prediction = list(out[0]).index(max(out[0]))
    class_name = class_list[class_prediction]
    confidence = confidence[class_prediction]
    run_time = time.time()-st

    cv2.imwrite("Predictions/" + class_name[0] + ".png", save_image)
    Prediction = class_name[0]
    
    return Prediction, round(confidence*100,2), round(run_time,2)
    
print(classifyImage("img.jpg"))
print(classifyImage("img2.jpg"))
print(classifyImage("img3.jpg"))