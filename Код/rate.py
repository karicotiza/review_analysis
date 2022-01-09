import numpy as np
import tensorflow as tf
from transformers import BertConfig, BertTokenizerFast


class RateNet:
    def __init__(self, path='C:/Storage/Net/predict_rate'):
        self.__path = str(path)
        self.__model = tf.keras.models.load_model(path)
        self.__name = 'bert-base-cased'
        self.__length = 40
        self.__config = BertConfig.from_pretrained(self.__name)
        self.__config.output_hidden_states = False

    def __prepare_data(self, user_input):
        tokenizers = BertTokenizerFast.from_pretrained(
            pretrained_model_name_or_path=self.__name,
            config=self.__config
        )
        x = tokenizers(
            text=user_input,
            add_special_tokens=True,
            max_length=self.__length,
            truncation=True,
            padding='max_length',
            return_tensors='tf',
            return_token_type_ids=False,
            return_attention_mask=True,
            verbose=True
        )
        return {
            'input_ids': tf.cast(x['input_ids'], tf.float64),
            'attention_mask': tf.cast(x['attention_mask'], tf.float64)
        }

    def predict(self, review):
        prediction = self.__prepare_data(review)
        probabilities = self.__model.predict(prediction)
        rate = np.argmax(probabilities[0])
        review_rate = int(rate) + 1
        return review_rate
