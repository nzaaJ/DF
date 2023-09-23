import platform
import cv2 as cv2
import time as time
import argparse
import sys
import os

import imutils
import tkinter as tk
import tkinter.filedialog
import tkinter.font
import PIL
from PIL import Image
from PIL import ImageTk
import shutil
import random

import numpy as np
import datetime
import serial
platformOS = platform.system()
if platformOS == "Windows":
    SerialData = serial.Serial("com3", 9600, timeout = 0.2)
    Dirdir = "C:/Users/Almuzreen/Documents/Py/Transfer-Learning/checkpoints/"
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
SerialData.write(bytes("I", "utf-8"))
time.sleep(2)
SerialData.write(bytes("K", "utf-8"))
time.sleep(2)

TopCam = 1

if TopCam == 1:
    cap=cv2.VideoCapture(2)
else:
    cap=cv2.VideoCapture(0)
    
root=tk.Tk()    #Main Root
root.state('normal')
root.configure(background='white')

sizex = 800
sizey = 415
posx  = 0
posy  = 0
root.wm_geometry("%dx%d+%d+%d" % (sizex, sizey, posx, posy))
#background of the root

root.title("IMS Watch!")

subFont = tkinter.font.Font(family='Segoe UI', size = 20, weight = "bold")

x=0
xx=0
prc=1
path = ""

def pressed(): #when pressed, 2nd process
    global prc
    prc=2

def tkShowP(Label, Image_Input, Percentage):
  Img = cv2.imread(Image_Input)
  h,w = Img.shape[:2]
  h = int(h*Percentage)
  print(h)
  Img = imutils.resize(Img, height=h)
  cv2.imwrite("IMGSome.jpg", Img)
  nextButtonImg = Image.open("IMGSome.jpg")
  nextButtonImg = ImageTk.PhotoImage(nextButtonImg)
  Label.configure(image=nextButtonImg)
  Label.image = nextButtonImg
  return nextButtonImg

def starts(e=None):
    global prc
    global x
    global slogan
    global path
    global lp
    global xx
    global path
    global lp
    global slogan,TopCam

    if prc==1: #showing only of the video feed

        start_time = time.time()
        ret, capt=cap.read()
        if TopCam == 1:
            capt = capt[50:440,60:640]
        else:
            capt = capt[50:390,44:530]
        cv2.imwrite('IMG.jpg', capt)

        tkShowP(slogan, 'IMG.jpg', 0.65)


    elif prc==2:

        entry1.focus_set()
        path=str(entry1.get())
        path=('Images/' + path)
        entry1.config(state='disabled')

        entry2.focus_set()
        lp=int(entry2.get())
        entry2.config(state='disabled')

        print(path)
        xxx=os.path.exists(path) #deletes the folder if it exists
        if xxx==False:
            os.mkdir(path)
        prc=3

    elif prc==3: #loop for capturing of pictures and saving it
        xx = xx+1
        xxx = (str(datetime.datetime.now().strftime("%Y")) + str(datetime.datetime.now().strftime("%m")) + str(datetime.datetime.now().strftime("%d")) + str(datetime.datetime.now().strftime("%H")) + str(datetime.datetime.now().strftime("%M")) + str(datetime.datetime.now().strftime("%S")) + str(datetime.datetime.now().strftime("%f")))
        ret, capt=cap.read()
        if TopCam == 1:
            capt = capt[0:440,60:640]
        else:
            capt = capt[0:390,44:530]
        
        file=(path + '/img' + xxx + '.jpg')
        cv2.imwrite(file, capt)
        tkShowP(slogan, file, 0.5)

        files = len(os.listdir(path))
        slogan2.configure(text=str(files))
        slogan2.text = str(files)

        if xx==lp:
            prc=1
            entry1.config(state='normal')
            entry2.config(state='normal')
            xx=0

    root.after(5,starts)

entry1=tk.Entry(root)
entry1.place(x=500,y=60)

entry2=tk.Entry(root)
entry2.place(x=500,y=80)

button1=tk.Button(root, text="Play", command=pressed)
button1.place(x=500,y=100)

slogan = tk.Label(root, text='A',
                  font = subFont, bg='white',
                  borderwidth=0)
slogan.place(x=30, y=60)

slogan2 = tk.Label(root, text='0',
                   font = subFont, bg='white',
                   borderwidth=0)
slogan2.place(x=500, y=340)

root.after(5,starts)
root.mainloop()

SerialData.write(bytes("J", "utf-8"))
time.sleep(2)
SerialData.write(bytes("L", "utf-8"))
time.sleep(2)