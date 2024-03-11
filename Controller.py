from GameTime import GameTime
from Model import Model
from View import View
from tkinter import simpledialog, messagebox


class Controller:
    def __init__(self, db_name=None):
        self.__model = Model()
        self.__view = View(self, self.__model)
        if db_name is not None:
            self.__model.database = db_name
        self.__game_time = GameTime(self.__view.lbl_time)
        # print(self.__model.database)

    def main(self):
        self.__view.main()

    def btn_scoreboard_click(self):
        window = self.__view.create_scoreboard_window()
        data = self.__model.read_scores_data()
        self.__view.draw_scoreboard(window, data)

    def buttons_no_game(self):
        self.__view.btn_new['state'] = 'normal'
        self.__view.btn_cancel['state'] = 'disabled'
        self.__view.btn_send['state'] = 'disabled'
        self.__view.char_input.delete(0, 'end')  # Sisestus kast tühjaks
        self.__view.char_input['state'] = 'disabled'

    def buttons_to_game(self):
        self.__view.btn_new['state'] = 'disabled'
        self.__view.btn_cancel['state'] = 'normal'
        self.__view.btn_send['state'] = 'normal'
        self.__view.char_input['state'] = 'normal'
        self.__view.char_input.focus()

    def btn_new_click(self):
        self.buttons_to_game()
        # Muuda pildi id-ga 0
        self.__view.change_image(0)

        self.__view.change_image(0)
        self.__model.setup_new_game()
        self.__view.lbl_result.config(text=self.__model.guessable_word)
        self.__view.lbl_error.config(text='Vigased tähed:', fg='red')

        self.__game_time.reset()
        self.__game_time.start()

    def btn_cancel_click(self):
        self.__game_time.stop()
        self.__view.change_image(-1)  # õpetaja variant -> self.__view.change_image(len(self.__model.image_files)-1)
        self.buttons_no_game()

    def btn_send_click(self):
        # print(self.__view.char_input.get())
        self.__model.control_user_input(self.__view.char_input.get())
        # print(self.__model.guessable_word)
        self.__view.lbl_result.config(text=self.__model.guessable_word)
        vigased = "Vigased tähed: " + self.__model.get_wrong_guesses_as_string()
        self.__view.lbl_error.config(text=vigased, fg="red")
        self.__view.char_input.delete(0, 'end')
        self.__view.change_image(self.__model.wrong_guesses)
        if self.__model.guessable_word == self.__model.random_word:
            self.winner()
        if self.__model.count == 11:
            self.lose()

    def winner(self):
        self.btn_cancel_click()
        messagebox.showinfo("Võitja!", "Huraa võitsid!")
        player_name = simpledialog.askstring("Edetabelisse", "Sisesta oma nimi:")
        if player_name:
            self.__model.add_player_score(player_name, self.__game_time.counter)
            return

    def lose(self):
        self.btn_cancel_click()
        messagebox.showinfo("Luuser", "Kaotasid lammas!")
