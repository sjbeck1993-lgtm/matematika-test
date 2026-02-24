import streamlit as st
import random
import time
import os
import io
import base64
import datetime
from PIL import Image, ImageDraw, ImageFont

# --- Vocabulary Constants ---
UZBEK_NAMES = [
    "Ali", "Vali", "Gani", "Sadiya", "Madina", "Temur", "Otabek", "Zilola", "Mohira", "Farruh",
    "Aziza", "Barno", "Jamshid", "Dilshod", "Nigora", "Anvar", "Malika", "Jasur", "Umid", "Laylo",
    "Bobur", "Kamola", "Sardor", "Dilnoza", "Shahzod", "Iroda", "Sanjar", "Nargiza", "Oybek", "Ra'no",
    "Ulug'bek", "Dildora", "Bekzod", "Feruza", "Javlon", "Gulnoza", "Ziyoda", "Sherzod", "Durdona", "Alisher",
    "Shahnoza", "Muzaffar", "Sevara", "Davron", "Charos", "Ilhom", "Yulduz", "Rustam", "Lobar", "Shoxrux"
]

UZBEK_OBJECTS = [
    "shar", "qalam", "daftar", "konfet", "qush", "velosiped", "olma", "nok", "uzum", "mashina",
    "qo'g'irchoq", "koptok", "gul", "daraxt", "mushuk", "kuchuk", "soat", "stul", "stol", "sumka",
    "kitob", "o'chirgich", "qoshiq", "piyola", "choynak", "varrak", "bayroq", "kalit", "tugma", "telefon",
    "kompyuter", "sichqoncha", "oynak", "shapka", "etik", "paypoq", "ko'ylak", "shim", "ro'mol", "non",
    "tuxum", "sut", "qaychi", "yelim", "bo'yoq", "mo'yqalam", "chizg'ich", "parta", "doska"
]

# --- Certificate Generator Logic ---
def create_certificate(name):
    # Dimensions (A4 Landscape approx @ 72dpi is 842x595, let's use 1000x700 for better res)
    width, height = 1000, 750
    background_color = (255, 255, 255)
    border_color = (0, 114, 206) # Blue from theme

    img = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(img)

    # Draw Border
    border_width = 20
    draw.rectangle(
        [(border_width, border_width), (width - border_width, height - border_width)],
        outline=border_color,
        width=10
    )

    # Load Fonts
    try:
        # Try to load a nice font
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
        name_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except IOError:
        # Fallback to default
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Add Logo
    if os.path.exists("logo.png"):
        try:
            logo = Image.open("logo.png")
            # Resize logo to reasonable size (e.g., 150px height)
            logo_height = 150
            aspect_ratio = logo.width / logo.height
            logo_width = int(logo_height * aspect_ratio)
            logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

            # Paste at top center
            x_pos = (width - logo_width) // 2
            y_pos = 50
            img.paste(logo, (x_pos, y_pos), logo if logo.mode == 'RGBA' else None)
        except Exception as e:
            print(f"Error loading logo: {e}")

    # Add Text
    def draw_centered_text(text, font, y, color=(0, 0, 0)):
        # textbbox returns (left, top, right, bottom)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), text, font=font, fill=color)

    y_offset = 220

    # "SERTIFIKAT"
    draw_centered_text("SERTIFIKAT", title_font, y_offset, color=border_color)
    y_offset += 80

    # "Ushbu sertifikat taqdim etiladi:"
    draw_centered_text("Ushbu sertifikat taqdim etiladi:", subtitle_font, y_offset)
    y_offset += 60

    # Name
    draw_centered_text(name, name_font, y_offset, color=(0, 0, 0))
    y_offset += 100

    # "Matematika bilimdoni"
    draw_centered_text("Matematika bilimdoni", text_font, y_offset, color=border_color)
    y_offset += 80

    # Date
    now = datetime.datetime.now()
    date_str = now.strftime("%d.%m.%Y %H:%M")
    draw_centered_text(f"Sana: {date_str}", small_font, height - 60, color=(100, 100, 100))

    return img

