import chess
import threading
import socket
import time
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.image import AsyncImage
import urllib.request

# ---------- NETWORK SETTINGS ----------
TCP_PORT = 5001
UDP_PORT = 5000
BROADCAST_MSG = b'CHESS_HOST'
BROADCAST_INTERVAL = 1

# ---------- NETWORK THREAD ----------
class NetworkThread(threading.Thread):
    def __init__(self, app, is_server=False, host='localhost'):
        super().__init__(daemon=True)
        self.app = app
        self.is_server = is_server
        self.host = host
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = None

    def run(self):
        try:
            if self.is_server:
                self.sock.bind(('', TCP_PORT))
                self.sock.listen(1)
                self.app.update_status("Waiting for opponent...")
                self.conn, _ = self.sock.accept()
                self.app.update_status("Opponent connected! Your turn.")
            else:
                self.sock.connect((self.host, TCP_PORT))
                self.conn = self.sock
                self.app.update_status("Connected! Waiting for opponent's move.")

            while True:
                data = self.conn.recv(1024)
                if not data:
                    break
                text = data.decode()
                if ':' in text:
                    msg_type, msg_data = text.split(':', 1)
                    if msg_type == "MOVE":
                        move = chess.Move.from_uci(msg_data)
                        self.app.board.push(move)
                        self.app.update_board()
                        self.app.is_my_turn = True
                        self.app.update_status(f"{'White' if self.app.board.turn else 'Black'} to move")
                    elif msg_type == "DRAW":
                        self.app.offer_draw_network()
                    elif msg_type == "DRAW_ACCEPT":
                        self.app.show_popup("Draw accepted. Game ends.", self.app.reset_game)
                    elif msg_type == "RESIGN":
                        winner = 'Black' if self.app.board.turn else 'White'
                        self.app.show_popup(f"{winner} wins by resignation!", self.app.reset_game)
        except Exception as e:
            print("Network error:", e)
            self.app.update_status("Connection lost!")

    def send_move(self, move):
        if self.conn:
            self.conn.sendall(f"MOVE:{move.uci()}".encode())

    def send_message(self, msg):
        if self.conn:
            self.conn.sendall(msg.encode())

