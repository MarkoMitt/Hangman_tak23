import glob
import sqlite3
import datetime
from Score import Score


class Model:
    def __init__(self):
        self.__database = 'databases/hangman_words_ee.db'  # Andmebaas
        # Installime vajaliku mooduli piltide kasutamiseks (käsureale => pip install Pillow)
        self.__image_files = glob.glob('images/*.png')  # List mängu piltidega
        self.random_word = ''
        self.__typed_letters = []
        self.__wrong_letters = []
        self.wrong_guesses = 0
        self.__user_found_letters = []
        self.guessable_word = ""
        self.__count = 0

    @property
    def count(self):
        return self.__count

    @property
    def database(self):
        return self.__database

    @property
    def image_files(self):
        return self.__image_files

    @database.setter
    def database(self, value):
        self.__database = value

    # Loeb andmebaasi tabelist edetabel kõik kirjad :return:
    def read_scores_data(self):
        connection = None
        try:
            connection = sqlite3.connect(self.__database)
            sql = 'SELECT * FROM scores ORDER BY seconds;'
            cursor = connection.execute(sql)
            data = cursor.fetchall()
            result = []
            for row in data:
                result.append(Score(row[1], row[2], row[3], row[4], row[5]))

            return result
        except sqlite3.Error as error:
            print(f'Viga ühenduda andmebaasi {self.__database}: {error}')
        finally:
            if connection:
                connection.close()

    def setup_new_game(self):
        self.random_word = self.get_random_word()
        # print(self.random_word)
        self.guessable_word = len(self.random_word) * '-'
        self.__typed_letters = []
        self.__wrong_letters = []
        self.wrong_guesses = 0
        self.__user_found_letters = ['_' for _ in range(len(self.random_word))]
        self.__count = 0

    def get_random_word(self):
        connection = None
        try:
            connection = sqlite3.connect(self.__database)
            cursor = connection.cursor()
            cursor.execute('SELECT word FROM words ORDER BY RANDOM() LIMIT 1;')
            random_word = cursor.fetchone()[0]
            return random_word.lower()
        except sqlite3.Error as error:
            print(f'Error fetching random word from database: {error}')
            return ''
        finally:
            if connection:
                connection.close()

    def control_user_input(self, user_input):
        if user_input:
            letter = user_input[0].lower()
            if letter in self.__typed_letters:
                self.wrong_guesses += 1
                self.__count += 1
                self.__wrong_letters.append(letter)
            self.__typed_letters.append(letter)
            if letter in self.random_word:
                for i, char in enumerate(self.random_word):
                    if char == letter:
                        self.__user_found_letters[i] = letter
                new_guessable_word = ""
                for i, char1 in enumerate(self.random_word):
                    if char1 == letter:
                        new_guessable_word += letter
                    elif self.guessable_word[i] != '-':
                        new_guessable_word += self.guessable_word[i]
                    else:
                        new_guessable_word += '-'
                self.guessable_word = new_guessable_word
            else:
                self.wrong_guesses += 1
                self.__count += 1

    def get_wrong_guesses_as_string(self):
        return ', '.join(self.__wrong_letters)

    def add_player_score(self, player_name, time_counter):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        player_name = player_name.strip()
        connection = None
        try:
            connection = sqlite3.connect(self.__database)
            cursor = connection.cursor()
            cursor.execute(
                'INSERT INTO scores (name, word, missing, seconds, date_time) VALUES (?, ?, ?, ?, ?);',
                (player_name, self.random_word, self.get_wrong_guesses_as_string(),
                 time_counter, current_time))
            connection.commit()
        except sqlite3.Error as error:
            print(f'Error adding player score to database: {error}')
        finally:
            if connection:
                connection.close()
