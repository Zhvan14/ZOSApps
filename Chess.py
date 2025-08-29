import chess
import os

# Create a new board
board = chess.Board()

# Game loop
while not board.is_game_over():
    # Print the board
    os.system('clear')
    print(board)
    print("\n")

    # Get a move from the current player
    try:
        move_san = input(f"Enter your move ({'White' if board.turn else 'Black'}): ")
        move = board.parse_san(move_san)

        # Make the move
        if move in board.legal_moves:
            board.push(move)
        else:
            print("Illegal move. Try again.")

    except (ValueError, chess.InvalidMoveError):
        print("Invalid format. Please use SAN (e.g., 'Nf3', 'e4').")

# Print the final board and the game result
print("\nFinal board:")
print(board)
print("\nGame Over!")
print(f"Result: {board.result()}")
