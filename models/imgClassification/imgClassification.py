# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array

import numpy as np
from PIL import Image
import base64
import io

model = tf.keras.models.load_model('models/imgClassification/imgClassification.h5')

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

    
def reformat_predictions(predictions):
    # Variables
    class_names = ['desktop', 'laptop', 'mobilephone' , 'modem' , 'printer', 'refrigerator', 'settopbox' , 'tablet' , 'tv']
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
    
    if (highest_percent * 100) <= 50.0:
        highest_class = 'non-regulated' 

    return highest_class

