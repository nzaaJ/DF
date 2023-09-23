# Layers
from keras.layers import Dense, Activation, Flatten, Dropout
from keras import backend as K

# Other
from keras import optimizers
from keras import losses
# from tensorflow.keras.optimizers import SGD, Adam
from keras.models import Sequential, Model
from keras.callbacks import ModelCheckpoint, LearningRateScheduler
from keras.layers.normalization import BatchNormalization
from keras.models import load_model
from tensorflow.keras.regularizers import l2

# Utils
import matplotlib.pyplot as plt
import numpy as np
import argparse
import random, glob
import os, sys, csv
import cv2
import time, datetime


def save_class_list(class_list, model_name, dataset_name):
    class_list.sort()
    target=open("./checkpoints/" + model_name + ".txt",'w')
    for c in class_list:
        target.write(c)
        target.write("\n")

def load_class_list(class_list_file):
    class_list = []
    with open(class_list_file, 'r') as csvfile:
        file_reader = csv.reader(csvfile)
        for row in file_reader:
            class_list.append(row)
    class_list.sort()
    return class_list

# Get a list of subfolders in the directory
def get_subfolders(directory):
    subfolders = os.listdir(directory)
    subfolders.sort()
    return subfolders

# Get number of files by searching directory recursively
def get_num_files(directory):
    if not os.path.exists(directory):
        return 0
    cnt = 0
    for r, dirs, files in os.walk(directory):
        for dr in dirs:
            cnt += len(glob.glob(os.path.join(r, dr + "/*")))
    return cnt

# Add on new FC layers with dropout for fine tuning
def build_finetune_model(base_model, dropout, fc_layers, num_classes):
    for layer in base_model.layers:
        layer.trainable = False

    x = base_model.output
    x = Flatten()(x)
    for fc in fc_layers:
        # x = Dense(fc, activation='relu', kernel_regularizer=l2(0.0001))(x) # New FC layer, random init (also added L2 Regularizer)
        x = Dense(fc, activation='relu')(x) #without L2 regularization
        # x = BatchNormalization()(x)
        x = Dropout(dropout)(x)

    predictions = Dense(num_classes, activation='softmax')(x) # New softmax layer
    
    finetune_model = Model(inputs=base_model.input, outputs=predictions)

    return finetune_model