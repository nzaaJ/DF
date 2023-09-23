import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img

datagen = ImageDataGenerator(
    rotation_range=20,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    vertical_flip=True,
    fill_mode='nearest')

# path to the folder with input images
input_folder = 'C:/Users/Eris Salas/Desktop/Codes/TransferLearning/Dragon Fruit Dataset/Reject'
# path to the folder where augmented images will be saved
output_folder = 'C:/Users/Eris Salas/Desktop/Codes/TransferLearning/augment/Reject'
# number of copies to be made for each image
n_copies = 69

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# loop through all the images in the input folder
for filename in os.listdir(input_folder):
    # load the image
    img = load_img(os.path.join(input_folder, filename))
    # convert to numpy array
    x = img_to_array(img)
    # reshape to (1, height, width, channels)
    x = x.reshape((1,) + x.shape)
    # initialize the counter
    i = 0
    # generate n_copies augmented images for the input image
    for batch in datagen.flow(x, batch_size=1, save_to_dir=output_folder, save_prefix='aug_', save_format='jpg'):
        i += 1
        if i >= n_copies:
            break
    # print the progress
    print(f"Finished augmenting {filename} ({i} images generated).")