import config
import translate
import rate
import toxicity
import pymysql
import tkinter


class MySQL:
    def __init__(self, mode="csv"):
        self.__mode = mode
        self.__connection = str()
        self.__counter = 0
        self.__review = str()
        self.__review_rate = str()
        self.__review_toxicity = str()

    def __change_database(self, cursor, connection):
        update_table = str(
            "update review_analysis " +
            f"set id = '{self.__counter}', " +
            f"rate = '{self.__review_rate}', " +
            f"toxic = '{self.__review_toxicity[0]}', " +
            f"severe_toxic = '{self.__review_toxicity[1]}', " +
            f"obscene = '{self.__review_toxicity[2]}', " +
            f"threat = '{self.__review_toxicity[3]}', " +
            f"insult = '{self.__review_toxicity[4]}', " +
            f"identity_hate = '{self.__review_toxicity[5]}' " +
            f"where review = '{self.__review}' ;"
        )
        connection.commit()
        cursor.execute(update_table)

    def __make_csv(self):
        with open("reviews.csv", mode='a') as csv:
            csv.write(
                f"{self.__counter}` {self.__review}` {self.__review_rate}` {self.__review_toxicity[0]}` "
                f"{self.__review_toxicity[1]}` {self.__review_toxicity[2]}` {self.__review_toxicity[3]}` "
                f"{self.__review_toxicity[4]}` {self.__review_toxicity[5]}\n"
            )

    def predict(self):
        translator = translate.Translator()
        rate_net = rate.RateNet()
        toxicity_net = toxicity.ToxicityNet()

        try:
            self.__connection = pymysql.connect(
                host=config.host,
                port=config.port,
                user=config.user,
                password=config.password,
                database=config.db_name,
                cursorclass=pymysql.cursors.DictCursor
            )
            try:
                with self.__connection.cursor() as cursor:
                    get_reviews = str(
                        f"select {config.column_name} " +
                        f"from {config.table_name}; "
                    )
                    cursor.execute(get_reviews)
                    reviews = cursor.fetchall()

                    if self.__mode == "sql":
                        exist_check = str(
                            "drop table if exists review_analysis; "
                        )
                        cursor.execute(exist_check)

                        create_table = str(
                            "create table review_analysis " +
                            f"select {config.column_name} " +
                            f"from {config.table_name}; "
                        )
                        cursor.execute(create_table)

                        add_columns = str(
                            "alter table review_analysis " +
                            "add column id int first, "
                            "add column rate int, " +
                            "add column toxic int, " +
                            "add column severe_toxic int, " +
                            "add column obscene int, " +
                            "add column threat int, " +
                            "add column insult int, " +
                            "add column identity_hate int; "
                        )
                        cursor.execute(add_columns)

                        set_safe_updates = str(
                            "SET SQL_SAFE_UPDATES = 0;"
                        )
                        cursor.execute(set_safe_updates)

                    for line in reviews:
                        self.__counter += 1
                        for key in line:
                            self.__review = str(line[key])
                            translated_review = translator.translate(self.__review)
                            self.__review_rate = rate_net.predict(translated_review)
                            self.__review_toxicity = toxicity_net.predict(translated_review)

                            if self.__mode == "sql":
                                self.__change_database(cursor, self.__connection)
                            elif self.__mode == "csv":
                                if self.__counter == 1:
                                    with open("reviews.csv", mode='w') as csv:
                                        csv.write(
                                            "id` review` rate` toxic` severe_toxic` obscene` threat` insult` "
                                            "identity_hate\n"
                                        )
                                self.__make_csv()

            finally:
                self.__connection.commit()
                self.__connection.close()
        except Exception as error:
            print("Нет доступа к БД")
            print(error)