# --- Helper Functions ---
def get_names(n=2):
    return random.sample(UZBEK_NAMES, n)

def get_item():
    return random.choice(UZBEK_OBJECTS)

def format_options(correct_ans, options_list):
    """Formats a list of options into A) ..., B) ... format."""
    random.shuffle(options_list)
    formatted_options = []
    answer_str = ""
    labels = ["A", "B", "C"]

    for i, val in enumerate(options_list):
        opt_str = f"{labels[i]}) {val}"
        formatted_options.append(opt_str)
        if str(val) == str(correct_ans):
            answer_str = opt_str

    return formatted_options, answer_str

def generate_wrong_options(correct_ans, min_val=0, max_val=20, count=2):
    """Generates unique wrong options within range."""
    options = {correct_ans}
    attempts = 0
    while len(options) < count + 1 and attempts < 100:
        fake = correct_ans + random.randint(-5, 5)
        if min_val <= fake <= max_val and fake != correct_ans:
            options.add(fake)
        attempts += 1

    # Fallback if struggling to find unique within strict range
    while len(options) < count + 1:
        fake = random.randint(min_val, max_val)
        if fake != correct_ans:
            options.add(fake)

    return list(options)

# --- 1-sinf Generators ---

def gen_counting_1_10():
    count = random.randint(1, 10)
    item = get_item()
    # Using emojis for visual counting if possible, otherwise text description
    # Since we can't easily guarantee emojis map to objects, we use a generic shape or rely on text.
    # Let's try to use a simple repeating text or emoji.
    emoji_map = {
        "shar": "🎈", "qalam": "✏️", "daftar": "📓", "konfet": "🍬", "olma": "🍎",
        "mashina": "🚗", "koptok": "⚽", "gul": "🌸", "mushuk": "🐱", "kuchuk": "🐶"
    }
    emoji = emoji_map.get(item, "⭐️")

    visual = " ".join([emoji] * count)
    question_text = f"Quyidagi rasmdagi narsalarni sanang:\n\n{visual}\n\nNechta {item} bor?"
    ans = count
    options = generate_wrong_options(ans, 1, 10)
    return question_text, ans, options

def gen_comparison():
    n1 = random.randint(1, 10)
    n2 = random.randint(1, 10)
    while n1 == n2:
        n2 = random.randint(1, 10)

    names = get_names(2)
    item = get_item()

    question_text = f"{names[0]}da {n1} ta {item}, {names[1]}da {n2} ta {item} bor. Kimda ko'p?"
    ans = names[0] if n1 > n2 else names[1]
    options = [names[0], names[1], "Teng"]
    return question_text, ans, options

def gen_shapes():
    shapes = [
        ("Uchburchak", "3 ta burchagi bor shakl qaysi?"),
        ("Kvadrat", "Hamma tomoni teng bo'lgan to'rtburchak qaysi?"),
        ("Doira", "Burchagi yo'q shakl qaysi?"),
        ("To'g'ri to'rtburchak", "2 ta tomoni uzun, 2 ta tomoni qisqa bo'lgan shakl qaysi?")
    ]
    ans, question_text = random.choice(shapes)
    options = ["Uchburchak", "Kvadrat", "Doira", "To'g'ri to'rtburchak"]
    # Filter options to include answer and 2 others
    opts = [ans]
    while len(opts) < 3:
        o = random.choice(options)
        if o not in opts:
            opts.append(o)
    return question_text, ans, opts

def gen_left_right():
    scenarios = [
        ("o'ng", "chap"),
        ("chap", "o'ng")
    ]
    direction, opposite = random.choice(scenarios)
    items = random.sample(UZBEK_OBJECTS, 2)

    question_text = f"Stolning {direction} tomonida {items[0]}, {opposite} tomonida {items[1]} turibdi. {direction} tomonda nima bor?"
    ans = items[0]
    options = [items[0], items[1], "Hech narsa"]
    return question_text, ans, options

