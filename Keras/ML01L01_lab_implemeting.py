import numpy as np 
from tensorflow.keras.models import Model 
from tensorflow.keras.layers import Input, Dense 
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='tensorflow')

input_layer = Input(shape=(20,))
print(input_layer)

hidden_layer1 = Dense(64, activation='relu')(input_layer) 
hidden_layer2 = Dense(64, activation='relu')(hidden_layer1) 

output_layer = Dense(1, activation='sigmoid')(hidden_layer2) 

model = Model(inputs=input_layer, outputs=output_layer)
model.summary()

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

X_train = np.random.rand(1000, 20) 
y_train = np.random.randint(2, size=(1000, 1)) 
model.fit(X_train, y_train, epochs=10, batch_size=32) 


X_test = np.random.rand(200, 20) 
y_test = np.random.randint(2, size=(200, 1)) 
loss, accuracy = model.evaluate(X_test, y_test) 
print(f'Test loss: {loss}') 
print(f'Test accuracy: {accuracy}') 


#### DROPOUT #####
from tensorflow.keras.layers import Dropout, Dense, Input
from tensorflow.keras.models import Model


input_layer = Input(shape=(20,))
hidden_layer = Dense(64, activation='relu')(input_layer)
dropout_layer = Dropout(rate=0.5)(hidden_layer)
hidden_layer2 = Dense(64, activation='relu')(dropout_layer)
output_layer = Dense(1, activation='sigmoid')(hidden_layer2)
model = Model(inputs=input_layer, outputs=output_layer)
model.summary()


### BATCH NORMALIZATION ####
from tensorflow.keras.layers import BatchNormalization, Dense, Input
from tensorflow.keras.models import Model


input_layer = Input(shape=(20,))
hidden_layer = Dense(64, activation='relu')(input_layer)
batch_norm_layer = BatchNormalization()(hidden_layer)
hidden_layer2 = Dense(64, activation='relu')(batch_norm_layer)
output_layer = Dense(1, activation='sigmoid')(hidden_layer2)
model = Model(inputs=input_layer, outputs=output_layer)
model.summary()