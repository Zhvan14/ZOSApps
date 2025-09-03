import chess
import os

# Create a new board
board = chess.Board()

# A flag to check if the game ended by resignation or exit
game_ended = False

# Game loop
while not board.is_game_over() and not game_ended:
    # Print the board
    os.system('clear')
    print(board)
    print("\n")

    # Get a move from the current player
    try:
        move_san = input(f"Enter your move ({'White' if board.turn else 'Black'}): ")
        
        if move_san == "draw":
            print("Draw offered. Type 'accept' to agree or a move to decline.")
            response = input(f"{'Black' if board.turn else 'White'}'s response: ")
            if response == "accept":
                print("\nGame is a draw.")
                game_ended = True  # Set the flag to end the loop
                input()
            else:
                continue

        elif move_san == "resign":
            resigner = "White" if board.turn else "Black"
            winner = "Black" if board.turn else "White"
            print(f"{resigner} resigns. {winner} wins.")
            game_ended = True  # Set the flag to end the loop
            input()

        elif move_san == "exit":
            print("Exiting game...")
            game_ended = True  # Set the flag to end the loop
        
        else:
            move = board.parse_san(move_san)
            if move in board.legal_moves:
                board.push(move)
            else:
                print("Illegal move. Try again.")

    except (ValueError, chess.InvalidMoveError):
        print()
        
# A separate check for game outcome after the loop
if not game_ended:
    print("\nFinal board:")
    print(board)
    print("\nGame Over!")
    print(f"Result: {board.result()}")
