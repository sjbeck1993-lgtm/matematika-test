import streamlit as st
import random
import time
import os
import io
from certificate import create_certificate

# Mock Data for Book Curriculum
COURSES = {
    "1-sinf": [
        "10 ichida qo'shish va ayirish",
        "20 ichida qo'shish va ayirish",
        "Mantiqiy savollar"
    ],
    "2-sinf": [
        "100 ichida qo'shish va ayirish",
        "Ko'paytirish va bo'lish",
        "Qoldiqli bo'lish",
        "Mantiqiy savollar"
    ]
}

# Mock Data for Logical Questions (Interactive Text Problems)
LOGICAL_QUESTIONS = [
    {
        "q": "Stolda 4 ta olma bor edi. Ulardan birini olib yeyishdi. Nechta olma qoldi?",
        "options": ["A) 3 ta", "B) 4 ta", "C) 5 ta"],
        "a": "A) 3 ta",
        "type": "logical"
    },
    {
        "q": "Anvarda 5 ta qalam bor, Boburda esa undan 2 ta ko'p. Boburda nechta qalam bor?",
        "options": ["A) 3 ta", "B) 7 ta", "C) 5 ta"],
        "a": "B) 7 ta",
        "type": "logical"
    },
    {
        "q": "Qaysi son qatorni davom ettiradi: 2, 4, 6, 8, ...?",
        "options": ["A) 9", "B) 10", "C) 12"],
        "a": "B) 10",
        "type": "logical"
    },
    {
        "q": "Bir hafta necha kundan iborat?",
        "options": ["A) 5 kun", "B) 6 kun", "C) 7 kun"],
        "a": "C) 7 kun",
        "type": "logical"
    },
    {
        "q": "Avtobusda 10 kishi bor edi. Bekatda 3 kishi tushdi va 2 kishi chiqdi. Avtobusda necha kishi bo'ldi?",
        "options": ["A) 9 kishi", "B) 11 kishi", "C) 15 kishi"],
        "a": "A) 9 kishi",
        "type": "logical"
    }
]

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

