import random
print("🎲 Guessing Game (1–10, type 'exit' to quit)")

number = random.randint(1, 10)
while True:
    guess = input("Your guess: ")
    if guess.lower() == "exit":
        break
    if guess.isdigit():
        if int(guess) == number:
            print("🎉 Correct! You win!")
            break
        else:
            print("❌ Wrong! Try again.")
    else:
        print("Enter a number!")
