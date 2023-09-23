import platform
platformOS = platform.system()
import matplotlib.pyplot as plt
import numpy as np
import cv2
from keras.layers import Dense, Flatten, Dropout
from keras.models import Model
import glob
import os, sys, csv
import time
import serial
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.font
import ImportantFunctions as IF

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
if platformOS == "Windows":
    SerialData = serial.Serial("com3", 9600, timeout = 0.2)
    Dirdir = "C:\Users\Eris Salas\Desktop\PD2\TransferLearning"
    Dirdir2 = ""
else:
    Dirdir = "/home/pi/Desktop/Transfer-Learning-Suite-master/checkpoints/"
    Dirdir2 = "/home/pi/Desktop/Main/"
    SerialData = serial.Serial("/dev/ttyACM0", 9600, timeout = 0.2)
    import RPi.GPIO as GPIO
    Buttton = 2
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(Buttton, GPIO.IN,pull_up_down=GPIO.PUD_UP)
    
SerialData.setDTR(False)
time.sleep(1)
SerialData.flushInput()
SerialData.setDTR(True)
time.sleep(2)

# def save_class_list(class_list, model_name, dataset_name):
#     class_list.sort()
#     target=open("./checkpoints/" + model_name + ".txt",'w')
#     for c in class_list:
#         target.write(c)
#         target.write("\n")

def load_class_list(class_list_file):
    class_list = []
    with open(class_list_file, 'r') as csvfile:
        file_reader = csv.reader(csvfile)
        for row in file_reader:
            class_list.append(row)
    class_list.sort()
    return class_list

def build_finetune_model(base_model, dropout, fc_layers, num_classes):
    for layer in base_model.layers:
        layer.trainable = False

    x = base_model.output
    x = Flatten()(x)
    for fc in fc_layers:
        x = Dense(fc, activation='relu')(x) # New FC layer, random init
        x = Dropout(dropout)(x)

    predictions = Dense(num_classes, activation='softmax')(x) # New softmax layer
    
    finetune_model = Model(inputs=base_model.input, outputs=predictions)

    return finetune_model

# def plot_training(history):
#     print(history.history.keys())
#     acc = history.history['acc']
#     loss = history.history['loss']
#     epochs = range(len(acc))

#     plt.plot(epochs, acc, 'r.')
#     plt.plot(epochs, loss, 'r')
#     plt.title('Training and validation accuracy')

#     plt.figure()
#     plt.plot(epochs, loss, 'r.')
#     plt.plot(epochs, val_loss, 'r-')
#     plt.title('Training and validation loss')
#     plt.show()
#     plt.savefig('acc_vs_epochs.png')


fileRead = open(Dirdir2 + "model.txt", "r+")
fileRead = fileRead.read()


if fileRead == "0":
    from keras.applications.resnet import ResNet50
    from keras.applications.resnet import preprocess_input
    preprocessing_function = preprocess_input
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    
    class_list = load_class_list(Dirdir + "ResNet50.txt")
    finetune_model = build_finetune_model(base_model, dropout=1e-3, fc_layers=[1024,1024], num_classes=len(class_list))
    finetune_model.load_weights(Dirdir + "ResNet50.h5")