class Demo:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title("Система анализа тональности отзывов")

        self.input = tkinter.Entry(self.window, width=40, )
        self.input.grid(row=0, columnspan=2, pady=(20, 0), padx=20)

        self.button = tkinter.Button(
            self.window, text="Провести анализ", width=33, bg="red", fg="white", command=self.__predict
        )
        self.button.grid(row=1, columnspan=2, pady=(20, 20), padx=20)

        self.rate_left = tkinter.Label(self.window, text="Предполагаемая оценка:")
        self.rate_left.grid(row=2, column=0, pady=(0, 5), padx=(20, 0), sticky=tkinter.W)

        self.rate_right = tkinter.Label(self.window, text="-")
        self.rate_right.grid(row=2, column=1, pady=(0, 5), padx=(0, 20), sticky=tkinter.E)

        self.toxic_left = tkinter.Label(self.window, text="Незначительная токсичность:")
        self.toxic_left.grid(row=3, column=0, pady=(5, 5), padx=(20, 0), sticky=tkinter.W)

        self.toxic_right = tkinter.Label(self.window, text="-")
        self.toxic_right.grid(row=3, column=1, pady=(5, 5), padx=(0, 20), sticky=tkinter.E)

        self.severe_toxic_left = tkinter.Label(self.window, text="Значительной токсичность:")
        self.severe_toxic_left.grid(row=4, column=0, pady=(5, 5), padx=(20, 0), sticky=tkinter.W)

        self.severe_toxic_right = tkinter.Label(self.window, text="-")
        self.severe_toxic_right.grid(row=4, column=1, pady=(5, 5), padx=(0, 20), sticky=tkinter.E)

        self.obscene_left = tkinter.Label(self.window, text="Нецензурная лексика:")
        self.obscene_left.grid(row=5, column=0, pady=(5, 5), padx=(20, 0), sticky=tkinter.W)

        self.obscene_right = tkinter.Label(self.window, text="-")
        self.obscene_right.grid(row=5, column=1, pady=(5, 5), padx=(0, 20), sticky=tkinter.E)

        self.threat_left = tkinter.Label(self.window, text="Угрозы:")
        self.threat_left.grid(row=6, column=0, pady=(5, 5), padx=(20, 0), sticky=tkinter.W)

        self.threat_right = tkinter.Label(self.window, text="-")
        self.threat_right.grid(row=6, column=1, pady=(5, 5), padx=(0, 20), sticky=tkinter.E)

        self.insult_left = tkinter.Label(self.window, text="Оскорбления:")
        self.insult_left.grid(row=7, column=0, pady=(5, 5), padx=(20, 0), sticky=tkinter.W)

        self.insult_right = tkinter.Label(self.window, text="-")
        self.insult_right.grid(row=7, column=1, pady=(5, 5), padx=(0, 20), sticky=tkinter.E)

        self.identity_hate_left = tkinter.Label(self.window, text="Переход на личности:")
        self.identity_hate_left.grid(row=8, column=0, pady=(5, 20), padx=(20, 0), sticky=tkinter.W)

        self.identity_hate_right = tkinter.Label(self.window, text="-")
        self.identity_hate_right.grid(row=8, column=1, pady=(5, 20), padx=(0, 20), sticky=tkinter.E)

    def __predict(self):
        translator = translate.Translator()
        rate_net = rate.RateNet()
        toxicity_net = toxicity.ToxicityNet()

        review = self.input.get()
        translated_review = translator.translate(review)
        review_rate = rate_net.predict(translated_review)
        review_toxicity = toxicity_net.predict(translated_review)

        self.rate_right.configure(text=review_rate)
        self.toxic_right.configure(text=review_toxicity[0])
        self.severe_toxic_right.configure(text=review_toxicity[1])
        self.obscene_right.configure(text=review_toxicity[2])
        self.threat_right.configure(text=review_toxicity[3])
        self.insult_right.configure(text=review_toxicity[4])
        self.identity_hate_right.configure(text=review_toxicity[5])

    def start(self):
        self.window.mainloop()


def main():
    print(
        "Система анализа тональности отзывов\n\n" +
        "Выберите режим:\n" +
        "0. Завершение работы\n"
        "1. Работа с базой данных MySQL\n" +
        "2. Демонстрация\n"
    )
    user_input = int(input("Режим: "))
    if user_input == 0:
        print("Работа завершена")
    elif user_input == 1:
        print(
            "\nВыберите операцию:\n" +
            "0. Назад\n"
            "1. Добавить таблицу с результатами в существующую БД\n" +
            "2. Создать .csv файл с результатами\n"
        )
        user_input = int(input("Операция: "))
        if user_input == 0:
            pass
        elif user_input == 1:
            database = MySQL(mode="sql")
            database.predict()
        elif user_input == 2:
            database = MySQL(mode="csv")
            database.predict()
        else:
            print("Неверная команда, введите цифру от 0 до 2")
    elif user_input == 2:
        window = Demo()
        window.start()
    else:
        print("Неверная команда, введите цифру от 0 до 2")


if __name__ == "__main__":
    main()
