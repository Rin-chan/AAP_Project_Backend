# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array

import numpy as np
from PIL import Image
import base64
import io

model = tf.keras.models.load_model('models/imgClassification/imgClassification.h5')
# model1 = tf.keras.models.load_model('models/imgClassification/imageclass.h5')

def classify_eWaste(filename):

    filepath = 'static/img/'+filename
    # Resize img
    img = load_img(filepath, target_size=(128, 128))
    # Convert image to numpy array
    img_array = img_to_array(img)
    # Model expect data in batches so need to add in batch axis (,0)
    img_array = tf.expand_dims(img_array, 0)
    # Predict
    predictions = model(img_array)

    return predictions

# Jaden Part
# def classify_eWaste(filename):

#     filepath = 'static/img/'+filename
#     # Resize img
#     img = load_img(filepath, target_size=(150, 150))
#     # Convert image to numpy array
#     img_array = img_to_array(img)
#     # Model expect data in batches so need to add in batch axis (,0)
#     img_array = tf.expand_dims(img_array, 0)
#     # Predict
#     predictions = model1(img_array)

#     return predictions

    
def reformat_predictions(predictions):
    # Variables
    class_names = ['desktop', 'laptop', 'mobilephone' , 'modem' , 'printer', 'refrigerator', 'settopbox' , 'tablet' , 'tv']
    class_names1 = ['battery', 'lamps', 'solarpanel' , 'washingmachine_dryer' ]
    highest_percent = 0
    highest_class = ""

    for tensor_arr in predictions:
        count = 0
        for tensor in tensor_arr:
            if float(tensor) > highest_percent:
                highest_percent = float(tensor)
                highest_class = class_names[count]
            print("%s: %.2f" %(class_names[count],float(tensor) * 100))
            count += 1
    
    if (highest_percent * 100) <= 40.0:
        highest_class = 'non-regulated' 

    return highest_class

