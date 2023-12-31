from __future__ import print_function


# import os
# os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
from keras.layers import Dense, Activation, Flatten, Dropout
from keras import backend as K
from keras import optimizers
from keras import losses
from tensorflow.keras.optimizers import SGD, Adam, Adagrad
from keras.models import Sequential, Model
from keras.callbacks import ModelCheckpoint, LearningRateScheduler, EarlyStopping
from keras.models import load_model
import matplotlib.pyplot as plt
import numpy as np
import argparse
import random, glob
import os, sys, csv
import cv2
import time, datetime
import utils
import tensorflow as tf

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


# Command line args
parser = argparse.ArgumentParser()
parser.add_argument('--num_epochs', type=int, default=500, help='Number of epochs to train for')
parser.add_argument('--mode', type=str, default="train", help='Select "train", or "predict" mode. \
    Note that for prediction mode you have to specify an image to run the model on.')
parser.add_argument('--image', type=str, default=None, help=  'The image you want to predict on. Only valid in "predict" mode.')
parser.add_argument('--continue_training', type=str2bool, default=False, help='Whether to continue training from a checkpoint')
parser.add_argument('--dataset', type=str, default="dataset", help='Dataset you are using.')
parser.add_argument('--resize_height', type=int, default=224, help='Height of cropped input image to network')
parser.add_argument('--resize_width', type=int, default=224, help='Width of cropped input image to network')
parser.add_argument('--batch_size', type=int, default=64, help='Number of images in each batch')
parser.add_argument('--dropout', type=float, default=0.5, help='Dropout ratio')
parser.add_argument('--h_flip', type=str2bool, default=False, help='Whether to randomly flip the image horizontally for data augmentation')
parser.add_argument('--v_flip', type=str2bool, default=False, help='Whether to randomly flip the image vertically for data augmentation')
parser.add_argument('--rotation', type=float, default=0.0, help='Whether to randomly rotate the image for data augmentation')
parser.add_argument('--zoom', type=float, default=0.0, help='Whether to randomly zoom in for data augmentation')
parser.add_argument('--shear', type=float, default=0.0, help='Whether to randomly shear in for data augmentation')
parser.add_argument('--model', type=str, default="ResNet50", help='Your pre-trained classification model of choice')
args = parser.parse_args()


# Global settings
BATCH_SIZE = args.batch_size
WIDTH = args.resize_width
HEIGHT = args.resize_height
FC_LAYERS = [1024, 1024]
TRAIN_DIR = args.dataset + "/train/"
VAL_DIR = args.dataset + "/val/"

preprocessing_function = None
base_model = None

# Prepare the model
if args.model == "ResNet50":
    from keras.applications.resnet import ResNet50
    from keras.applications.resnet import preprocess_input
    preprocessing_function = preprocess_input
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(HEIGHT, WIDTH, 3))
elif args.model == "InceptionV3":
    from keras.applications.inception_v3 import InceptionV3
    from keras.applications.inception_v3 import preprocess_input
    preprocessing_function = preprocess_input
    base_model = InceptionV3(weights='imagenet', include_top=False, input_shape=(HEIGHT, WIDTH, 3))
elif args.model == "MobileNet":
    from keras.applications.mobilenet import MobileNet
    from keras.applications.mobilenet import preprocess_input
    preprocessing_function = preprocess_input
    base_model = MobileNet(weights='imagenet', include_top=False, input_shape=(HEIGHT, WIDTH, 3))
elif args.model == "VGG16":
    from keras.applications.vgg16 import VGG16
    from keras.applications.vgg16 import preprocess_input
    preprocessing_function = preprocess_input
    base_model = VGG16(weights='imagenet', include_top=False, input_shape=(HEIGHT, WIDTH, 3))
else:
    ValueError("The model you requested is not supported in Keras")

    
