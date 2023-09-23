directory=""

import cv2
import imutils
from PIL import Image
from PIL import ImageTk
import numpy as np
import tkinter as tk


#Tkinter---------------------------------------------------------------------------
def tkShow(Label, Image_Input, Percentage):
  Img = cv2.imread(directory + Image_Input)
  h,w = Img.shape[:2]
  h = int(h*Percentage)
  Img = imutils.resize(Img, height=h)
  cv2.imwrite("IMG.jpg", Img)
  nextButtonImg = Image.open("IMG.jpg")
  nextButtonImg = ImageTk.PhotoImage(nextButtonImg)
  Label.configure(image=nextButtonImg)
  Label.image = nextButtonImg
  return nextButtonImg

from PIL import Image, ImageDraw, ImageFont

def imwrite(file_name, img):
    cv2.imwrite(directory + file_name,img)

def Create_White_Screen(Output_File, DimX, DimY):
    img = np.ones((DimY, DimX,3))*int(255)
    imwrite(Output_File,img)