def gen_first_last():
    people = get_names(3)
    question_text = f"Bolalar safda turishibdi: {', '.join(people)}. Kim oxirida turibdi?"
    ans = people[-1]
    options = people
    return question_text, ans, options

def gen_neighbors():
    num = random.randint(2, 9)
    question_text = f"{num} sonining qo'shnilarini toping."
    ans = f"{num-1} va {num+1}"

    # Generate fake options
    fake1 = f"{num-2} va {num-1}" if num > 2 else f"{num+1} va {num+2}"
    fake2 = f"{num} va {num+2}"
    options = [ans, fake1, fake2]
    return question_text, ans, options

def gen_add_simple():
    n1 = random.randint(1, 5)
    n2 = random.randint(1, 5)
    ans = n1 + n2
    question_text = f"{n1} + {n2} = ?"
    options = generate_wrong_options(ans, 1, 10)
    return question_text, ans, options

def gen_sub_simple():
    n1 = random.randint(2, 10)
    n2 = random.randint(1, n1)
    ans = n1 - n2
    question_text = f"{n1} - {n2} = ?"
    options = generate_wrong_options(ans, 0, 10)
    return question_text, ans, options

def gen_logic_simple():
    # Simple verbal logic
    puzzles = [
        ("Muzlatgichda suv nima bo'ladi?", "Muzlaydi", ["Muzlaydi", "Qaynaydi", "Bug'lanadi"]),
        ("Qaysi biri uchadi?", "Qush", ["Qush", "Mushuk", "Kuchuk"]),
        ("Yozda havo qanday bo'ladi?", "Issiq", ["Issiq", "Sovuq", "Qorli"]),
        ("Baliq qayerda yashaydi?", "Suvda", ["Suvda", "Daraxtda", "Osmonda"])
    ]
    q, ans, opts = random.choice(puzzles)
    return q, ans, opts

def gen_even_odd():
    num = random.randint(1, 10)
    question_text = f"{num} soni juftmi yoki toqmi?"
    ans = "Juft" if num % 2 == 0 else "Toq"
    options = ["Juft", "Toq", "Bilmayman"]
    return question_text, ans, options

def gen_measuring():
    l1 = random.randint(1, 10)
    l2 = random.randint(1, 10)
    while l1 == l2: l2 = random.randint(1, 10)

    item1 = get_item()
    item2 = get_item()

    question_text = f"{item1}ning uzunligi {l1} sm, {item2}niki esa {l2} sm. Qaysi biri uzun?"
    ans = item1 if l1 > l2 else item2
    options = [item1, item2, "Teng"]
    return question_text, ans, options

def gen_segments():
    # Text-based geometry logic
    shapes = [
        ("Uchburchak", 3),
        ("Kvadrat", 4),
        ("Beshburchak", 5)
    ]
    shape, sides = random.choice(shapes)
    question_text = f"{shape}da nechta tomon (kesma) bor?"
    ans = sides
    options = [3, 4, 5]
    return question_text, ans, options

def gen_counting_20():
    start = random.randint(1, 15)
    seq = [start, start+1, start+2]
    ans = start + 3
    question_text = f"Sanashni davom ettiring: {start}, {start+1}, {start+2}, ... ?"
    options = generate_wrong_options(ans, 1, 20)
    return question_text, ans, options

def gen_hidden_number():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    total = a + b
    question_text = f"{a} ga qanday sonni qo'shsak {total} bo'ladi? ({a} + ? = {total})"
    ans = b
    options = generate_wrong_options(ans, 1, 10)
    return question_text, ans, options

