import googletrans


class Translator:
    def __init__(self, input_language='ru', output_language='en'):
        self.__instance = googletrans.Translator()
        self.__input_language = input_language
        self.__output_language = output_language

    def translate(self, user_input):
        translation = self.__instance.translate(
            user_input,
            src=self.__input_language,
            dest=self.__output_language
        )
        return str(translation.text)
