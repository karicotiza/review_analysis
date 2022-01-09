import pandas as pd
import tensorflow as tf


class ToxicityNet:
    def __init__(
            self,
            net_path='C:/Storage/Net/predict_toxicity/predict_toxicity.h5',
            test_path='C:/Storage/Dataset/Commentary/test.csv'
    ):
        self.__net_path = net_path
        self.__test_path = test_path
        self.__model = tf.keras.models.Sequential()
        self.__model.add(tf.keras.layers.Embedding(10000, 128, input_length=50))
        self.__model.add(tf.keras.layers.SpatialDropout1D(0.5))
        self.__model.add(tf.keras.layers.LSTM(40, return_sequences=True))
        self.__model.add(tf.keras.layers.LSTM(40))
        self.__model.add(tf.keras.layers.Dense(6, activation='sigmoid'))
        self.__model.load_weights(self.__net_path)
        self.__train = pd.read_csv(self.__test_path)
        self.__comments = self.__train['comment_text']
        self.__tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=10000)
        self.__tokenizer.fit_on_texts(self.__comments)

    def predict(self, review):
        sequence = self.__tokenizer.texts_to_sequences([review])
        data = tf.keras.preprocessing.sequence.pad_sequences(sequence, maxlen=50)
        return (
            int(round(self.__model.predict(data)[0][0] * 5, 0)),  # Токсичность
            int(round(self.__model.predict(data)[0][1] * 5, 0)),  # Значительная токсичность
            int(round(self.__model.predict(data)[0][2] * 5, 0)),  # Нецензурная лексика
            int(round(self.__model.predict(data)[0][3] * 5, 0)),  # Угроза
            int(round(self.__model.predict(data)[0][4] * 5, 0)),  # Оскорбление
            int(round(self.__model.predict(data)[0][5] * 5, 0)),  # Переход на личности с последующим оскорблением
        )
