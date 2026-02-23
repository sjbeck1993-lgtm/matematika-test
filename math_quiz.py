import random

def math_quiz():
    score = 0
    total_questions = 10

    print("Salom! Matematika testiga xush kelibsiz!")
    print(f"{total_questions} ta ko'paytirish misolini bajaring.\n")

    for i in range(1, total_questions + 1):
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        correct_answer = num1 * num2

        while True:
            try:
                user_answer = int(input(f"{i}-savol: {num1} * {num2} = "))
                break
            except ValueError:
                print("Iltimos, son kiriting!")

        if user_answer == correct_answer:
            print("To'g'ri!")
            score += 1
        else:
            print(f"Xato! To'g'ri javob: {correct_answer}")

    print("\nTest tugadi!")
    print(f"Siz {total_questions} ta savoldan {score} tasini to'g'ri topdingiz.")

if __name__ == "__main__":
    math_quiz()