def gen_money():
    # Simple <= 20 simulation
    names = get_names(1)
    money = random.randint(10, 20)
    price = random.randint(1, 9)
    question_text = f"{names[0]}da {money} so'm bor. U {price} so'mga qalam oldi. Qancha puli qoldi?"
    ans = money - price
    options = generate_wrong_options(ans, 1, 20)
    return question_text, ans, options

def gen_time_days():
    days = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
    idx = random.randint(0, 5)
    question_text = f"Bugun {days[idx]}. Ertaga qaysi kun?"
    ans = days[idx+1]

    opts = [ans]
    while len(opts) < 3:
        d = random.choice(days)
        if d not in opts:
            opts.append(d)
    return question_text, ans, opts

def gen_heavy_light():
    pairs = [
        ("Fil", "Chumoli", "Fil"),
        ("Mashina", "Velosiped", "Mashina"),
        ("Tarvuz", "Olma", "Tarvuz"),
        ("Kitob", "Daftar", "Kitob") # Generally true
    ]
    heavy, light, heaviest = random.choice(pairs)
    question_text = f"{heavy} og'irmi yoki {light}?"
    ans = heavy
    options = [heavy, light, "Ikkisi teng"]
    return question_text, ans, options

def gen_sequences():
    # Pattern 1, 2, 1, 2...
    p1 = random.randint(1, 5)
    p2 = random.randint(1, 5)
    while p1 == p2: p2 = random.randint(1, 5)

    question_text = f"Ketma-ketlikni davom ettiring: {p1}, {p2}, {p1}, {p2}, ... ?"
    ans = p1
    options = [p1, p2, p1+p2]
    return question_text, ans, options

def gen_competition():
    # Mix of simple math and logic
    if random.random() < 0.5:
        return gen_add_simple()
    else:
        return gen_logic_simple()

def generate_1sinf_topic_questions(topic, count=10):
    questions = []

    generator_map = {
        "Sonlarni sanash (1-10)": gen_counting_1_10,
        "Kimda ko'p? (Taqqoslash)": gen_comparison,
        "Shakllarni topamiz": gen_shapes,
        "O'ng va chapni o'rganamiz": gen_left_right,
        "Birinchi va oxirgi tartibi": gen_first_last,
        "Qo'shni sonlarni top": gen_neighbors,
        "10 ichida qo'shish (Sodda)": gen_add_simple,
        "10 ichida ayirish (Sodda)": gen_sub_simple,
        "Zukko bolajon (Mantiq)": gen_logic_simple,
        "Juft va toq sonlar": gen_even_odd,
        "Chizg'ich bilan o'lchash": gen_measuring,
        "Kesmalarni sanash": gen_segments,
        "20 ichida sanash": gen_counting_20,
        "Yashiringan sonni top": gen_hidden_number,
        "So'm bilan hisob-kitob": gen_money,
        "Bugun, kecha va ertaga": gen_time_days,
        "Hafta kunlari tartibi": gen_time_days, # Similar logic
        "Og'ir va yengil narsalar": gen_heavy_light,
        "Navbatni davom ettir": gen_sequences,
        "Bilimdonlar bellashuvi": gen_competition
    }

    gen_func = generator_map.get(topic)

    # Fallback if topic not found exactly (though it should be)
    if not gen_func:
        gen_func = gen_add_simple

    for _ in range(count):
        q_text, ans, options = gen_func()

        formatted_options, answer_str = format_options(ans, options)

        questions.append({
            "question": q_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "1sinf_analog"
        })

    return questions


# --- 2nd & 3rd Grade + Mukammal Generators ---

def generate_2sinf_jadvalli(count=10):
    questions = []
    for _ in range(count):
        n1 = random.randint(2, 9)
        n2 = random.randint(2, 9)
        question_text = f"{n1} x {n2} = ?"
        ans = n1 * n2
        options = generate_wrong_options(ans, 4, 81, 2)
        formatted_options, answer_str = format_options(ans, options)
        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "2sinf_jadvalli"
        })
    return questions

