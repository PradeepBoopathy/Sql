from tensorflow.keras import callbacks
import pandas as pd
from numpy import asarray
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
import tensorflow as tf



def get_keras_model():
    """Define the model."""
    model = Sequential()
    model.add(Dense(128, input_shape=[512, ], activation='relu'))
    model.add(Dropout(0.1))
    model.add(Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.L1(0.01),
                    activity_regularizer=tf.keras.regularizers.L2(0.01)))
    model.add(Dense(6, activation='softmax'))

    model.compile(loss = 'sparse_categorical_crossentropy', optimizer = 'adam', metrics = ['accuracy'])

    model.summary()
    return model


data =pd.read_csv("wikidatas.csv" ,usecols=["questions" ,"types"])
data = data.sample(frac = 1)
categories =data["types"]

x_train, x_test, y_train ,y_test =train_test_split(data["questions"], categories, shuffle=True)

import tensorflow_hub as hub

embed = hub.load('https://tfhub.dev/google/universal-sentence-encoder/4')
#embed = hub.load('models/universal-sentence-encoder_4')

def get_embeddings(x):
    embeddings = embed(x)
    return asarray(embeddings)


train_encodings = get_embeddings(x_train.to_list())
test_encodings = get_embeddings(x_test.tolist())

y_train = asarray(y_train, dtype="float32")
y_test = asarray(y_test, dtype="float32")

model = get_keras_model()
print(train_encodings.shape)

es = callbacks.EarlyStopping(monitor='accuracy', min_delta=0.000001, patience=10, verbose=0, mode='max', baseline=None, restore_best_weights=True)
plateau = callbacks.ReduceLROnPlateau(monitor='accuracy', factor=0.5, patience=2, verbose=0,
                                        mode='max', min_delta=0.0001, cooldown=0, min_lr=1e-7)
model.fit(train_encodings, y_train, epochs=100, validation_split=0.2, callbacks=[es, plateau])

model.save("Question_Classifier.h5")

score, acc = model.evaluate(test_encodings, y_test)