# ---------- LAN DISCOVERY ----------
def broadcast_host(stop_event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while not stop_event.is_set():
        sock.sendto(BROADCAST_MSG, ('<broadcast>', UDP_PORT))
        stop_event.wait(BROADCAST_INTERVAL)

def discover_hosts(timeout=3):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', UDP_PORT))
    sock.settimeout(timeout)
    hosts = set()
    start = time.time()
    while time.time() - start < timeout:
        try:
            data, addr = sock.recvfrom(1024)
            if data == BROADCAST_MSG:
                hosts.add(addr[0])
        except socket.timeout:
            break
    return list(hosts)

# ---------- CHESS APP ----------
class ChessApp(App):
    def build(self):
        self.board = chess.Board()
        self.selected_square = None
        self.network = None
        self.is_my_turn = True
        self.broadcast_thread = None
        self.broadcast_stop_event = threading.Event()
        self.online = True

        # Check internet connection to decide online/offline pieces
        try:
            urllib.request.urlopen('https://images.chesscomfiles.com', timeout=2)
            self.online = True
        except:
            self.online = False

        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Board
        self.grid = GridLayout(cols=8, rows=8, spacing=0)
        self.square_buttons = {}
        self.create_board()
        main_layout.add_widget(self.grid)

        # Controls
        controls = BoxLayout(size_hint=(1, 0.2), spacing=5)
        self.status_label = Label(text='Choose Host, Join or Local')
        controls.add_widget(self.status_label)

        resign_btn = Button(text='Resign', on_press=self.resign)
        draw_btn = Button(text='Draw', on_press=self.offer_draw)
        host_btn = Button(text='Host', on_press=self.host_game)
        join_btn = Button(text='Join', on_press=self.join_game)
        local_btn = Button(text='Local', on_press=self.start_local)

        controls.add_widget(resign_btn)
        controls.add_widget(draw_btn)
        controls.add_widget(host_btn)
        controls.add_widget(join_btn)
        controls.add_widget(local_btn)

        main_layout.add_widget(controls)
        return main_layout

    # ---------- BOARD ----------
    def create_board(self):
        self.grid.clear_widgets()
        for rank in range(7, -1, -1):
            for file in range(8):
                square = chess.square(file, rank)
                piece = self.board.piece_at(square)
                text = piece.symbol() if piece else ''
                btn = Button(text=text, font_size=32,
                             background_color=self.get_square_color(rank, file),
                             on_press=lambda btn, s=square: self.select_square(s))
                self.square_buttons[square] = btn
                self.grid.add_widget(btn)

    def get_square_color(self, rank, file):
        if (rank + file) % 2 == 0:
            return (1, 1, 1, 1)  # White
        else:
            return (0.2, 0.2, 0.2, 1)  # Black

    def reset_colors(self):
        for square, btn in self.square_buttons.items():
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            btn.background_color = self.get_square_color(rank, file)

    def select_square(self, square):
        if self.network and not self.is_my_turn:
            self.update_status("Wait for your turn!")
            return

        # Reset colors before making a new selection
        self.reset_colors()

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece is None or piece.color != self.board.turn:
                self.update_status("Select your own piece!")
                return
            self.selected_square = square
            self.square_buttons[square].background_color = (0, 1, 0, 1)

            # Highlight legal moves
            for move in self.board.legal_moves:
                if move.from_square == square:
                    self.square_buttons[move.to_square].background_color = (0, 0, 1, 1) # Blue for legal moves
        else:
            move_made = False
            for move in self.board.legal_moves:
                if move.from_square == self.selected_square and move.to_square == square:
                    self.board.push(move)
                    self.update_board()
                    if self.network:
                        self.network.send_move(move)
                        self.is_my_turn = False
                    self.update_status(f"{'White' if self.board.turn else 'Black'} to move")
                    if self.board.is_game_over():
                        self.show_game_over()
                    move_made = True
                    break
            if not move_made:
                self.update_status("Illegal move!")

            self.selected_square = None
            self.update_board()
            self.reset_colors()


    def update_board(self):
        for square, btn in self.square_buttons.items():
            piece = self.board.piece_at(square)
            btn.clear_widgets()
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            btn.background_color = self.get_square_color(rank, file)
            if piece:
                if self.online:
                    piece_name = piece.symbol().lower()
                    color = 'w' if piece.color == chess.WHITE else 'b'
                    url = f"https://images.chesscomfiles.com/chess-themes/pieces/neo/300/{color}{piece_name}.png"
                    img = AsyncImage(source=url, size_hint=(None, None), size=(50, 50))
                    btn.add_widget(img)
                else:
                    btn.text = piece.symbol()
            else:
                btn.text = ''

    # ---------- GAME EVENTS ----------
    def resign(self, instance):
        winner = 'Black' if self.board.turn else 'White'
        if self.network:
            self.network.send_message("RESIGN")
        self.show_popup(f"{winner} wins by resignation!", self.reset_game)

    def offer_draw(self, instance):
        if self.network:
            self.network.send_message("DRAW")
            self.show_popup("Draw offer sent to opponent.", None)
        else:
            self.show_popup("Local draw offered!", None)

    def offer_draw_network(self):
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text="Opponent offered a draw. Accept?"))
        buttons = BoxLayout(spacing=10)
        accept_btn = Button(text="Accept", on_press=self.accept_draw_network)
        decline_btn = Button(text="Decline", on_press=self.decline_draw_network)
        buttons.add_widget(accept_btn)
        buttons.add_widget(decline_btn)
        content.add_widget(buttons)
        self.draw_popup = Popup(title="Draw Offer", content=content, size_hint=(0.8, 0.4))
        self.draw_popup.open()

    def accept_draw_network(self, instance=None):
        if self.draw_popup:
            self.draw_popup.dismiss()
        if self.network:
            self.network.send_message("DRAW_ACCEPT")
        self.show_popup("Draw accepted. Game ends.", self.reset_game)

    def decline_draw_network(self, instance=None):
        if self.draw_popup:
            self.draw_popup.dismiss()
        self.show_popup("Draw declined. Game continues.", None)

    def reset_game(self, instance=None):
        self.board.reset()
        self.selected_square = None
        self.is_my_turn = True
        self.update_board()
        self.update_status("White to move")

    def show_game_over(self):
        result = self.board.result()
        self.show_popup(f"Game over! Result: {result}", self.reset_game)

    # ---------- STATUS/POPUPS ----------
    def update_status(self, message):
        self.status_label.text = message

    def show_popup(self, message, callback=None):
        popup = Popup(title="Chess", content=Label(text=message), size_hint=(0.8, 0.4))
        if callback:
            popup.bind(on_dismiss=lambda x: callback())
        popup.open()

    # ---------- HOST/JOIN ----------
    def host_game(self, instance=None):
        self.broadcast_stop_event.clear()
        self.broadcast_thread = threading.Thread(target=broadcast_host, args=(self.broadcast_stop_event,), daemon=True)
        self.broadcast_thread.start()
        self.network = NetworkThread(self, is_server=True)
        self.network.start()
        self.is_my_turn = True
        self.update_status("Hosting game. Waiting for opponent...")

    def join_game(self, instance=None):
        hosts = discover_hosts()
        if not hosts:
            self.show_popup("No hosts found on Wi-Fi!", None)
            return
        self.show_host_selection_popup(hosts)

    def show_host_selection_popup(self, hosts):
        content = BoxLayout(orientation='vertical', spacing=10)
        for ip in hosts:
            btn = Button(text=ip, size_hint_y=None, height=40)
            btn.bind(on_press=lambda x, ip=ip: self.connect_to_host(ip))
            content.add_widget(btn)
        popup = Popup(title="Select Host", content=content, size_hint=(0.8, 0.6))
        self.host_popup = popup
        popup.open()

    def connect_to_host(self, host_ip):
        if hasattr(self, 'host_popup'):
            self.host_popup.dismiss()
        self.network = NetworkThread(self, is_server=False, host=host_ip)
        self.network.start()
        self.is_my_turn = False
        self.update_status("Connected! Waiting for opponent's move.")

    # ---------- LOCAL ----------
    def start_local(self, instance=None):
        self.network = None
        self.is_my_turn = True
        self.update_status("Local game started! White to move.")
        self.reset_game()

if __name__ == "__main__":
    ChessApp().run()
 