def generate_question(level, topic):
    q_type = 'standard'
    q_str = ""
    ans = 0
    options = []

    if topic == "Mantiqiy savollar":
        q_data = random.choice(LOGICAL_QUESTIONS)
        return {
            'q': q_data['q'],
            'a': q_data['a'],
            'options': q_data['options'],
            'type': 'logical'
        }

    elif topic == "Ko'paytirish va bo'lish":
        ops = ['*', '/']
        op = random.choice(ops)
        num1 = random.randint(2, 9)
        num2 = random.randint(2, 9)

        if op == '*':
            ans = num1 * num2
            q_str = f"{num1} * {num2}"
        else: # Division
            product = num1 * num2
            ans = num1
            q_str = f"{product} / {num2}"

    elif topic == "Qoldiqli bo'lish":
        dividend = random.randint(10, 99)
        divisor = random.randint(2, 9)
        quotient = dividend // divisor
        remainder = dividend % divisor
        ans = {'quotient': quotient, 'remainder': remainder}
        q_str = f"{dividend} : {divisor}"
        q_type = 'remainder'

    # Mapping new topics to logic
    elif "qo'shish va ayirish" in topic:
        if "10 " in topic:
            range_max = 10
        elif "20 " in topic:
            range_max = 20
        elif "100 " in topic:
            range_max = 100
        else:
            range_max = 10 * level # Fallback

        ops = ['+', '-']
        op = random.choice(ops)
        num1 = random.randint(1, range_max)
        num2 = random.randint(1, range_max)

        if op == '+':
            ans = num1 + num2
            q_str = f"{num1} + {num2}"
        else: # '-'
            if num1 < num2:
                num1, num2 = num2, num1
            ans = num1 - num2
            q_str = f"{num1} - {num2}"

    else: # Fallback / Umumiy (General)
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

    return {'q': q_str, 'a': ans, 'type': q_type}

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

        # Updated Selection Logic: Class -> Topic
        sinf = st.selectbox("Sinfni tanlang:", list(COURSES.keys()))
        topic = st.selectbox("Mavzuni tanlang:", COURSES[sinf])

        # We keep level for scoring multiplier or internal logic if needed
        level_map = {"1-sinf": 1, "2-sinf": 2}
        default_level = level_map.get(sinf, 1)

        # Hidden or informational level (since curriculum dictates difficulty mostly)
        st.write(f"Tanlangan daraja: {default_level}-daraja")

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
                st.session_state.level = default_level
                st.session_state.topic = topic
                st.session_state.quiz_state = 'playing'
                st.session_state.score = 0
                st.session_state.question_count = 0
                st.session_state.start_time = time.time()
                st.session_state.current_question = generate_question(default_level, topic)
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
                # Add Audio and Balloons here?
                # Ideally, they should trigger on the submission action to be immediate,
                # but st.rerun() clears them.
                # We can handle audio via st.audio with autoplay if supported, or just verify balloons appear.
                st.balloons()
                if os.path.exists("barakalla.mp3"):
                     st.audio("barakalla.mp3", autoplay=True)
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

        # Display Question
        if q_data.get('type') == 'logical':
             st.header(q_data['q'])
        else:
             st.header(f"{q_data['q']} = ?")

        with st.form(key=f"q_form_{q_num}"):
            user_ans = None

            if q_data.get('type') == 'logical':
                user_ans = st.radio("Javobni tanlang:", q_data['options'], index=None)
            elif q_data.get('type') == 'remainder':
                c1, c2 = st.columns(2)
                with c1:
                    user_q = st.number_input("Bo'linma (Javob):", step=1, value=0)
                with c2:
                    user_r = st.number_input("Qoldiq:", step=1, value=0)
                user_ans = {'quotient': user_q, 'remainder': user_r}
            else:
                user_ans = st.number_input("Javobingizni kiriting:", step=1, value=0)

            submit = st.form_submit_button("Javob berish")

            if submit:
                # Validation logic
                correct = False
                ans_display = ""

                if q_data.get('type') == 'logical':
                    if user_ans: # Check if selected
                        correct = (user_ans == q_data['a'])
                        ans_display = q_data['a']
                    else:
                        st.warning("Iltimos, javobni tanlang!")
                        st.stop() # Stop execution to let user select
                elif q_data.get('type') == 'remainder':
                    correct = (user_ans['quotient'] == q_data['a']['quotient'] and
                               user_ans['remainder'] == q_data['a']['remainder'])
                    ans_display = f"{q_data['a']['quotient']} (Qoldiq: {q_data['a']['remainder']})"
                else:
                    correct = (user_ans == q_data['a'])
                    ans_display = q_data['a']

                points = 1 if st.session_state.level == 1 else (2 if st.session_state.level == 2 else 3)

                if correct:
                    st.session_state.score += points

                st.session_state.feedback = {'correct': correct, 'ans': ans_display}
                st.session_state.question_count += 1

                if st.session_state.question_count < 10:
                    st.session_state.current_question = generate_question(st.session_state.level, st.session_state.topic)

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

        # Check for 100% result for Certificate
        points_per_q = 1 if st.session_state.level == 1 else (2 if st.session_state.level == 2 else 3)
        max_possible_score = 10 * points_per_q

        if st.session_state.score == max_possible_score:
            st.success("Tabriklaymiz! Siz barcha savollarga to'g'ri javob berdingiz!")

            # Certificate generation
            cert_img = create_certificate(st.session_state.user_name)
            st.image(cert_img, caption="Sizning sertifikatingiz", use_container_width=True)

            # Convert to bytes for download
            buf = io.BytesIO()
            cert_img.save(buf, format="PNG")
            byte_im = buf.getvalue()

            st.download_button(
                label="📥 Sertifikatni yuklab olish",
                data=byte_im,
                file_name="Sertifikat.png",
                mime="image/png"
            )

        if st.button("Qayta boshlash"):
            st.session_state.quiz_state = 'welcome'
            st.session_state.saved = False
            if 'feedback' in st.session_state:
                del st.session_state.feedback
            st.rerun()

if __name__ == "__main__":
    main()
