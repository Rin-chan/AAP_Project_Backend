# TensorFlow and tf.keras
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Input, Lambda
from tensorflow.keras import backend as K

import numpy as np
from PIL import Image
import base64
import io

def create_shared_network(input_shape):
    model = Sequential()
    model.add(Conv2D(filters=128, kernel_size=(3,3), activation='relu', input_shape=input_shape))
    model.add(MaxPooling2D())
    model.add(Conv2D(filters=64, kernel_size=(3,3), activation='relu'))
    model.add(Flatten())
    model.add(Dense(units=128, activation='sigmoid'))
    return model

def euclidean_distance(vectors):
    vector1, vector2 = vectors
    sum_square = K.sum(K.square(vector1 - vector2), axis=1, keepdims=True)
    return K.sqrt(K.maximum(sum_square, K.epsilon()))

def generateDiss(img1, img2):
    input_shape = (112, 92, 1)
    shared_network = create_shared_network(input_shape)
    input_top = Input(shape=input_shape)
    input_bottom = Input(shape=input_shape)
    output_top = shared_network(input_top)
    output_bottom = shared_network(input_bottom)
    
    distance = Lambda(euclidean_distance, output_shape=(1,))([output_top, output_bottom])
    model = Model(inputs=[input_top, input_bottom], outputs=distance)

    # Load pretrained model
    model.load_weights("models/faceVerification/siamese.h5")

    result = False
    
    # Convert base64 image to NumPy array
    base64_decoded1 = base64.b64decode(img1)
    image1 = Image.open(io.BytesIO(base64_decoded1)).convert('L')
    image1 = image1.resize((92, 112))
    img1 = img_to_array(image1).astype('float32')/255
    img1 = np.expand_dims(img1, axis=0)
    
    base64_decoded2 = base64.b64decode(img2)
    image2 = Image.open(io.BytesIO(base64_decoded2)).convert('L')
    image2 = image2.resize((92, 112))
    img2 = img_to_array(image2).astype('float32')/255
    img2 = np.expand_dims(img2, axis=0)

    # Find dissimilarity
    dissimilarity = model.predict([img1, img2])[0][0]
    
    if (dissimilarity < 0.5):
        result = True
        
    return result
