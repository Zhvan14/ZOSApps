import chess
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.window import Window

class ChessApp(App):
    def build(self):
        self.board = chess.Board()
        self.selected_square = None

        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Board layout, centered and properly scaled
        self.grid = GridLayout(cols=8, rows=8, spacing=2, size_hint=(0.9, 0.8), pos_hint={'center_x': 0.5})
        self.square_buttons = {}
        self.create_board()
        main_layout.add_widget(self.grid)

        # Controls
        controls = BoxLayout(size_hint=(1, 0.2), spacing=5)
        self.status_label = Label(text='White to move')
        controls.add_widget(self.status_label)

        resign_btn = Button(text='Resign', on_press=self.resign)
        draw_btn = Button(text='Draw', on_press=self.offer_draw)
        reset_btn = Button(text='Reset', on_press=self.reset_game)

        controls.add_widget(resign_btn)
        controls.add_widget(draw_btn)
        controls.add_widget(reset_btn)

        main_layout.add_widget(controls)
        return main_layout

    def create_board(self):
        self.grid.clear_widgets()
        button_size = min(Window.width, Window.height) / 10  # make buttons fit nicely

        for rank in range(7, -1, -1):
            for file in range(8):
                square = chess.square(file, rank)
                piece = self.board.piece_at(square)
                text = piece.symbol() if piece else ''
                btn = Button(text=text, font_size=24, size_hint=(None, None), width=button_size, height=button_size, on_press=lambda btn, s=square: self.select_square(s))
                self.square_buttons[square] = btn
                self.grid.add_widget(btn)

    def select_square(self, square):
        if self.selected_square is None:
            if self.board.piece_at(square) is None or self.board.piece_at(square).color != self.board.turn:
                self.status_label.text = 'Select a valid piece to move.'
                return
            self.selected_square = square
            self.square_buttons[square].background_color = (0, 1, 0, 1)
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.update_board()
                self.selected_square = None
                self.status_label.text = f"{'White' if self.board.turn else 'Black'} to move"
                if self.board.is_game_over():
                    self.show_game_over()
            else:
                self.status_label.text = 'Illegal move!'
                self.square_buttons[self.selected_square].background_color = (1, 1, 1, 1)
                self.selected_square = None

    def update_board(self):
        for square, btn in self.square_buttons.items():
            piece = self.board.piece_at(square)
            btn.text = piece.symbol() if piece else ''
            btn.background_color = (1, 1, 1, 1)

    def resign(self, instance):
        winner = 'Black' if self.board.turn else 'White'
        self.show_popup(f'{winner} wins by resignation!')

    def offer_draw(self, instance):
        self.show_popup('Draw offered. Game ends in a draw.')

    def reset_game(self, instance):
        self.board.reset()
        self.selected_square = None
        self.update_board()
        self.status_label.text = 'White to move'

    def show_game_over(self):
        result = self.board.result()
        self.show_popup(f'Game over! Result: {result}')

    def show_popup(self, message):
        popup = Popup(title='Chess', content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

if __name__ == '__main__':
    ChessApp().run()
