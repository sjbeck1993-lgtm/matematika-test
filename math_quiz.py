import streamlit as st
import random
import time
import os
import io
import json
import base64
from certificate import create_certificate
from generators import generate_quiz

# Set page config
st.set_page_config(page_title="SMART LEARNING CENTER: Mukammal Matematika", page_icon="📚")

# --- State Management ---
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'home' # home, 1-sinf, 2-sinf, 3-sinf, mukammal
if 'quiz_state' not in st.session_state:
    st.session_state.quiz_state = 'welcome' # welcome, playing, finished
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0

# --- Helper Functions ---
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
                        'level': level,
                        'time': float(duration)
                    })
            except ValueError:
                continue
    scores.sort(key=lambda x: (-x['score'], x['time']))
    return scores[:5]

def save_result(name, score, level, duration):
    with open("results.txt", "a") as file:
        file.write(f"{name},{score},{level},{duration}\n")

def set_view(view):
    st.session_state.current_view = view
    st.session_state.quiz_state = 'welcome'
    st.rerun()

# --- CSS Injection ---
def inject_css(theme_color, is_home=False):
    hover_color = "#0056b3" # Default
    if theme_color == "#28a745": hover_color = "#218838"
    if theme_color == "#003366": hover_color = "#002244"
    if theme_color == "#0072CE": hover_color = "#0056b3"
    if theme_color == "#FF4500": hover_color = "#CC3700"

    # Base CSS
    css = f"""
    <style>
    .stAppHeader {{
        background-color: transparent;
    }}
    h1, h2, h3, .stHeading, span[data-testid="stHeader"] {{
        color: {theme_color} !important;
    }}
    /* Custom Card Style for Home */
    .card {{
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        cursor: pointer;
        transition: 0.3s;
    }}
    .card:hover {{
        background-color: #e0e2e6;
        transform: scale(1.02);
    }}
    .card h3 {{
        color: {theme_color};
    }}

    .highlight {{
        background-color: #FFD700;
        padding: 5px;
        border-radius: 5px;
        color: #000000;
        font-weight: bold;
    }}

    /* Standard Button Style */
    div.stButton > button:first-child {{
        background-color: {theme_color} !important;
        color: white !important;
        border-radius: 5px;
        border: none;
    }}
    div.stButton > button:first-child:hover {{
        background-color: {hover_color} !important;
    }}
    """

    if is_home:
        # Inject Big Button styles for Home but reset for Sidebar
        css += f"""
        /* Big buttons for Home Main Area */
        div.stButton > button:first-child {{
            height: 100px;
            font-size: 20px !important;
            font-weight: bold;
        }}

        /* Reset Sidebar buttons to normal */
        section[data-testid="stSidebar"] div.stButton > button:first-child {{
            height: auto !important;
            font-size: 1rem !important;
            font-weight: normal !important;
        }}
        """
    else:
        # Ensure sidebar buttons (and other buttons) are normal size on other pages
        css += """
        div.stButton > button:first-child {
            height: auto !important;
            font-size: 1rem !important;
            font-weight: normal !important;
        }
        """

    css += "</style>"
    st.markdown(css, unsafe_allow_html=True)

def show_header():
    st.markdown("<h1 style='text-align: center;'>SMART LEARNING CENTER</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Mukammal Matematika</h3>", unsafe_allow_html=True)
    st.write("---")

# --- Views ---

def show_home_buttons():
    col1, col2 = st.columns([1, 2])
    with col2:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)

    st.write("")

    # Navigation Cards (4 buttons)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button("1-sinf", use_container_width=True):
            set_view('1-sinf')
    with c2:
        if st.button("2-sinf", use_container_width=True):
            set_view('2-sinf')
    with c3:
        if st.button("3-sinf", use_container_width=True):
            set_view('3-sinf')
    with c4:
        if st.button("Mukammal Matematika", use_container_width=True):
            set_view('mukammal')

def show_class_view(class_name, topics):
    col1, col2 = st.columns([1, 4])
    with col1:
         if st.button("⬅️ Orqaga"):
             set_view('home')
    with col2:
        st.header(f"{class_name} Matematika" if "Mukammal" not in class_name else class_name)

    run_quiz_interface(topics)