def generate_2sinf_onliklar(count=10):
    questions = []
    for _ in range(count):
        op = random.choice(['add', 'sub'])
        if op == 'add':
            if random.random() < 0.5:
                n1 = random.randint(1, 9) * 10
                n2 = random.randint(1, 9) * 10
            else:
                n1 = random.randint(10, 89)
                n2 = 10
            ans = n1 + n2
            question_text = f"{n1} + {n2} = ?"
        else:
            if random.random() < 0.5:
                n1 = random.randint(2, 9) * 10
                n2 = random.randint(1, n1//10 - 1) * 10
            else:
                n1 = random.randint(20, 99)
                n2 = 10
            ans = n1 - n2
            question_text = f"{n1} - {n2} = ?"

        options = generate_wrong_options(ans, 10, 100, 2)
        formatted_options, answer_str = format_options(ans, options)
        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "2sinf_onliklar"
        })
    return questions

def generate_2sinf_matnli(count=10):
    questions = []
    for _ in range(count):
        names = get_names(2)
        q_type = random.choice(['fabric', 'logic'])

        if q_type == 'fabric':
            dresses = random.randint(2, 10)
            per_dress = random.randint(2, 4)
            total_material = dresses * per_dress

            if random.random() < 0.5:
                question_text = f"{total_material} metr matodan {dresses} ta ko'ylak tikishdi. Bitta ko'ylak uchun necha metr mato ketgan?"
                ans = per_dress
            else:
                question_text = f"Bitta ko'ylak uchun {per_dress} metr mato kerak. {total_material} metr matodan nechta ko'ylak tikish mumkin?"
                ans = dresses
        else:
             age1 = random.randint(7, 15)
             diff = random.randint(2, 5)
             age2 = age1 + diff
             question_text = f"{names[0]} {age1} yoshda. {names[1]} undan {diff} yosh katta. {names[1]} necha yoshda?"
             ans = age2

        options = generate_wrong_options(ans, 1, 100, 2)
        formatted_options, answer_str = format_options(ans, options)

        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "2sinf_matnli"
        })
    return questions

def generate_2sinf_questions(count=10):
    # Fallback generic generator
    questions = []
    for _ in range(count):
        # Mix of types
        choice = random.choice([generate_2sinf_jadvalli, generate_2sinf_onliklar, generate_2sinf_matnli])
        pool = choice(1)
        if pool:
            questions.append(pool[0])
    return questions

def generate_3sinf_word_problems(count=10):
    questions = []
    for _ in range(count):
        names = get_names(2)
        item = get_item()
        q_type = random.choice(['add', 'sub', 'mult', 'div'])

        if q_type == 'add':
            n1 = random.randint(10, 100)
            n2 = random.randint(10, 100)
            question_text = f"{names[0]} {n1} ta {item} oldi va yana {n2} ta oldi. Hammasi qancha?"
            ans = n1 + n2
        elif q_type == 'sub':
            n1 = random.randint(20, 100)
            n2 = random.randint(10, n1 - 10)
            question_text = f"{names[0]}da {n1} ta {item} bor edi. U {names[1]}ga {n2} tasini berdi. {names[0]}da nechta {item} qoldi?"
            ans = n1 - n2
        elif q_type == 'mult':
            n1 = random.randint(2, 10)
            n2 = random.randint(2, 10)
            question_text = f"{names[0]}da {n1} ta quti bor. Har bir qutida {n2} tadan {item} bor. Jami nechta {item} bor?"
            ans = n1 * n2
        else: # div
            total = random.randint(10, 100)
            divisor = random.randint(2, 10)
            while total % divisor != 0:
                total = random.randint(10, 100)
            question_text = f"{names[0]} {total} ta {item}ni {divisor} ta do'stiga teng bo'lib berdi. Har biriga nechtadan tegdi?"
            ans = total // divisor

        options = generate_wrong_options(ans, 0, 500, 2)
        formatted_options, answer_str = format_options(ans, options)

        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "mukammal"
        })
    return questions

