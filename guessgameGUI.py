import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout

class GuessingGame(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=20, **kwargs)
        self.number = random.randint(1, 10)

        # Info Label
        self.info_label = Label(text="Guess a number between 1–10 (type 'exit' to quit)", halign='center', font_size=32)
        self.info_label.bind(size=self.info_label.setter('text_size'))
        self.add_widget(self.info_label)

        # AnchorLayout to center the input
        input_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None, height=100)
        self.input_box = TextInput(multiline=False, size_hint=(None, None), size=(100, 100), halign='center', font_size=36)
        self.input_box.bind(on_text_validate=self.check_guess)
        input_anchor.add_widget(self.input_box)
        self.add_widget(input_anchor)

        # Result Label
        self.result_label = Label(text="", halign='center', font_size=32)
        self.result_label.bind(size=self.result_label.setter('text_size'))
        self.add_widget(self.result_label)

        # Restart Button
        self.restart_button = Button(text="Restart Game", size_hint=(None, None), size=(250, 70), font_size=28)
        self.restart_button.bind(on_press=self.restart_game)
        restart_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None, height=80)
        restart_anchor.add_widget(self.restart_button)
        self.add_widget(restart_anchor)

    def check_guess(self, instance):
        guess = self.input_box.text.strip()
        if guess.lower() == "exit":
            App.get_running_app().stop()
        elif guess.isdigit():
            guess_num = int(guess)
            if guess_num == self.number:
                self.result_label.text = "Correct! You win!"
            elif guess_num < self.number:
                self.result_label.text = "Too low! Try again."
            else:
                self.result_label.text = "Too high! Try again."
        else:
            self.result_label.text = "Enter a number!"
        self.input_box.text = ""

    def restart_game(self, instance):
        self.number = random.randint(1, 10)
        self.result_label.text = ""
        self.input_box.text = ""
        self.info_label.text = "Guess a number between 1–10 (type 'exit' to quit)"

class GuessingGameApp(App):
    def build(self):
        return GuessingGame()

if __name__ == "__main__":
    GuessingGameApp().run()