def run_quiz_interface(topics_list):
    if st.session_state.quiz_state == 'welcome':
        name = st.text_input("Ismingizni kiriting:", key="user_name_input")
        topic = st.selectbox("Mavzuni tanlang:", topics_list)

        st.markdown("---")
        st.write("🏆 **Eng yaxshi 5 natija:**")
        top_scores = load_top_scores()
        if top_scores:
            for i, s in enumerate(top_scores, 1):
                st.write(f"{i}. **{s['name']}**: {s['score']} ball (Mavzu: {s['level']}, Vaqt: {s['time']}s)")
        else:
            st.write("Hozircha natijalar yo'q.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Boshlash", use_container_width=True):
                if name:
                    st.session_state.user_name = name
                    st.session_state.topic = topic

                    # Generate Questions
                    pool = generate_quiz(topic, 10)
                    if not pool:
                        st.error("Savollar topilmadi.")
                    else:
                        st.session_state.quiz_questions = pool
                        st.session_state.total_questions = len(pool)
                        st.session_state.score = 0
                        st.session_state.question_count = 0
                        st.session_state.start_time = time.time()
                        st.session_state.quiz_state = 'playing'
                        if 'feedback' in st.session_state: del st.session_state.feedback
                        st.rerun()
                else:
                    st.error("Iltimos, ismingizni kiriting!")
        with col2:
             if st.button("Yangi savollar", use_container_width=True):
                 st.success("Savollar yangilanmoqda...")
                 # Just rerun to refresh random seeds if needed, though 'Boshlash' calls generate_quiz fresh anyway.
                 st.rerun()

    elif st.session_state.quiz_state == 'playing':
        # Feedback Display
        if 'feedback' in st.session_state:
            if st.session_state.feedback['correct']:
                st.success("To'g'ri! ✅")
                st.balloons()
                if os.path.exists("barakalla.mp3"):
                     st.audio("barakalla.mp3", autoplay=True)
            else:
                st.error(f"Xato! ❌ To'g'ri javob: {st.session_state.feedback['ans']}")

        # Check finish
        if st.session_state.question_count >= st.session_state.total_questions:
            st.session_state.end_time = time.time()
            st.session_state.quiz_state = 'finished'
            st.rerun()

        # Display Question
        q_idx = st.session_state.question_count
        q_data = st.session_state.quiz_questions[q_idx]
        q_num = q_idx + 1
        total = st.session_state.total_questions

        st.progress(q_idx / total)
        st.markdown(f"**Savol {q_num}/{total}** | Ball: <span class='highlight'>{st.session_state.score}</span>", unsafe_allow_html=True)
        st.header(q_data['question'])

        with st.form(key=f"q_form_{q_num}"):
            user_ans = st.radio("Javobni tanlang:", q_data['options'], index=None)
            if st.form_submit_button("Javob berish"):
                if user_ans:
                    correct = (user_ans.strip() == q_data['answer'].strip())
                    if correct:
                        st.session_state.score += 1

                    st.session_state.feedback = {'correct': correct, 'ans': q_data['answer']}
                    st.session_state.question_count += 1
                    st.rerun()
                else:
                    st.warning("Javobni tanlang!")

    elif st.session_state.quiz_state == 'finished':
        # Show last feedback
        if 'feedback' in st.session_state:
             if st.session_state.feedback['correct']:
                st.success("Oxirgi savol: To'g'ri! ✅")
             else:
                st.error(f"Oxirgi savol: Xato! ❌ To'g'ri javob: {st.session_state.feedback['ans']}")

        if 'saved' not in st.session_state or not st.session_state.saved:
             duration = round(st.session_state.end_time - st.session_state.start_time, 2)
             save_result(st.session_state.user_name, st.session_state.score, st.session_state.topic, duration)
             st.session_state.saved = True
             st.session_state.final_duration = duration

        st.balloons()
        st.title("🎉 Test tugadi!")
        st.subheader(f"{st.session_state.user_name}, natijalaringiz:")
        st.write(f"✅ **Jami ball:** {st.session_state.score} / {st.session_state.total_questions}")
        st.write(f"⏱ **Vaqt:** {st.session_state.final_duration} soniya")

        if st.session_state.score == st.session_state.total_questions and st.session_state.total_questions > 0:
            st.success("Tabriklaymiz! Siz barcha savollarga to'g'ri javob berdingiz!")
            cert_img = create_certificate(st.session_state.user_name)
            st.image(cert_img, caption="Sertifikat", use_container_width=True)

            buf = io.BytesIO()
            cert_img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.download_button("📥 Sertifikatni yuklab olish", data=byte_im, file_name="Sertifikat.png", mime="image/png")

        if st.button("Qayta boshlash"):
            st.session_state.quiz_state = 'welcome'
            st.session_state.saved = False
            if 'feedback' in st.session_state: del st.session_state.feedback
            st.rerun()


