import cv2
import os
import numpy as np

def preprocess_image(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding to create a binary image
    _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours in the binary image
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest contour
    max_contour = max(contours, key=cv2.contourArea)

    # Create a mask with the same shape as the image
    mask = np.zeros_like(gray)

    # Draw the largest contour filled with white color on the mask
    cv2.drawContours(mask, [max_contour], 0, 255, cv2.FILLED)

    # Apply the mask to the original image
    masked_image = cv2.bitwise_and(image, image, mask=mask)

    # Crop the image using the bounding rectangle of the largest contour
    x, y, w, h = cv2.boundingRect(max_contour)
    cropped_image = masked_image[y:y+h, x:x+w]

    return cropped_image

# Specify the input directory, output directory, and extension of the images to process
input_dir = 'C:/Users/Eris Salas/Desktop/inp'
output_dir = 'C:/Users/Eris Salas/Desktop/out'
image_extension = '.jpg'

# Get the list of image files in the input directory
image_files = [f for f in os.listdir(input_dir) if f.endswith(image_extension)]

# Loop over each image file
for filename in image_files:
    # Read the image
    image_path = os.path.join(input_dir, filename)
    image = cv2.imread(image_path)
    
    # Preprocess the image (crop white background)
    processed_image = preprocess_image(image)
    
    # Save the processed image to the output directory
    output_path = os.path.join(output_dir, filename)
    cv2.imwrite(output_path, processed_image)