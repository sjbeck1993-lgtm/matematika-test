import streamlit as st
import random
import time
import os
import pandas as pd

def generate_question(level):
    if level == "Oson (1-10, +, -)":
        range_max = 10
        ops = ['+', '-']
    elif level == "O'rta (1-50, +, -, *)":
        range_max = 50
        ops = ['+', '-', '*']
    else:  # Qiyin
        range_max = 100
        ops = ['+', '-', '*', '/']

    op = random.choice(ops)
    num1 = random.randint(1, range_max)
    num2 = random.randint(1, range_max)

    if op == '+':
        correct_answer = num1 + num2
        question_str = f"{num1} + {num2}"
    elif op == '-':
        if num1 < num2:
            num1, num2 = num2, num1
        correct_answer = num1 - num2
        question_str = f"{num1} - {num2}"
    elif op == '*':
        correct_answer = num1 * num2
        question_str = f"{num1} * {num2}"
    elif op == '/':
        num1 = random.randint(1, range_max)
        factors = [x for x in range(1, num1 + 1) if num1 % x == 0]
        num2 = random.choice(factors)
        correct_answer = num1 // num2
        question_str = f"{num1} / {num2}"

    return num1, num2, op, correct_answer, question_str

def save_result(name, score, level, duration):
    with open("results.txt", "a") as file:
        # Map level name back to number for consistency with CLI or just use name
        # The prompt didn't specify format strictly, but keeping CSV is good.
        # Let's just save the level string or a simple int.
        # For simplicity, I'll save the level string as is, but maybe clean it up.
        lvl_map = {"Oson (1-10, +, -)": 1, "O'rta (1-50, +, -, *)": 2, "Qiyin (1-100, +, -, *, /)": 3}
        lvl_num = lvl_map.get(level, 0)
        file.write(f"{name},{score},{lvl_num},{duration}\n")

def load_top_scores():
    if not os.path.exists("results.txt"):
        return pd.DataFrame(columns=["Ism", "Ball", "Daraja", "Vaqt"])

    data = []
    with open("results.txt", "r") as file:
        for line in file:
            try:
                parts = line.strip().split(',')
                if len(parts) == 4:
                    name, score, level, duration = parts
                    data.append({
                        "Ism": name,
                        "Ball": int(score),
                        "Daraja": int(level),
                        "Vaqt": float(duration)
                    })
            except ValueError:
                continue

    df = pd.DataFrame(data)
    if not df.empty:
        df = df.sort_values(by=["Ball", "Vaqt"], ascending=[False, True])
        return df.head(5)
    return df

# --- State Initialization ---
if 'quiz_active' not in st.session_state:
    st.session_state.quiz_active = False
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0
if 'feedback' not in st.session_state:
    st.session_state.feedback = None

# --- Sidebar ---
st.sidebar.title("Natijalar")
st.sidebar.subheader("Eng yaxshi 5 natija")
top_scores = load_top_scores()
st.sidebar.table(top_scores)

# --- Main App ---
st.title("Matematika Testi")

if not st.session_state.quiz_active:
    st.header("Xush kelibsiz!")
    name = st.text_input("Ismingizni kiriting:")
    level = st.selectbox(
        "Darajani tanlang:",
        ["Oson (1-10, +, -)", "O'rta (1-50, +, -, *)", "Qiyin (1-100, +, -, *, /)"]
    )

    if st.button("Boshlash"):
        if name:
            st.session_state.user_name = name.replace(',', '')
            st.session_state.level = level
            st.session_state.score = 0
            st.session_state.question_count = 1
            st.session_state.quiz_active = True
            st.session_state.start_time = time.time()
            st.session_state.current_question = generate_question(level)
            st.rerun()
        else:
            st.warning("Iltimos, ismingizni kiriting!")

elif st.session_state.quiz_active and st.session_state.question_count <= 10:
    q_num = st.session_state.question_count
    num1, num2, op, correct, q_str = st.session_state.current_question

    st.subheader(f"{q_num}-savol: {q_str} = ?")

    # Use a unique key for input to clear it on next question
    user_answer = st.number_input("Javobingiz:", step=1, key=f"q_{q_num}")

    if st.button("Javob berish"):
        if user_answer == correct:
            st.success("To'g'ri!")
            st.session_state.score += (1 if "Oson" in st.session_state.level else 2 if "O'rta" in st.session_state.level else 3)
            st.session_state.feedback = "To'g'ri!"
        else:
            st.error(f"Xato! To'g'ri javob: {correct}")
            st.session_state.feedback = f"Xato! To'g'ri javob: {correct}"

        time.sleep(1) # Brief pause to show feedback
        st.session_state.question_count += 1

        if st.session_state.question_count <= 10:
            st.session_state.current_question = generate_question(st.session_state.level)
        st.rerun()

else:
    # Quiz Finished
    end_time = time.time()
    # Only calculate duration once
    if 'duration' not in st.session_state:
        # Subtract the accumulated sleep time (1s per question * 10 questions)
        total_time = end_time - st.session_state.start_time
        st.session_state.duration = round(max(0, total_time - 10), 2)
        save_result(
            st.session_state.user_name,
            st.session_state.score,
            st.session_state.level,
            st.session_state.duration
        )
        st.balloons()

    st.header("Test tugadi!")
    st.write(f"Ism: {st.session_state.user_name}")
    st.write(f"Jami ball: {st.session_state.score}")
    st.write(f"Sarflangan vaqt: {st.session_state.duration} soniya")

    if st.button("Qayta boshlash"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