# --- Main Dispatcher ---
def main():
    # Sidebar Header
    if os.path.exists("logo.png"):
        with open("logo.png", "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()

        st.sidebar.markdown(
            f"""
            <div style="background-color: #003366; padding: 20px; border-radius: 10px; border: 2px solid #FFD700; text-align: center; margin-bottom: 20px;">
                <img src="data:image/png;base64,{encoded}" style="width: 80px; margin-bottom: 10px; border-radius: 50%;">
                <p style="color: white; font-size: 12px; margin: 0;">Sardorbek Jo'raboyev muallifligidagi</p>
                <h4 style="color: #FFD700; margin: 0; padding-top: 5px;">Mukammal Matematika platformasi</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.sidebar.markdown(
            """
            <div style="background-color: #003366; padding: 20px; border-radius: 10px; border: 2px solid #FFD700; text-align: center; margin-bottom: 20px;">
                <div style="width: 60px; height: 60px; background-color: #FFD700; border-radius: 50%; display: inline-block; margin-bottom: 10px; line-height: 60px; color: #003366; font-weight: bold; font-size: 24px;">M</div>
                <p style="color: white; font-size: 12px; margin: 0;">Sardorbek Jo'raboyev muallifligidagi</p>
                <h4 style="color: #FFD700; margin: 0; padding-top: 5px;">Mukammal Matematika platformasi</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Sidebar
    st.sidebar.title("Menyu")
    if st.sidebar.button("🏠 Bosh sahifa", use_container_width=True):
        set_view('home')
    if st.sidebar.button("1-sinf", use_container_width=True):
        set_view('1-sinf')
    if st.sidebar.button("2-sinf", use_container_width=True):
        set_view('2-sinf')
    if st.sidebar.button("3-sinf", use_container_width=True):
        set_view('3-sinf')

    st.sidebar.markdown("---")
    if st.sidebar.button("🏆 Mukammal Matematika", use_container_width=True):
        set_view('mukammal')

    # Determine Theme Color
    color = "#0072CE" # Default Blue
    if st.session_state.current_view == '1-sinf':
        color = "#28a745"
    elif st.session_state.current_view == '2-sinf':
        color = "#003366"
    elif st.session_state.current_view == '3-sinf':
        color = "#0072CE"
    elif st.session_state.current_view == 'mukammal':
        color = "#FF4500"

    # Inject CSS & Show Header
    inject_css(color, is_home=(st.session_state.current_view == 'home'))
    show_header()

    # Main Content
    if st.session_state.current_view == 'home':
        show_home_buttons()
    elif st.session_state.current_view == '1-sinf':
        show_class_view("1-sinf", ["Sonlar olami", "Sodda yig'indi", "Mantiqiy o'yinlar"])
    elif st.session_state.current_view == '2-sinf':
        show_class_view("2-sinf", ["Jadvalli ko'paytirish", "O'nliklar bilan ishlash", "Matnli masalalar"])
    elif st.session_state.current_view == '3-sinf':
        show_class_view("3-sinf", ["Matnli masalalar (3-sinf)"])
    elif st.session_state.current_view == 'mukammal':
        show_class_view("Mukammal Matematika", ["Olimpiada masalalari"])

if __name__ == "__main__":
    main()
