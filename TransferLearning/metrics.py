import numpy as np
from sklearn.metrics import classification_report
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# load saved model
model = load_model('C:/Users/Eris Salas/Desktop/Codes/TransferLearning/checkpoints/ResNet50.h5')

# set up test data generator
test_datagen = ImageDataGenerator(rescale=1./255)

# set up test data
test_dir = 'C:/Users/Eris Salas/Desktop/Codes/TransferLearning/dataset/test'
test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=(224, 224),
        batch_size=1,
        class_mode='categorical',
        shuffle=False)

# evaluate model on test set
test_loss, test_acc = model.evaluate(test_generator, verbose=1)
print('Test accuracy:', test_acc)

# generate predictions for test set
test_generator.reset()
preds = model.predict(test_generator, verbose=1)
predicted_classes = np.argmax(preds, axis=1)

# get true class labels
true_classes = test_generator.classes
class_labels = list(test_generator.class_indices.keys())

# print classification report
print('Classification Report:')
print(classification_report(true_classes, predicted_classes, target_names=class_labels)) 