elif fileRead == "1":
    from keras.applications.inception_v3 import InceptionV3
    from keras.applications.inception_v3 import preprocess_input
    preprocessing_function = preprocess_input
    base_model = InceptionV3(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    
    class_list = load_class_list(Dirdir + "InceptionV3.txt")
    finetune_model = build_finetune_model(base_model, dropout=1e-3, fc_layers=[1024,1024], num_classes=len(class_list))
    finetune_model.load_weights(Dirdir + "InceptionV3.h5")
elif fileRead == "2":
    from keras.applications.mobilenet import MobileNet
    from keras.applications.mobilenet import preprocess_input
    preprocessing_function = preprocess_input
    base_model = MobileNet(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    
    class_list = load_class_list(Dirdir + "MobileNet.txt")
    finetune_model = build_finetune_model(base_model, dropout=1e-3, fc_layers=[1024,1024], num_classes=len(class_list))
    finetune_model.load_weights(Dirdir + "MobileNet.h5")

def classifyImage(Image_Path):
    global class_list, finetune_model
    image = cv2.imread(Image_Path,-1)
    image = np.float32(cv2.resize(image, (224, 224)))
    image = preprocessing_function(image.reshape(1, 224, 224, 3))
    
    st = time.time()
    
    out = finetune_model.predict(image)    

    confidence = out[0]
    class_prediction = list(out[0]).index(max(out[0]))
    class_name = class_list[class_prediction]
    confidence = confidence[class_prediction]
    run_time = time.time()-st

    Prediction = class_name[0]
    Prediction = Prediction[0].upper() + Prediction[1::]
    return Prediction, round(confidence*100,2), round(run_time,2)

def find(P):
    lili=[[3,"Premium"],[2,"Classa"],[1,"Rejected"],[0,"Others"]]
    for i in lili:
        if P == i[1]:
            return i[0]

# def find2(P):
#     lili=[[3,"Premium"],[2,"Classa"],[1,"Rejected"]]
#     for i in lili:
#         if P == i[0]:
#             return i[1]

import cv2
import threading
# import eel
# eel.init('GUI')

def ListCameraDevices():
    # checks the first 10 indexes.
    index = 0
    arr = []
    i = 10
    while i > 0:
        cap = cv2.VideoCapture(index)
        if cap.read()[0]:
            arr.append(index)
            cap.release()
        index += 1
        i -= 1
    return arr

Cams = ListCameraDevices()
# Prediction,Percentage,_ = classifyImage(Dirdir2 + "GUI/Video.jpg")

print(Cams)
if platformOS == "Windows":
    cap = cv2.VideoCapture(Cams[0])
    cap2 = cv2.VideoCapture(Cams[1])

ToIdentify = 0
Bypass = ""
root=tk.Tk()    #Main Root
root.attributes('-fullscreen', True)
##root.state('normal')
root.configure(background='white')
subFont1 = tkinter.font.Font(family='Segoe UI', size = 20, weight = "bold")
subFont2 = tkinter.font.Font(family='Segoe UI', size = 10, weight = "bold")

SerialData.write(bytes("X", "utf-8"))

def MainLoop():
    global ToIdentify,cap, cap2, Bypass
    if platformOS == "Windows":
        _, frame = cap.read()
        cv2.imwrite(Dirdir2 + "GUI/Video.jpg",frame)
        _, frame2 = cap2.read()
        cv2.imwrite(Dirdir2 + "GUI/Video2.jpg",frame2)
    else:
        if (GPIO.input(Buttton) == False):
            SerialData.write(bytes("Z", "utf-8")) 
            time.sleep(1)
            os.system("sudo shutdown -h now")
        while True:
            try:
                cap = cv2.VideoCapture(2)
                _, frame = cap.read()
                _, frame = cap.read()
                _, frame = cap.read()
                _, frame = cap.read()
                frame = frame[0:440,60:640]
                cv2.imwrite(Dirdir2 + "GUI/Video.jpg",frame)
                cap.release()
                break
            except:
                pass
        
        while True:
            try:
                cap2 = cv2.VideoCapture(0)
                _, frame2 = cap2.read()
                _, frame2 = cap2.read()
                _, frame2 = cap2.read()
                _, frame2 = cap2.read()
                frame2 = frame2[0:390,44:530]
                cv2.imwrite(Dirdir2 + "GUI/Video2.jpg",frame2)
                cap2.release()
                break
            except:
                pass
            
    reading = SerialData.read().decode("utf-8")
    # print(reading)
    if reading == 'A' or (ToIdentify == 1):
        ToIdentify = 0
        Prediction,Percentage,_ = classifyImage(Dirdir2 + "GUI/Video.jpg")
        cv2.imwrite(Dirdir2 + "GUI/Video"+str(int(time.time()))+".jpg",frame)
        Prediction2,Percentage2,_ = classifyImage(Dirdir2 + "GUI/Video2.jpg")
        cv2.imwrite(Dirdir2 + "GUI/Video2"+str(int(time.time()))+".jpg",frame2)
        
        index1 = find(Prediction)
        index2 = find(Prediction2)
        print([Prediction,Percentage],[Prediction2,Percentage2])
        
        if index1 < index2:
            Prediction, Percentage = Prediction, Percentage
        elif index1 == index2:
            if Percentage > Percentage2:
                Percentage = Percentage
            else:
                Percentage = Percentage2
        else:
            Prediction, Percentage = Prediction2, Percentage2
        print("Final: " + Prediction, Percentage)
        if Bypass != "":
            if Bypass == "P":
                Prediction = "Premium"
            if Bypass == "C":
                Prediction = "Classa"
            if Bypass == "R":
                Prediction = "Rejected"
            if Bypass == "O":
                Prediction = "Others"
                
        if Prediction == "Premium":
            SerialData.write(bytes("1", "utf-8"))
        elif Prediction == "Classa":
            Prediction = "Class A"
            SerialData.write(bytes("2", "utf-8"))
        elif Prediction == "Rejected":
            SerialData.write(bytes("3", "utf-8"))
        elif Prediction == "Others":
            SerialData.write(bytes("4", "utf-8"))
              
        Percentage = str(Percentage) + "%"
        Label1.configure(text="Classification: " + Prediction)
        Label2.configure(text="Percentage: " + str(Percentage))
    
    if reading == 'B':
        Prediction,Percentage,_ = classifyImage(Dirdir2 + "GUI/Video.jpg")
        cv2.imwrite(Dirdir2 + "GUI/Video"+str(int(time.time()))+".jpg",frame)
        Prediction2,Percentage2,_ = classifyImage(Dirdir2 + "GUI/Video2.jpg")
        cv2.imwrite(Dirdir2 + "GUI/Video2"+str(int(time.time()))+".jpg",frame2)

        if Prediction == "Others" or Prediction2 == "Others":
            SerialData.write(bytes("4", "utf-8"))
        else:
            SerialData.write(bytes("3", "utf-8"))

        Prediction = "Rejected"
        Percentage = "by weight"
        Label1.configure(text="Classification: " + Prediction)
        Label2.configure(text="Percentage: " + str(Percentage))
    
        
    try:
        IF.tkShow(Video1, "GUI/Video.jpg", 0.5)
        IF.tkShow(Video2, "GUI/Video2.jpg", 0.55)
    except:
        pass
    print(Bypass)
    root.after(5,MainLoop)
    

# @eel.expose
def IdentifyNow():
    global ToIdentify
    ToIdentify = 1

# @eel.expose
def Py_Save_Model_Selection(n):
    f = open(Dirdir2 + "model.txt", "w+")
    f.write(n) 
    f.close()
    cap.release()
    cap2.release()
    os.execv(sys.executable, ['python'] + sys.argv)
    
# @eel.expose
def Py_Request_Model_No():
    return fileRead

# @eel.expose
def PY_Bypass(n):
    global Bypass
    Bypass = n


GUI1 = tk.Frame(root)
GUI1.pack()

IF.Create_White_Screen("bg1.png", root.winfo_screenwidth(), root.winfo_screenheight())
Background = tk.Label(GUI1, text='',font = subFont1, bg='white',bd=0)
Background.pack()
IF.tkShow(Background, "bg1.png", 1)

BaseY = 290
Label1 = tk.Label(GUI1, text='Classification: ', font = subFont2, bg='white')
Label1.place(x=30,y=BaseY+0*30)

Label2 = tk.Label(GUI1, text='Percentage: ', font = subFont2, bg='white')
Label2.place(x=30,y=BaseY+1*30)

def Change1():
    Py_Save_Model_Selection("0")
    
def Change2():
    Py_Save_Model_Selection("1")
    
def Change3():
    Py_Save_Model_Selection("2")

ResnetButton = tk.Button(GUI1, text='Resnet', font = subFont2, command=Change1, height = 1, width=10)
ResnetButton.place(x=400,y=BaseY+0*30)

InceptionButton = tk.Button(GUI1, text='Inception', font = subFont2, command=Change2, height = 1, width=10)
InceptionButton.place(x=400,y=BaseY+1*30)

MobilenetButton = tk.Button(GUI1, text='MobileNet', font = subFont2, command=Change3, height = 1, width=10)
MobilenetButton.place(x=400,y=BaseY+2*30)

if fileRead == "0":
    ResnetButton.configure(background="#AAAAAA")
if fileRead == "1":
    InceptionButton.configure(background="#AAAAAA")
if fileRead == "2":
    MobilenetButton.configure(background="#AAAAAA")

Video1 = tk.Label(GUI1, text='', font = subFont1, bg='white')
Video1.place(x=30,y=20)

Video2 = tk.Label(GUI1, text='', font = subFont1, bg='white')
Video2.place(x=400,y=20)

def key_input(event):
        global Bypass
        key_press = event.char
        sleep_time=0.030
        if key_press.lower()=="p":
                Bypass = "P"
        elif key_press.lower()=="c":
                Bypass = "C"
        elif key_press.lower()=="r":
                Bypass = "R"
        elif key_press.lower()=="o":
                Bypass = "O"
        elif key_press.lower()=="d":
                Bypass = ""


root.after(5,MainLoop)
root.bind("<KeyPress>", key_input)
root.mainloop()
