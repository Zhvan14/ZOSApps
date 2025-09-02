import random

print("Guessing Game (1–10, type 'exit' to quit)")

number = random.randint(1, 10)

while True:
    guess = input("Your guess: ").strip()
    
    if guess.lower() == "exit":
        print("Goodbye!")
        break
    
    if guess.isdigit():
        guess_num = int(guess)
        if guess_num == number:
            print("Correct! You win!")
            break
        elif guess_num < number:
            print("Too low! Try again.")
        else:
            print("Too high! Try again.")
    else:
        print("Enter a number!")