if args.mode == "train":
    print("\n***** Begin training *****")
    print("Dataset -->", args.dataset)
    print("Model -->", args.model)
    print("Resize Height -->", args.resize_height)
    print("Resize Width -->", args.resize_width)
    print("Num Epochs -->", args.num_epochs)
    print("Batch Size -->", args.batch_size)

    print("Data Augmentation:")
    print("\tVertical Flip -->", args.v_flip)
    print("\tHorizontal Flip -->", args.h_flip)
    print("\tRotation -->", args.rotation)
    print("\tZooming -->", args.zoom)
    print("\tShear -->", args.shear)
    print("")

    # Create directories if needed
    if not os.path.isdir("checkpoints"):
        os.makedirs("checkpoints")

    # Prepare data generators
    train_datagen =  ImageDataGenerator(rescale=1./255,
      preprocessing_function=preprocessing_function,
      rotation_range=args.rotation,
      shear_range=args.shear,
      zoom_range=args.zoom,
      horizontal_flip=args.h_flip,
      vertical_flip=args.v_flip
    )

    val_datagen = ImageDataGenerator(preprocessing_function=preprocessing_function)

    train_generator = train_datagen.flow_from_directory(TRAIN_DIR, target_size=(HEIGHT, WIDTH), batch_size=BATCH_SIZE)

    validation_generator = val_datagen.flow_from_directory(VAL_DIR, target_size=(HEIGHT, WIDTH), batch_size=BATCH_SIZE)


    # Save the list of classes for prediction mode later
    class_list = utils.get_subfolders(TRAIN_DIR)
    utils.save_class_list(class_list, model_name=args.model, dataset_name=args.dataset)

    finetune_model = utils.build_finetune_model(base_model, dropout=args.dropout, fc_layers=FC_LAYERS, num_classes=len(class_list))

    if args.continue_training:
        finetune_model.load_weights("./checkpoints/" + args.model + ".h5")

    adam = Adam(lr=0.001)
    finetune_model.compile(adam, loss='categorical_crossentropy', metrics=['acc'])

    num_train_images = utils.get_num_files(TRAIN_DIR)
    num_val_images = utils.get_num_files(VAL_DIR)

    def lr_decay(epoch, lr):
        if epoch % 20 == 0 and epoch != 0:
            lr = lr / 2
            print("LR changed to {}".format(lr))
        return lr

    learning_rate_schedule = LearningRateScheduler(lr_decay, verbose=1)

    filepath="./checkpoints/" + args.model + ".h5"
    checkpoint = ModelCheckpoint(filepath, monitor=["acc"], verbose=1, mode='max')
    earlystop = EarlyStopping(monitor='val_loss', min_delta=0.01, patience=20)
    callbacks_list = [checkpoint,earlystop,learning_rate_schedule] #added lr sched to list of callbacks


    history = finetune_model.fit(train_generator, epochs=args.num_epochs, workers=8, steps_per_epoch=num_train_images // BATCH_SIZE, 
        validation_data=validation_generator, validation_steps=num_val_images // BATCH_SIZE, class_weight=None, shuffle=True, callbacks=callbacks_list)

    acc = history.history['acc']
    loss = history.history['loss']
    val_acc = history.history['val_acc']
    val_loss = history.history['val_loss']
    epochs = range(len(acc))

    plt.plot(epochs, acc, 'g', label='Training Accuracy')
    plt.plot(epochs, val_acc, 'b', label='Validation Accuracy')
    plt.title('Training and validation accuracy')
    plt.legend()
    plt.savefig('acc_vs_epochs.png')

    plt.figure()
    plt.plot(epochs, loss, 'g', label='Training loss')
    plt.plot(epochs, val_loss, 'b', label='validation loss')
    plt.title('Training and validation loss')
    plt.legend()
    plt.savefig('loss_vs_epochs.png')

    plt.show()

elif args.mode == "predict":

    if args.image is None:
        ValueError("You must pass an image path when using prediction mode.")

    # Create directories if needed
    if not os.path.isdir("%s"%("Predictions")):
        os.makedirs("%s"%("Predictions"))

    # Read in your image
    image = cv2.imread(args.image,-1)
    save_image = image
    image = np.float32(cv2.resize(image, (HEIGHT, WIDTH)))
    image = preprocessing_function(image.reshape(1, HEIGHT, WIDTH, 3))

    class_list_file = "./checkpoints/" + args.model + ".txt"

    class_list = utils.load_class_list(class_list_file)
    
    finetune_model = utils.build_finetune_model(base_model, dropout=args.dropout, fc_layers=FC_LAYERS, num_classes=len(class_list))
    finetune_model.load_weights("./checkpoints/" + args.model + ".h5")

    # Run the classifier and print results
    st = time.time()

    out = finetune_model.predict(image)

    confidence = out[0]
    class_prediction = list(out[0]).index(max(out[0]))
    class_name = class_list[class_prediction]

    run_time = time.time()-st

    print("Predicted class = ", class_name)
    print("Confidence = ", confidence)
    print("Run time = ", run_time)
    cv2.imwrite("Predictions/" + class_name[0] + ".png", save_image)