def generate_olympiad_questions(count=10):
    questions = []
    for _ in range(count):
        # Placeholder for complex logic, reusing 3-sinf mixed with patterns
        q_type = random.choice(['logic', 'chain'])
        if q_type == 'logic':
            # Simple logic reusing 2sinf logic for now but harder numbers?
            # Keeping it simple as per original code structure
            names = get_names(2)
            n1 = random.randint(20, 50)
            n2 = random.randint(20, 50)
            question_text = f"{names[0]}da {n1} ta, {names[1]}da {n2} ta olma bor. {names[0]}da {names[1]}ga qaraganda nechta ko'p yoki kam olma bor (farqi)?"
            ans = abs(n1 - n2)
        else:
            start = random.randint(1, 20)
            step = random.randint(2, 9)
            seq = [start + i*step for i in range(5)]
            missing_idx = random.randint(1, 4)
            ans = seq[missing_idx]
            seq[missing_idx] = "?"
            question_text = f"Sonli zanjirni davom ettiring: {', '.join(map(str, seq))}"

        options = generate_wrong_options(ans, 0, 100, 2)
        formatted_options, answer_str = format_options(ans, options)

        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "olympiad"
        })
    return questions


# --- Main Generator Dispatcher ---

def generate_quiz(topic_name, count=10):
    # 1-sinf Specific Topics (The 20 new topics)
    if topic_name in [
        "Sonlarni sanash (1-10)", "Kimda ko'p? (Taqqoslash)", "Shakllarni topamiz",
        "O'ng va chapni o'rganamiz", "Birinchi va oxirgi tartibi", "Qo'shni sonlarni top",
        "10 ichida qo'shish (Sodda)", "10 ichida ayirish (Sodda)", "Zukko bolajon (Mantiq)",
        "Juft va toq sonlar", "Chizg'ich bilan o'lchash", "Kesmalarni sanash",
        "20 ichida sanash", "Yashiringan sonni top", "So'm bilan hisob-kitob",
        "Bugun, kecha va ertaga", "Hafta kunlari tartibi", "Og'ir va yengil narsalar",
        "Navbatni davom ettir", "Bilimdonlar bellashuvi"
    ]:
        return generate_1sinf_topic_questions(topic_name, count)

    # 2-sinf
    elif topic_name == "Jadvalli ko'paytirish":
        return generate_2sinf_jadvalli(count)
    elif topic_name == "O'nliklar bilan ishlash":
        return generate_2sinf_onliklar(count)
    elif topic_name == "Matnli masalalar":
        return generate_2sinf_matnli(count)
    elif "2-sinf" in topic_name:
         return generate_2sinf_questions(count)

    # 3-sinf
    elif "3-sinf" in topic_name or topic_name == "Matnli masalalar (3-sinf)":
        return generate_3sinf_word_problems(count)

    # Mukammal / Olimpiada
    elif "Olimpiada" in topic_name or "Mukammal" in topic_name:
        return generate_olympiad_questions(count)

    # Fallback
    else:
        return []

# --- UI Setup ---
st.set_page_config(page_title="SMART LEARNING CENTER: Mukammal Matematika", page_icon="📚")

def initialize_session():
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'home'
    if 'quiz_state' not in st.session_state:
        st.session_state.quiz_state = 'welcome'
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'question_count' not in st.session_state:
        st.session_state.question_count = 0
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []

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
    st.session_state.quiz_questions = []
    st.session_state.score = 0
    st.session_state.question_count = 0
    if 'topic' in st.session_state: del st.session_state.topic
    if 'feedback' in st.session_state: del st.session_state.feedback
    st.rerun()

