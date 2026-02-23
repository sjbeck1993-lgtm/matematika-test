import streamlit as st
import random
import time
import os

# Set page config
st.set_page_config(page_title="Matematika Testi", page_icon="🔢")

# Custom CSS for Blue and Yellow theme optimization
st.markdown("""
    <style>
    /* Headers in Blue */
    h1, h2, h3, .stHeading, span[data-testid="stHeader"] {
        color: #0072CE !important;
    }
    /* Buttons in Blue */
    div.stButton > button:first-child {
        background-color: #0072CE !important;
        color: white !important;
        border-radius: 5px;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #0056b3 !important;
    }
    /* Highlight/Accent in Yellow */
    .highlight {
        background-color: #FFD700;
        padding: 5px;
        border-radius: 5px;
        color: #000000;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def load_top_scores():
    if not os.path.exists("results.txt"):
        return []
    scores = []
    with open("results.txt", "r") as file:
        for line in file:
            try:
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
    return scores[:5]

def save_result(name, score, level, duration):
    with open("results.txt", "a") as file:
        file.write(f"{name},{score},{level},{duration}\n")

def generate_question(level):
    if level == 1:
        range_max = 10
        ops = ['+', '-']
    elif level == 2:
        range_max = 50
        ops = ['+', '-', '*']
    else:
        range_max = 100
        ops = ['+', '-', '*', '/']

    op = random.choice(ops)
    num1 = random.randint(1, range_max)
    num2 = random.randint(1, range_max)

    if op == '+':
        ans = num1 + num2
        q_str = f"{num1} + {num2}"
    elif op == '-':
        if num1 < num2:
            num1, num2 = num2, num1
        ans = num1 - num2
        q_str = f"{num1} - {num2}"
    elif op == '*':
        ans = num1 * num2
        q_str = f"{num1} * {num2}"
    elif op == '/':
        num1 = random.randint(1, range_max)
        factors = [x for x in range(1, num1 + 1) if num1 % x == 0]
        num2 = random.choice(factors)
        ans = num1 // num2
        q_str = f"{num1} / {num2}"

    return {'q': q_str, 'a': ans}

def main():
    # Logo centered
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            st.warning("Logo topilmadi!")

    st.title("Matematika Testi")

    # Initialize Session State
    if 'quiz_state' not in st.session_state:
        st.session_state.quiz_state = 'welcome'
        st.session_state.score = 0
        st.session_state.question_count = 0

    if st.session_state.quiz_state == 'welcome':
        st.subheader("Xush kelibsiz!")
        name = st.text_input("Ismingizni kiriting:")
        level = st.selectbox("Darajani tanlang:", [1, 2, 3], format_func=lambda x: f"Daraja {x}")

        st.markdown("---")
        st.write("🏆 **Eng yaxshi 5 natija:**")
        top_scores = load_top_scores()
        if top_scores:
            for i, s in enumerate(top_scores, 1):
                st.write(f"{i}. **{s['name']}**: {s['score']} ball (Daraja: {s['level']}, Vaqt: {s['time']}s)")
        else:
            st.write("Hozircha natijalar yo'q.")

        if st.button("Boshlash"):
            if name:
                st.session_state.user_name = name
                st.session_state.level = level
                st.session_state.quiz_state = 'playing'
                st.session_state.score = 0
                st.session_state.question_count = 0
                st.session_state.start_time = time.time()
                st.session_state.current_question = generate_question(level)
                # Clear feedback from previous games
                if 'feedback' in st.session_state:
                    del st.session_state.feedback
                st.rerun()
            else:
                st.error("Iltimos, ismingizni kiriting!")

    elif st.session_state.quiz_state == 'playing':
        # Show feedback from previous question
        if 'feedback' in st.session_state:
            if st.session_state.feedback['correct']:
                st.success("To'g'ri! ✅")
            else:
                st.error(f"Xato! ❌ To'g'ri javob: {st.session_state.feedback['ans']}")

        # Check if finished
        if st.session_state.question_count >= 10:
            st.session_state.end_time = time.time()
            st.session_state.quiz_state = 'finished'
            st.rerun()

        q_num = st.session_state.question_count + 1
        total_q = 10

        st.progress(st.session_state.question_count / total_q)
        st.markdown(f"**Savol {q_num}/{total_q}** | Ball: <span class='highlight'>{st.session_state.score}</span>", unsafe_allow_html=True)

        q_data = st.session_state.current_question

        with st.form(key=f"q_form_{q_num}"):
            st.header(f"{q_data['q']} = ?")
            user_ans = st.number_input("Javobingizni kiriting:", step=1, value=0)
            submit = st.form_submit_button("Javob berish")

            if submit:
                correct = (user_ans == q_data['a'])
                points = 1 if st.session_state.level == 1 else (2 if st.session_state.level == 2 else 3)

                if correct:
                    st.session_state.score += points

                st.session_state.feedback = {'correct': correct, 'ans': q_data['a']}
                st.session_state.question_count += 1

                if st.session_state.question_count < 10:
                    st.session_state.current_question = generate_question(st.session_state.level)

                st.rerun()

    elif st.session_state.quiz_state == 'finished':
        # Show last feedback if it exists
        if 'feedback' in st.session_state:
            if st.session_state.feedback['correct']:
                st.success("Oxirgi savol: To'g'ri! ✅")
            else:
                st.error(f"Oxirgi savol: Xato! ❌ To'g'ri javob: {st.session_state.feedback['ans']}")

        # Ensure we don't save multiple times if user refreshes
        if 'saved' not in st.session_state or not st.session_state.saved:
             duration = round(st.session_state.end_time - st.session_state.start_time, 2)
             save_result(st.session_state.user_name, st.session_state.score, st.session_state.level, duration)
             st.session_state.saved = True
             st.session_state.final_duration = duration

        st.balloons()
        st.title("🎉 Test tugadi!")
        st.subheader(f"{st.session_state.user_name}, natijalaringiz:")
        st.write(f"✅ **Jami ball:** {st.session_state.score}")
        st.write(f"⏱ **Vaqt:** {st.session_state.final_duration} soniya")

        if st.button("Qayta boshlash"):
            st.session_state.quiz_state = 'welcome'
            st.session_state.saved = False
            if 'feedback' in st.session_state:
                del st.session_state.feedback
            st.rerun()

if __name__ == "__main__":
    main()
