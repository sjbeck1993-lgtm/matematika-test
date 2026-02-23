import streamlit as st
import random
import time
import os
import io
import json
from certificate import create_certificate

# Set page config
st.set_page_config(page_title="Smart Learning Center", page_icon="📚")

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

@st.cache_data
def load_questions():
    try:
        with open('data/questions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return {}

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
                        'level': level, # Can be string now (topic)
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

def get_question_pool(topic_key, data):
    topic_data = data.get(topic_key)
    if not topic_data:
        return []

    # Combine exercises and tests
    # Filter only questions that have options and an answer
    pool = []

    # Add Tests
    for q in topic_data.get('tests', []):
        if q.get('options') and q.get('answer'):
            q['type'] = 'test'
            pool.append(q)

    # Add Exercises
    for q in topic_data.get('exercises', []):
        if q.get('options') and q.get('answer'):
            q['type'] = 'exercise'
            pool.append(q)

    return pool

def main():
    # Logo centered
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            pass # No logo, no warning needed strictly

    st.title("Smart Learning Center: 3-sinf Mukammal Matematika")

    data = load_questions()
    topics = list(data.keys())

    # Sort topics numerically if they start with number
    topics.sort(key=lambda x: int(x.split('-')[0]) if x.split('-')[0].isdigit() else 999)

    # Initialize Session State
    if 'quiz_state' not in st.session_state:
        st.session_state.quiz_state = 'welcome'
        st.session_state.score = 0
        st.session_state.question_count = 0
        st.session_state.question_pool = []

    if st.session_state.quiz_state == 'welcome':
        st.subheader("Xush kelibsiz!")
        name = st.text_input("Ismingizni kiriting:")

        topic = st.selectbox("Mavzuni tanlang:", topics)

        st.markdown("---")
        st.write("🏆 **Eng yaxshi 5 natija:**")
        top_scores = load_top_scores()
        if top_scores:
            for i, s in enumerate(top_scores, 1):
                st.write(f"{i}. **{s['name']}**: {s['score']} ball (Mavzu: {s['level']}, Vaqt: {s['time']}s)")
        else:
            st.write("Hozircha natijalar yo'q.")

        if st.button("Boshlash"):
            if name:
                st.session_state.user_name = name
                st.session_state.topic = topic

                # Load pool
                pool = get_question_pool(topic, data)
                if not pool:
                    st.error("Ushbu mavzu bo'yicha savollar tayyorlanmoqda (javoblar kiritilmagan). Iltimos, boshqa mavzuni tanlang (masalan, 1-5 mavzular).")
                    return

                # Shuffle pool and take 10 (or less if pool is small)
                random.shuffle(pool)
                selected_questions = pool[:10]

                st.session_state.quiz_questions = selected_questions
                st.session_state.total_questions = len(selected_questions)

                st.session_state.quiz_state = 'playing'
                st.session_state.score = 0
                st.session_state.question_count = 0
                st.session_state.start_time = time.time()

                # Clear feedback
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
                st.balloons()
                if os.path.exists("barakalla.mp3"):
                     st.audio("barakalla.mp3", autoplay=True)
            else:
                st.error(f"Xato! ❌ To'g'ri javob: {st.session_state.feedback['ans']}")

        # Check if finished
        if st.session_state.question_count >= st.session_state.total_questions:
            st.session_state.end_time = time.time()
            st.session_state.quiz_state = 'finished'
            st.rerun()

        q_idx = st.session_state.question_count
        q_data = st.session_state.quiz_questions[q_idx]

        q_num = q_idx + 1
        total_q = st.session_state.total_questions

        st.progress(q_idx / total_q)
        st.markdown(f"**Savol {q_num}/{total_q}** | Ball: <span class='highlight'>{st.session_state.score}</span>", unsafe_allow_html=True)

        st.header(q_data['question'])

        with st.form(key=f"q_form_{q_num}"):
            # Shuffle options for display? Text implies A, B, C, D are fixed.
            # "A) 30"
            # If I shuffle, A) might be at position 3. That's confusing.
            # Better to keep order A, B, C, D as in source.
            options = q_data['options']

            # The answer is stored as the full string "B) 20" or similar.

            user_ans = st.radio("Javobni tanlang:", options, index=None)

            submit = st.form_submit_button("Javob berish")

            if submit:
                if user_ans:
                    # Compare full string match
                    # Some cleaning might be needed if format varies
                    correct = (user_ans.strip() == q_data['answer'].strip())

                    if correct:
                        st.session_state.score += 1 # 1 point per question

                    st.session_state.feedback = {'correct': correct, 'ans': q_data['answer']}
                    st.session_state.question_count += 1
                    st.rerun()
                else:
                    st.warning("Iltimos, javobni tanlang!")

    elif st.session_state.quiz_state == 'finished':
        # Show last feedback
        if 'feedback' in st.session_state:
            if st.session_state.feedback['correct']:
                st.success("Oxirgi savol: To'g'ri! ✅")
            else:
                st.error(f"Oxirgi savol: Xato! ❌ To'g'ri javob: {st.session_state.feedback['ans']}")

        if 'saved' not in st.session_state or not st.session_state.saved:
             duration = round(st.session_state.end_time - st.session_state.start_time, 2)
             # Use topic name as level/context
             save_result(st.session_state.user_name, st.session_state.score, st.session_state.topic, duration)
             st.session_state.saved = True
             st.session_state.final_duration = duration

        st.balloons()
        st.title("🎉 Test tugadi!")
        st.subheader(f"{st.session_state.user_name}, natijalaringiz:")
        st.write(f"✅ **Jami ball:** {st.session_state.score} / {st.session_state.total_questions}")
        st.write(f"⏱ **Vaqt:** {st.session_state.final_duration} soniya")

        # Certificate condition: 100%
        if st.session_state.score == st.session_state.total_questions and st.session_state.total_questions > 0:
            st.success("Tabriklaymiz! Siz barcha savollarga to'g'ri javob berdingiz!")

            cert_img = create_certificate(st.session_state.user_name)
            st.image(cert_img, caption="Sizning sertifikatingiz", use_container_width=True)

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
