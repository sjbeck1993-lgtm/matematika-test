import random
import time
import os

def show_top_scores():
    print("\n--- Eng yaxshi 5 natija ---")
    if not os.path.exists("results.txt"):
        print("Hozircha natijalar yo'q.")
        print("---------------------------")
        return

    scores = []
    with open("results.txt", "r") as file:
        for line in file:
            try:
                # Expected: name,score,level,time
                parts = line.strip().split(',')
                if len(parts) == 4:
                    name, score, level, duration = parts
                    scores.append({
                        'name': name,
                        'score': int(score),
                        'level': int(level),
                        'time': float(duration)
                    })
            except ValueError:
                continue

    # Sort: High score first (desc), then low time (asc)
    scores.sort(key=lambda x: (-x['score'], x['time']))

    for i, s in enumerate(scores[:5], 1):
        print(f"{i}. {s['name']}: {s['score']} ball (Daraja: {s['level']}, Vaqt: {s['time']}s)")
    print("---------------------------")

def math_quiz():
    show_top_scores()
    score = 0
    total_questions = 10

    print("Salom! Matematika testiga xush kelibsiz!")
    name = input("Ismingizni kiriting: ")
    print("Darajani tanlang:")
    print("1. Oson (1-10, +, -)")
    print("2. O'rta (1-50, +, -, *)")
    print("3. Qiyin (1-100, +, -, *, /)")

    while True:
        try:
            level = int(input("Tanlovingiz (1, 2 yoki 3): "))
            if level in [1, 2, 3]:
                break
            else:
                print("Iltimos, 1, 2 yoki 3 ni tanlang!")
        except ValueError:
            print("Iltimos, son kiriting!")

    if level == 1:
        range_max = 10
        ops = ['+', '-']
        points = 1
    elif level == 2:
        range_max = 50
        ops = ['+', '-', '*']
        points = 2
    else:
        range_max = 100
        ops = ['+', '-', '*', '/']
        points = 3

    print(f"\n{total_questions} ta savolga javob bering. Har bir to'g'ri javob uchun {points} ball beriladi.\n")

    start_time = time.time()
    for i in range(1, total_questions + 1):
        op = random.choice(ops)

        # Initialize numbers
        num1 = random.randint(1, range_max)
        num2 = random.randint(1, range_max)

        if op == '+':
            correct_answer = num1 + num2
            question_str = f"{num1} + {num2}"
        elif op == '-':
            # Ensure positive result
            if num1 < num2:
                num1, num2 = num2, num1
            correct_answer = num1 - num2
            question_str = f"{num1} - {num2}"
        elif op == '*':
            correct_answer = num1 * num2
            question_str = f"{num1} * {num2}"
        elif op == '/':
            # Ensure integer result and dividend within range if possible,
            # or simply divisible.
            # Strategy: Generate dividend (num1), find random factor as divisor (num2)
            num1 = random.randint(1, range_max)
            factors = [x for x in range(1, num1 + 1) if num1 % x == 0]
            num2 = random.choice(factors)
            correct_answer = num1 // num2
            question_str = f"{num1} / {num2}"

        while True:
            try:
                user_answer = int(input(f"{i}-savol: {question_str} = "))
                break
            except ValueError:
                print("Iltimos, son kiriting!")

        if user_answer == correct_answer:
            print("To'g'ri!")
            score += points
        else:
            print(f"Xato! To'g'ri javob: {correct_answer}")

    end_time = time.time()
    duration = round(end_time - start_time, 2)

    with open("results.txt", "a") as file:
        file.write(f"{name},{score},{level},{duration}\n")

    print("\nTest tugadi!")
    print(f"Siz {total_questions * points} balldan {score} ball to'pladingiz.")

if __name__ == "__main__":
    math_quiz()
