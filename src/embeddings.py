import os
import re
from math import floor, ceil

import numpy as np
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import one_hot
from keras.models import Sequential
from keras.layers import Embedding, Flatten, Dense

# Define documents
"""docs = ['Well done!', 'Good work', 'Great effort', 'nice work', 'Excellent!',
        'Weak', 'Poor effort!', 'not good', 'poor work', 'Could have done better.']
"""
docs = []
main_dir = os.getcwd()
with open(main_dir + '/../corpus/jawiki-20181001-corpus.txt') as f:
    for line in f:
        l = " ".join(line)
        docs.append(l)
print(docs[:10])
# Define class labels
own_embedding_vocab_size = 1024*16
labels = [1 for i in range(floor(len(docs)/2))] + [0 for i in range(ceil(len(docs)/2))]

encoded_docs_oe = [one_hot(d, own_embedding_vocab_size, split=' ', filters='') for d in docs]
print(encoded_docs_oe[:10])

maxlen = 60
padded_docs_oe = pad_sequences(encoded_docs_oe, maxlen=maxlen, padding='post')
print(padded_docs_oe)

model = Sequential()
model.add(Embedding(input_dim=own_embedding_vocab_size, # 10
                    output_dim=512,
                    input_length=maxlen))
model.add(Flatten())
model.add(Dense(1, activation='sigmoid'))

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])  # Compile the model
print(model.summary())  # Summarize the model
model.fit(padded_docs_oe, labels, epochs=50, verbose=1)  # Fit the model
loss, accuracy = model.evaluate(padded_docs_oe, labels, verbose=1)  # Evaluate the model
print('Accuracy: %0.3f' % accuracy)
