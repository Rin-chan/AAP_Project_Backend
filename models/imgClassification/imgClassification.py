# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array

import numpy as np
from PIL import Image
import base64
import io

model_s = tf.keras.models.load_model('models/imgClassification/full_model3.h5')
model_j = tf.keras.models.load_model('models/imgClassification/imageclassjaden.h5')

def classify_eWaste_s(filename):

    filepath = 'static/img/'+filename
    # Resize img
    img = load_img(filepath, target_size=(128, 128))
    # Convert image to numpy array
    img_array = img_to_array(img)
    # Model expect data in batches so need to add in batch axis (,0)
    img_array = tf.expand_dims(img_array, 0)
    # Predict
    predictions = model_s(img_array)

    return predictions

# Jaden Part
def classify_eWaste_j(filename):

    filepath = 'static/img/'+filename
    # Resize img
    img = load_img(filepath, target_size=(150, 150))
    # Convert image to numpy array
    img_array = img_to_array(img)
    # Model expect data in batches so need to add in batch axis (,0)
    img_array = tf.expand_dims(img_array, 0)
    # Predict
    predictions = model_j(img_array)

    return predictions

    
def reformat_predictions(predictions, classlisttype):
    
    # Variables
    class_names = []
    highest_percent = 0
    highest_class = ""

    if (classlisttype == 's'):
        class_names = ['desktop', 'laptop', 'mobilephone' , 'modem' , 'others', 'printer', 'refrigerator', 'settopbox' , 'tablet' , 'tv']
    
    elif (classlisttype == 'j'):
        class_names = ['battery', 'lamps', 'others', 'solarpanel' , 'washingmachine_dryer' ]
    

    for tensor_arr in predictions:
        count = 0
        for tensor in tensor_arr:
            if float(tensor) > highest_percent:
                highest_percent = float(tensor)
                highest_class = class_names[count]
            print("%s: %.2f" %(class_names[count],float(tensor) * 100))
            count += 1


    return highest_class, highest_percent