def inject_css(theme_color, is_home=False):
    hover_color = "#0056b3"
    css = f"""
    <style>
    .stAppHeader {{ background-color: transparent; }}
    h1, h2, h3, .stHeading, span[data-testid="stHeader"] {{ color: {theme_color} !important; }}
    div.stButton > button:first-child {{
        background-color: {theme_color} !important;
        color: white !important;
        border-radius: 5px;
        border: none;
    }}
    div.stButton > button:first-child:hover {{
        background-color: {hover_color} !important;
    }}
    .highlight {{ background-color: #FFD700; padding: 5px; border-radius: 5px; color: #000; font-weight: bold; }}
    """
    if is_home:
        css += """
        div.stButton > button:first-child {
            height: 100px; font-size: 20px !important; font-weight: bold;
        }
        section[data-testid="stSidebar"] div.stButton > button:first-child {
            height: auto !important; font-size: 1rem !important; font-weight: normal !important;
        }
        """
    st.markdown(css, unsafe_allow_html=True)

def show_header():
    title = "Mukammal Matematika"
    subtitle = "SMART LEARNING CENTER"

    if st.session_state.current_view == '1-sinf':
        title = "1-sinf Mukammal Matematika (Analog tizim)"

    st.markdown(f"<h1 style='text-align: center;'>{subtitle}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>{title}</h3>", unsafe_allow_html=True)
    st.write("---")

def run_quiz_interface(topics_list):
    if st.session_state.quiz_state == 'welcome':
        name = st.text_input("Ismingizni kiriting:", key="user_name_input")
        topic = st.selectbox("Mavzuni tanlang:", topics_list)

        st.markdown("---")
        st.write("🏆 **Eng yaxshi 5 natija:**")
        top_scores = load_top_scores()
        if top_scores:
            for i, s in enumerate(top_scores, 1):
                st.write(f"{i}. **{s['name']}**: {s['score']} ball ({s['level']}, {s['time']}s)")
        else:
            st.write("Hozircha natijalar yo'q.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Boshlash", use_container_width=True):
                if name:
                    st.session_state.user_name = name
                    st.session_state.topic = topic
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
                        st.session_state.saved = False
                        if 'feedback' in st.session_state: del st.session_state.feedback
                        st.rerun()
                else:
                    st.error("Ismingizni kiriting!")
        with col2:
             # Redundant but kept for consistent UI layout request, maybe remove if strictly adhering to review?
             # Reviewer noted it's redundant. I'll keep it as it's part of the original request's implicit structure
             # or legacy UI, but I can make it just rerun.
             if st.button("Yangi savollar", use_container_width=True):
                 st.rerun()

    elif st.session_state.quiz_state == 'playing':
        if 'feedback' in st.session_state:
            if st.session_state.feedback['correct']:
                st.success("To'g'ri! ✅")
                st.balloons()
                if os.path.exists("barakalla.mp3"):
                     st.audio("barakalla.mp3", autoplay=True)
            else:
                st.error(f"Xato! ❌ To'g'ri javob: {st.session_state.feedback['ans']}")

        if st.session_state.question_count >= st.session_state.total_questions:
            st.session_state.end_time = time.time()
            st.session_state.quiz_state = 'finished'
            st.rerun()

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
                    if correct: st.session_state.score += 1
                    st.session_state.feedback = {'correct': correct, 'ans': q_data['answer']}
                    st.session_state.question_count += 1
                    st.rerun()
                else:
                    st.warning("Javobni tanlang!")

    elif st.session_state.quiz_state == 'finished':
        if 'feedback' in st.session_state:
             if st.session_state.feedback['correct']: st.success("Oxirgi savol: To'g'ri! ✅")
             else: st.error(f"Oxirgi savol: Xato! ❌ To'g'ri javob: {st.session_state.feedback['ans']}")

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
            st.success("Tabriklaymiz! 100% natija!")
            cert_img = create_certificate(st.session_state.user_name)
            st.image(cert_img, caption="Sertifikat", use_container_width=True)
            buf = io.BytesIO()
            cert_img.save(buf, format="PNG")
            st.download_button("📥 Sertifikatni yuklab olish", data=buf.getvalue(), file_name="Sertifikat.png", mime="image/png")

        if st.button("Qayta boshlash"):
            st.session_state.quiz_state = 'welcome'
            st.session_state.saved = False
            if 'feedback' in st.session_state: del st.session_state.feedback
            st.rerun()

def main():
    initialize_session()

    # Sidebar Logo
    if os.path.exists("logo.png"):
        with open("logo.png", "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.sidebar.markdown(
            f"""<div style="text-align: center; margin-bottom: 20px;">
                <img src="data:image/png;base64,{encoded}" style="width: 80px; border-radius: 50%;">
                <h4 style="color: #FFD700;">Mukammal Matematika</h4>
            </div>""", unsafe_allow_html=True
        )
    else:
        st.sidebar.markdown("""<div style="text-align: center; margin-bottom: 20px;">
            <h4 style="color: #FFD700;">Mukammal Matematika</h4></div>""", unsafe_allow_html=True)

    st.sidebar.title("Menyu")
    if st.sidebar.button("🏠 Bosh sahifa", use_container_width=True): set_view('home')
    if st.sidebar.button("1-sinf", use_container_width=True): set_view('1-sinf')
    if st.sidebar.button("2-sinf", use_container_width=True): set_view('2-sinf')
    if st.sidebar.button("3-sinf", use_container_width=True): set_view('3-sinf')
    st.sidebar.markdown("---")
    if st.sidebar.button("🏆 Mukammal Matematika", use_container_width=True): set_view('mukammal')

    color = "#0072CE"
    if st.session_state.current_view == '1-sinf': color = "#28a745"
    elif st.session_state.current_view == '2-sinf': color = "#003366"
    elif st.session_state.current_view == '3-sinf': color = "#0072CE"
    elif st.session_state.current_view == 'mukammal': color = "#FF4500"

    inject_css(color, is_home=(st.session_state.current_view == 'home'))
    show_header()

    if st.session_state.current_view == 'home':
        col1, col2 = st.columns([1, 2])
        with col2:
            if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("1-sinf", use_container_width=True): set_view('1-sinf')
        with c2:
            if st.button("2-sinf", use_container_width=True): set_view('2-sinf')
        with c3:
            if st.button("3-sinf", use_container_width=True): set_view('3-sinf')
        with c4:
            if st.button("Mukammal Matematika", use_container_width=True): set_view('mukammal')

    elif st.session_state.current_view == '1-sinf':
        topics_1sinf = [
            "Sonlarni sanash (1-10)", "Kimda ko'p? (Taqqoslash)", "Shakllarni topamiz",
            "O'ng va chapni o'rganamiz", "Birinchi va oxirgi tartibi", "Qo'shni sonlarni top",
            "10 ichida qo'shish (Sodda)", "10 ichida ayirish (Sodda)", "Zukko bolajon (Mantiq)",
            "Juft va toq sonlar", "Chizg'ich bilan o'lchash", "Kesmalarni sanash",
            "20 ichida sanash", "Yashiringan sonni top", "So'm bilan hisob-kitob",
            "Bugun, kecha va ertaga", "Hafta kunlari tartibi", "Og'ir va yengil narsalar",
            "Navbatni davom ettir", "Bilimdonlar bellashuvi"
        ]
        run_quiz_interface(topics_1sinf)

    elif st.session_state.current_view == '2-sinf':
        run_quiz_interface(["Jadvalli ko'paytirish", "O'nliklar bilan ishlash", "Matnli masalalar"])

    elif st.session_state.current_view == '3-sinf':
        run_quiz_interface(["Matnli masalalar (3-sinf)"])

    elif st.session_state.current_view == 'mukammal':
        run_quiz_interface(["Olimpiada masalalari"])

if __name__ == "__main__":
    main()
