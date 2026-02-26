import streamlit as st
import random
import time
import os
import io
import base64
import datetime
import sqlite3
import json
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# --- Database Helper Functions ---
def init_db():
    conn = sqlite3.connect('math_quiz.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students
                 (student_id INTEGER PRIMARY KEY, full_name TEXT, phone TEXT UNIQUE,
                  attendance_count INTEGER DEFAULT 0, homework_status TEXT DEFAULT '[]',
                  balance INTEGER DEFAULT 0, registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def get_student_by_phone(phone):
    conn = sqlite3.connect('math_quiz.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE phone=?", (phone,))
    student = c.fetchone()
    conn.close()
    return student

def register_student(full_name, phone):
    conn = sqlite3.connect('math_quiz.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO students (full_name, phone) VALUES (?, ?)", (full_name, phone))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def update_student_field(student_id, field, value):
    conn = sqlite3.connect('math_quiz.db')
    c = conn.cursor()
    # Validate field to prevent injection (though internal use only)
    if field in ['attendance_count', 'balance', 'full_name', 'phone']:
        c.execute(f"UPDATE students SET {field}=? WHERE student_id=?", (value, student_id))
        conn.commit()
    conn.close()

def add_homework_result(student_id, result):
    conn = sqlite3.connect('math_quiz.db')
    c = conn.cursor()
    c.execute("SELECT homework_status FROM students WHERE student_id=?", (student_id,))
    row = c.fetchone()
    if row:
        current_status = row[0]
        try:
            homework_list = json.loads(current_status) if current_status else []
        except:
            homework_list = []

        homework_list.append(result)
        new_status = json.dumps(homework_list)

        c.execute("UPDATE students SET homework_status=? WHERE student_id=?", (new_status, student_id))
        conn.commit()
    conn.close()

def get_all_students():
    conn = sqlite3.connect('math_quiz.db')
    try:
        df = pd.read_sql_query("SELECT * FROM students", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

# --- Vocabulary Constants ---
UZBEK_NAMES = [
    "Ali", "Vali", "Gani", "Sadiya", "Madina", "Temur", "Otabek", "Zilola", "Mohira", "Farruh",
    "Aziza", "Barno", "Jamshid", "Dilshod", "Nigora", "Anvar", "Malika", "Jasur", "Umid", "Laylo",
    "Bobur", "Kamola", "Sardor", "Dilnoza", "Shahzod", "Iroda", "Sanjar", "Nargiza", "Oybek", "Ra'no",
    "Ulug'bek", "Dildora", "Bekzod", "Feruza", "Javlon", "Gulnoza", "Ziyoda", "Sherzod", "Durdona", "Alisher",
    "Shahnoza", "Muzaffar", "Sevara", "Davron", "Charos", "Ilhom", "Yulduz", "Rustam", "Lobar", "Shoxrux",
    "Lola", "Bahodir", "Nodira", "Botir", "Kumush", "Odil", "Zafar", "Karim", "Salim", "Nasiba",
    "Zahro", "Husniddin", "Sojida", "Murod", "Dilfuza", "Ruxshona", "Akmal", "Nodir", "Jamol", "Sarvinoz",
    "Tohir", "Zuhra", "Fotima", "Hasan", "Husan", "Shabnam", "Munira", "Saida", "Aziz", "Ravshan",
    "Malohat", "Nozima", "Farida", "Umida", "Jahongir", "Shokir", "Bahrom", "Abbos", "Shohruh", "Guli",
    "Maftuna", "Zarina", "Nilufar", "Oydin", "Zamira", "Ozoda", "Hilola", "Adolat", "Sobir", "G'ayrat"
]

UZBEK_OBJECTS = [
    "shar", "qalam", "daftar", "konfet", "qush", "velosiped", "olma", "nok", "uzum", "mashina",
    "qo'g'irchoq", "koptok", "gul", "daraxt", "mushuk", "kuchuk", "soat", "stul", "stol", "sumka",
    "kitob", "o'chirgich", "qoshiq", "piyola", "choynak", "varrak", "bayroq", "kalit", "tugma", "telefon",
    "kompyuter", "sichqoncha", "oynak", "shapka", "etik", "paypoq", "ko'ylak", "shim", "ro'mol", "non",
    "tuxum", "sut", "qaychi", "yelim", "bo'yoq", "mo'yqalam", "chizg'ich", "parta", "doska",
    "chiroq", "gilam", "eshik", "deraza", "parda", "ko'rpa", "yostiq", "sochiq", "sovun", "taroq",
    "oyna", "supurgi", "chelak", "jo'mrak", "quvur", "g'isht", "qog'oz", "quti", "savat", "jo'xori",
    "bug'doy", "un", "yog'", "shakar", "tuz", "murch", "piyoz", "kartoshka", "sabzi", "bodring", "pomidor",
    "karam", "qovun", "tarvuz", "anjir", "shaftoli", "o'rik", "gilos", "behi", "anor", "limon",
    "apelsin", "mandarin", "banan", "kivi", "xurmo", "yong'oq", "bodom", "pista", "mayiz", "qalamdon"
]

# --- Topic Constants ---
TOPICS_1SINF = [
    "Sonlarni sanash (1-10)", "Kimda ko'p? (Taqqoslash)", "Shakllarni topamiz",
    "O'ng va chapni o'rganamiz", "Birinchi va oxirgi tartibi", "Qo'shni sonlarni top",
    "10 ichida qo'shish (Sodda)", "10 ichida ayirish (Sodda)", "Zukko bolajon (Mantiq)",
    "Juft va toq sonlar", "Chizg'ich bilan o'lchash", "Kesmalarni sanash",
    "20 ichida sanash", "Yashiringan sonni top", "So'm bilan hisob-kitob",
    "Bugun, kecha va ertaga", "Hafta kunlari tartibi", "Og'ir va yengil narsalar",
    "Navbatni davom ettir", "Bilimdonlar bellashuvi"
]

TOPICS_2SINF = [
    "Ikki xonali sonlar (1-100)", "Yuzlik ichida qo'shish (Analog)", "Yuzlik ichida ayirish (Analog)",
    "Ko'paytirish jadvali (Dinamik)", "Bo'lish asoslari (Mantiqiy)", "Sonli ketma-ketliklar",
    "Perimetr hisoblash (To'rtburchak)", "Vaqt: Soat va minutlar", "Og'irlik: kg va gramm",
    "Qavsli amallar tartibi", "Taqqoslash (Katta, kichik, teng)", "Pul birliklari (So'm)",
    "Uzunlik o'lchovlari (sm, dm, m)", "Geometrik shakllar xossalari", "Juft va toq sonlar (100 gacha)",
    "Tenglamalar (Noma'lum qo'shiluvchini topish)", "Mantiqiy masalalar (Yoshga doir)",
    "Kasr tushunchasi (Yarim, chorak)", "Ko'paytirish va bo'lish (Matnli)", "Murakkab ifodalar"
]

TOPICS_3SINF = [
    "Uch xonali sonlar (1-1000)", "Mantiqiy tenglamalar (Sodda)", "Harakatga doir: Tezlik va masofa",
    "Yuzani hisoblash (Kvadrat)", "Ustun shaklida ko'paytirish", "Qoldiqli bo'lish",
    "Zulmira va qavatlar (Mantiqiy tuzoq)", "Kasrlar bilan tanishuv", "Diagramma va jadvallar",
    "Olimpiada masalalari (Analog)", "Rim raqamlari", "Yaxlitlash (O'nlik va yuzlikkacha)",
    "Vaqt birliklari (Asr, yil, oy)", "Geometriya: Uchburchak turlari", "Massani hisoblash (kg, t)",
    "Uzunlikni hisoblash (km, m)", "Hajm birliklari (Litr)", "3 ta amal qatnashgan ifodalar",
    "Mantiqiy ketma-ketliklar (Murakkab)", "Matnli masalalar (Ikki bosqichli)"
]

TOPICS_MUKAMMAL = [
    "1. Qo‘shish va ayirishga doir mantiqiy masalalar",
    "2. Ko‘paytirish va bo‘lishga doir mantiqiy masalalar",
    "3. To‘rt amalga doir murakkab masalalar",
    "4. Raqamlar va natural sonlar siri",
    "5. Xona birliklari va razryadlar mantiqi",
    "6. Ko‘p xonali sonlarni taqqoslash (Mantiqiy)",
    "7. Natural sonlarni yaxlitlash mantiqi",
    "8. Rim raqamlari (Gugurt cho'pi jumboqlari)",
    "9. Geometriya: To‘g‘ri chiziq, nur va kesma",
    "10. Siniq chiziq va uning uzunligi",
    "11. Ko‘pburchaklar va ularning perimetri",
    "12. To‘g‘ri to‘rtburchak va kvadrat (Murakkab)",
    "13. Vaqt va vaqt birliklari (Kabisa yili mantiqi)",
    "14. Mantiqiy savollar: Shamlar va tayoqchalar",
    "15. Harakatga doir: Poezd va tunnel",
    "16. Daryo oqimi bo‘ylab va qarshi harakat",
    "17. Ish unumdorligi (Birgalikda ishlash)",
    "18. Geometriya: Yuza va hajm (3D tasavvur)",
    "19. To‘plamlar va Venn diagrammasi",
    "20. Mantiqiy xulosalar va algoritmlar"
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
        ("To'g'ri to'rtburchak", "2 ta tomoni uzun, 2 ta tomoni qisqa bo'lgan shakl qaysi?"),
        ("Beshburchak", "5 ta burchagi bor shakl qaysi?"),
        ("Oltiburchak", "6 ta burchagi bor shakl qaysi?"),
        ("Romb", "Hamma tomonlari teng, lekin burchaklari to'g'ri bo'lmagan to'rtburchak qaysi?")
    ]
    ans, question_text = random.choice(shapes)
    options = ["Uchburchak", "Kvadrat", "Doira", "To'g'ri to'rtburchak", "Beshburchak", "Oltiburchak", "Romb"]
    # Filter options to include answer and 2 others
    opts = [ans]
    while len(opts) < 3:
        o = random.choice(options)
        if o not in opts:
            opts.append(o)
    return question_text, ans, opts

def gen_left_right():
    if random.random() < 0.7:
        scenarios = [
            ("o'ng", "chap"),
            ("chap", "o'ng")
        ]
        direction, opposite = random.choice(scenarios)
        items = random.sample(UZBEK_OBJECTS, 2)

        question_text = f"Stolning {direction} tomonida {items[0]}, {opposite} tomonida {items[1]} turibdi. {direction} tomonda nima bor?"
        ans = items[0]
        options = [items[0], items[1], "Hech narsa"]
    else:
        items = random.sample(UZBEK_OBJECTS, 3)
        question_text = f"Stol ustida {items[0]}, {items[1]} va {items[2]} turibdi. {items[1]} {items[0]} va {items[2]}ning o'rtasida. O'rtada nima bor?"
        ans = items[1]
        options = items
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
        ("Baliq qayerda yashaydi?", "Suvda", ["Suvda", "Daraxtda", "Osmonda"]),
        ("Qishda nima yog'adi?", "Qor", ["Qor", "Yomg'ir", "Barg"]),
        ("Daraxtda nima o'sadi?", "Meva", ["Meva", "Non", "Konfet"]),
        ("Maktabga nima uchun boramiz?", "O'qish uchun", ["O'qish uchun", "Uxlash uchun", "O'ynash uchun"]),
        ("Qaysi faslda gullar ochiladi?", "Bahorda", ["Bahorda", "Qishda", "Kuzda"]),
        ("Quyosh qachon chiqadi?", "Kunduzi", ["Kunduzi", "Kechasi", "Qishda"]),
        ("Oy qachon chiqadi?", "Kechasi", ["Kechasi", "Kunduzi", "Tushda"]),
        ("Svetoforning qaysi rangida to'xtash kerak?", "Qizil", ["Qizil", "Yashil", "Sariq"]),
        ("Qaysi hayvon vovullaydi?", "Kuchuk", ["Kuchuk", "Mushuk", "Sigir"]),
        ("Qaysi hayvon miyovlaydi?", "Mushuk", ["Mushuk", "Kuchuk", "Ot"]),
        ("Qo'l yuvish uchun nima kerak?", "Sovun va suv", ["Sovun va suv", "Qalam va qog'oz", "Osh va non"]),
        ("Choyni nima bilan ichamiz?", "Piyola", ["Piyola", "Qozon", "Chelak"]),
        ("Rasmni nima bilan chizamiz?", "Qalam", ["Qalam", "Qoshiq", "Taroq"])
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
    idx = random.randint(0, 6)

    q_type = random.choice(["ertaga", "kecha", "indin"])

    if q_type == "ertaga":
        question_text = f"Bugun {days[idx]}. Ertaga qaysi kun?"
        ans_idx = (idx + 1) % 7
    elif q_type == "kecha":
        question_text = f"Bugun {days[idx]}. Kecha qaysi kun edi?"
        ans_idx = (idx - 1) % 7
    else: # indin
        question_text = f"Bugun {days[idx]}. Indin (ertadan keyin) qaysi kun?"
        ans_idx = (idx + 2) % 7

    ans = days[ans_idx]

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
        ("Kitob", "Daftar", "Kitob"), # Generally true
        ("Tosh", "Pat", "Tosh"),
        ("Qozon", "Qoshiq", "Qozon"),
        ("Avtobus", "Samokat", "Avtobus"),
        ("Kit", "Baliq", "Kit"),
        ("Daraxt", "Gul", "Daraxt"),
        ("Stol", "Stul", "Stol"),
        ("Kompyuter", "Telefon", "Kompyuter"),
        ("Yuk mashinasi", "Yengil mashina", "Yuk mashinasi"),
        ("Tarvuz", "Uzum", "Tarvuz"),
        ("Qop", "Xalta", "Qop")
    ]
    heavy, light, heaviest = random.choice(pairs)
    question_text = f"{heavy} og'irmi yoki {light}?"
    ans = heavy
    options = [heavy, light, "Ikkisi teng"]
    return question_text, ans, options

def gen_sequences():
    # Multiple patterns
    p_type = random.choice(["repeat", "step2", "step3", "reverse", "double"])

    if p_type == "repeat":
        p1 = random.randint(1, 5)
        p2 = random.randint(1, 5)
        while p1 == p2: p2 = random.randint(1, 5)
        question_text = f"Ketma-ketlikni davom ettiring: {p1}, {p2}, {p1}, {p2}, ... ?"
        ans = p1
        options = [p1, p2, p1+p2]

    elif p_type == "step2":
        start = random.randint(1, 10)
        seq = [start, start+2, start+4, start+6]
        question_text = f"Ketma-ketlikni davom ettiring: {seq[0]}, {seq[1]}, {seq[2]}, ... ?"
        ans = seq[3]
        options = [seq[3], seq[3]-1, seq[3]+1]

    elif p_type == "step3":
        start = random.randint(1, 10)
        seq = [start, start+3, start+6, start+9]
        question_text = f"Ketma-ketlikni davom ettiring: {seq[0]}, {seq[1]}, {seq[2]}, ... ?"
        ans = seq[3]
        options = [seq[3], seq[3]-1, seq[3]+1]

    elif p_type == "reverse":
        start = random.randint(10, 20)
        seq = [start, start-1, start-2, start-3]
        question_text = f"Orqaga sanang: {seq[0]}, {seq[1]}, {seq[2]}, ... ?"
        ans = seq[3]
        options = [seq[3], seq[3]+2, seq[3]-2]

    else: # double
        start = random.randint(1, 5)
        seq = [start, start*2, start*4, start*8]
        question_text = f"Ketma-ketlikni davom ettiring: {seq[0]}, {seq[1]}, {seq[2]}, ... ?"
        ans = seq[3]
        options = [seq[3], seq[3]-2, seq[3]+2]

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

    seen = set()
    attempts = 0
    max_attempts = count * 10

    while len(questions) < count and attempts < max_attempts:
        attempts += 1
        q_text, ans, options = gen_func()

        if q_text in seen:
            continue
        seen.add(q_text)

        formatted_options, answer_str = format_options(ans, options)

        questions.append({
            "question": q_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "1sinf_analog"
        })

    random.shuffle(questions)
    return questions


# --- 3rd Grade Generators ---

def gen_3_digits_1000():
    # Place value or simple add/sub
    n = random.randint(100, 999)
    if random.random() < 0.5:
        # Place value
        hundreds = n // 100
        tens = (n % 100) // 10
        units = n % 10
        question_text = f"{n} sonida nechta yuzlik, o'nlik va birlik bor?"
        ans = f"{hundreds} yuzlik, {tens} o'nlik, {units} birlik"
        f1 = f"{hundreds} yuzlik, {units} o'nlik, {tens} birlik"
        f2 = f"{tens} yuzlik, {hundreds} o'nlik, {units} birlik"
        options = [ans, f1, f2]
    else:
        # Comparison
        n2 = random.randint(100, 999)
        while n == n2: n2 = random.randint(100, 999)
        question_text = f"{n} ... {n2}. Qaysi belgi mos?"
        ans = ">" if n > n2 else "<"
        options = [">", "<", "="]
    return question_text, ans, options

def gen_logic_equations():
    # x * a + b = c
    a = random.randint(2, 9)
    x = random.randint(2, 9)
    b = random.randint(1, 20)
    c = x * a + b
    question_text = f"Tenglamani yeching: x * {a} + {b} = {c}"
    ans = x
    options = generate_wrong_options(ans, 1, 20)
    return question_text, ans, options

def gen_speed_distance():
    v = random.randint(30, 80) # km/h
    t = random.randint(2, 5)   # h
    s = v * t
    if random.random() < 0.5:
        question_text = f"Avtomobil {v} km/soat tezlik bilan {t} soat yurdi. U qancha masofani bosib o'tgan?"
        ans = s
    else:
        question_text = f"Avtomobil {s} km masofani {t} soatda bosib o'tdi. Uning tezligini toping."
        ans = v
    options = generate_wrong_options(ans, 10, 500)
    return question_text, ans, options

def gen_area_square():
    # Square or Rectangle area
    if random.random() < 0.5:
        a = random.randint(2, 12)
        ans = a * a
        question_text = f"Kvadratning tomoni {a} sm. Uning yuzini toping (kv. sm)."
    else:
        a = random.randint(2, 10)
        b = random.randint(2, 10)
        ans = a * b
        question_text = f"To'g'ri to'rtburchakning tomonlari {a} sm va {b} sm. Uning yuzini toping."
    options = generate_wrong_options(ans, 4, 144)
    return question_text, ans, options

def gen_column_mult():
    # 2-digit * 1-digit or simple 3-digit add
    if random.random() < 0.5:
        a = random.randint(12, 99)
        b = random.randint(2, 9)
        ans = a * b
        question_text = f"{a} * {b} = ?"
    else:
        a = random.randint(100, 500)
        b = random.randint(100, 499)
        ans = a + b
        question_text = f"{a} + {b} = ?"
    options = generate_wrong_options(ans, 20, 1000)
    return question_text, ans, options

def gen_remainder_div():
    a = random.randint(10, 50)
    b = random.randint(2, 9)
    while a % b == 0: a = random.randint(10, 50)
    q = a // b
    r = a % b
    question_text = f"{a} : {b} = ? (qoldiqni toping)"
    ans = f"{q} (qoldiq {r})"
    # fakes
    f1 = f"{q} (qoldiq {r+1 if r+1<b else r-1})"
    f2 = f"{q-1} (qoldiq {b-1})"
    options = [ans, f1, f2]
    return question_text, ans, options

def gen_floors_puzzle():
    # Interval logic
    f1 = 1
    f2 = random.randint(3, 5)
    steps = random.randint(20, 60)
    # steps must be divisible by intervals (f2 - f1)
    intervals = f2 - f1
    steps = (steps // intervals) * intervals
    per_interval = steps // intervals

    target_f = random.randint(6, 10)
    target_intervals = target_f - f1
    ans = target_intervals * per_interval

    question_text = f"Zulmira {f1}-qavatdan {f2}-qavatga chiqish uchun {steps} ta zina bosib o'tdi. {f1}-qavatdan {target_f}-qavatga chiqish uchun nechta zina bosib o'tishi kerak?"
    options = generate_wrong_options(ans, 20, 200)
    return question_text, ans, options

def gen_fractions_intro():
    # a/b + c/b
    den = random.randint(3, 10)
    num1 = random.randint(1, den-2)
    num2 = random.randint(1, den - num1)
    ans_num = num1 + num2
    question_text = f"{num1}/{den} + {num2}/{den} = ?"
    ans = f"{ans_num}/{den}"
    options = [ans, f"{ans_num+1}/{den}", f"{ans_num}/{den+1}"]
    return question_text, ans, options

def gen_diagrams():
    # Text based table reading
    items = ["Olma", "Anor", "Nok"]
    counts = [random.randint(5, 15) for _ in range(3)]
    table_str = "\n".join([f"{i}: {c} kg" for i, c in zip(items, counts)])

    q_type = random.choice(["max", "min", "sum"])
    if q_type == "max":
        idx = counts.index(max(counts))
        question_text = f"Jadvalga qarang:\n{table_str}\n\nEng ko'p meva qaysi?"
        ans = items[idx]
        options = items
    elif q_type == "min":
        idx = counts.index(min(counts))
        question_text = f"Jadvalga qarang:\n{table_str}\n\nEng kam meva qaysi?"
        ans = items[idx]
        options = items
    else:
        question_text = f"Jadvalga qarang:\n{table_str}\n\nJami mevalar necha kg?"
        ans = sum(counts)
        options = generate_wrong_options(ans, 10, 100)

    return question_text, ans, options

def gen_olympiad_analog():
    # Simple logic puzzle
    # Heads and legs (light version) or similar
    rabbits = random.randint(2, 5)
    chickens = random.randint(2, 5)
    heads = rabbits + chickens
    legs = rabbits * 4 + chickens * 2
    question_text = f"Hovlida quyonlar va tovuqlar bor. Ularning boshlari soni {heads} ta, oyoqlari soni {legs} ta. Nechta quyon bor?"
    ans = rabbits
    options = generate_wrong_options(ans, 1, 10)
    return question_text, ans, options

def gen_roman_numerals():
    map_roman = {
        1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X",
        11: "XI", 12: "XII", 15: "XV", 20: "XX", 50: "L", 100: "C"
    }
    n = random.choice(list(map_roman.keys()))
    question_text = f"{n} sonining rim raqamlaridagi ifodasini toping."
    ans = map_roman[n]
    # Generate fake options
    fake_pool = list(map_roman.values())
    if ans in fake_pool: fake_pool.remove(ans)
    fakes = random.sample(fake_pool, 2)
    options = [ans] + fakes
    return question_text, ans, options

def gen_rounding():
    # Round to nearest 10 or 100
    if random.random() < 0.5:
        n = random.randint(10, 99)
        # Round to 10
        rem = n % 10
        if rem < 5: ans = n - rem
        else: ans = n + (10 - rem)
        question_text = f"{n} sonini o'nliklargacha yaxlitlang."
    else:
        n = random.randint(100, 999)
        rem = n % 100
        if rem < 50: ans = n - rem
        else: ans = n + (100 - rem)
        question_text = f"{n} sonini yuzliklargacha yaxlitlang."

    options = [ans, ans+10, ans-10]
    return question_text, ans, options

def gen_time_units():
    # Century, year
    q_type = random.choice(["century", "year"])
    if q_type == "century":
        c = random.randint(1, 21)
        question_text = f"{c}-asr necha yil?"
        ans = c * 100 # Technically "100 years in a century" but usually implies conversion logic?
        # Actually usually "1 asr = 100 yil". Let's do simple conversion.
        question_text = f"{c} asr necha yilga teng?"
        ans = c * 100
    else:
        y = random.randint(2, 5)
        question_text = f"{y} yil necha oy?"
        ans = y * 12

    options = generate_wrong_options(ans, 10, 2500)
    return question_text, ans, options

def gen_triangle_types():
    types = [
        ("Teng tomonli", "Hamma tomonlari teng"),
        ("Teng yonli", "Ikki tomoni teng"),
        ("Turli tomonli", "Hamma tomonlari har xil")
    ]
    t, desc = random.choice(types)
    question_text = f"{desc} uchburchak nima deb ataladi?"
    ans = t
    options = ["Teng tomonli", "Teng yonli", "Turli tomonli"]
    return question_text, ans, options

def gen_mass_calc():
    # Ton to kg
    t = random.randint(1, 10)
    question_text = f"{t} tonna necha kilogramm?"
    ans = t * 1000
    options = [ans, ans/10, ans*10]
    return question_text, ans, options

def gen_length_calc():
    # km to m
    k = random.randint(1, 10)
    m = random.randint(100, 900)
    question_text = f"{k} km {m} m necha metr?"
    ans = k * 1000 + m
    options = generate_wrong_options(ans, 1000, 15000)
    return question_text, ans, options

def gen_volume_liter():
    # Simple liter addition
    l1 = random.randint(10, 100)
    l2 = random.randint(10, 100)
    question_text = f"Idishda {l1} litr suv bor. Unga yana {l2} litr quyildi. Jami qancha bo'ldi?"
    ans = l1 + l2
    options = generate_wrong_options(ans, 10, 300)
    return question_text, ans, options

def gen_three_ops():
    # a * b - c / d ? Too complex integer division issues.
    # a * b + c - d
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    c = random.randint(10, 50)
    d = random.randint(1, 20)
    ans = a * b + c - d
    question_text = f"{a} * {b} + {c} - {d} = ?"
    options = generate_wrong_options(ans, 0, 200)
    return question_text, ans, options

def gen_complex_sequences():
    # Two steps or Fibonacci-like
    if random.random() < 0.5:
        # +a, -b
        start = 10
        step1 = random.randint(3, 5)
        step2 = random.randint(1, 2)
        seq = [start]
        curr = start
        for i in range(3):
            curr += step1
            seq.append(curr)
            curr -= step2
            seq.append(curr)
        # seq e.g. 10, 15, 13, 18, 16, 21, 19
        ans = seq[-1]
        seq_str = ", ".join(map(str, seq[:-1]))
        question_text = f"Ketma-ketlikni davom ettiring: {seq_str}, ... ?"
        options = generate_wrong_options(ans, 0, 100)
    else:
        # Doubling
        start = random.randint(1, 3)
        seq = [start, start*2, start*4, start*8, start*16]
        ans = seq[-1]
        seq_str = ", ".join(map(str, seq[:-1]))
        question_text = f"Ketma-ketlikni davom ettiring: {seq_str}, ... ?"
        options = generate_wrong_options(ans, 0, 100)
    return question_text, ans, options

def gen_two_step_problems():
    names = get_names(2)
    item = get_item()
    n1 = random.randint(10, 50)
    n2 = random.randint(5, 20)
    n3 = random.randint(5, 20)

    question_text = f"{names[0]}da {n1} ta {item} bor. {names[1]}da esa undan {n2} ta ko'p. Ikkalasida jami nechta {item} bor?"
    p2 = n1 + n2
    ans = n1 + p2
    options = generate_wrong_options(ans, 10, 200)
    return question_text, ans, options

def generate_3sinf_topic_questions(topic, count=10):
    questions = []

    generator_map = {
        "Uch xonali sonlar (1-1000)": gen_3_digits_1000,
        "Mantiqiy tenglamalar (Sodda)": gen_logic_equations,
        "Harakatga doir: Tezlik va masofa": gen_speed_distance,
        "Yuzani hisoblash (Kvadrat)": gen_area_square,
        "Ustun shaklida ko'paytirish": gen_column_mult,
        "Qoldiqli bo'lish": gen_remainder_div,
        "Zulmira va qavatlar (Mantiqiy tuzoq)": gen_floors_puzzle,
        "Kasrlar bilan tanishuv": gen_fractions_intro,
        "Diagramma va jadvallar": gen_diagrams,
        "Olimpiada masalalari (Analog)": gen_olympiad_analog,
        "Rim raqamlari": gen_roman_numerals,
        "Yaxlitlash (O'nlik va yuzlikkacha)": gen_rounding,
        "Vaqt birliklari (Asr, yil, oy)": gen_time_units,
        "Geometriya: Uchburchak turlari": gen_triangle_types,
        "Massani hisoblash (kg, t)": gen_mass_calc,
        "Uzunlikni hisoblash (km, m)": gen_length_calc,
        "Hajm birliklari (Litr)": gen_volume_liter,
        "3 ta amal qatnashgan ifodalar": gen_three_ops,
        "Mantiqiy ketma-ketliklar (Murakkab)": gen_complex_sequences,
        "Matnli masalalar (Ikki bosqichli)": gen_two_step_problems
    }

    gen_func = generator_map.get(topic)

    # Fallback
    if not gen_func:
        gen_func = gen_column_mult

    seen = set()
    attempts = 0
    max_attempts = count * 10

    while len(questions) < count and attempts < max_attempts:
        attempts += 1
        try:
            q_text, ans, options = gen_func()
        except Exception as e:
            print(f"Error in {topic}: {e}")
            continue

        if q_text in seen:
            continue
        seen.add(q_text)

        formatted_options, answer_str = format_options(ans, options)

        questions.append({
            "question": q_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "3sinf_analog"
        })

    random.shuffle(questions)
    return questions


# --- 2nd Grade Generators ---

def gen_2_digits_100():
    # Identify digits or composition
    num = random.randint(10, 99)
    if random.random() < 0.5:
        tens = num // 10
        units = num % 10
        question_text = f"{num} sonida nechta o'nlik va nechta birlik bor?"
        ans = f"{tens} o'nlik, {units} birlik"
        # Fake options
        f1 = f"{units} o'nlik, {tens} birlik"
        f2 = f"{tens+1} o'nlik, {units} birlik"
        options = [ans, f1, f2]
    else:
        # Decomposition
        tens = num // 10 * 10
        units = num % 10
        question_text = f"{num} soni qanday yoziladi? (Xona qo'shiluvchilari yig'indisi ko'rinishida)"
        ans = f"{tens} + {units}"
        f1 = f"{tens} + {units+1}"
        f2 = f"{tens-10} + {units}"
        options = [ans, f1, f2]
    return question_text, ans, options

def gen_add_100():
    # a + b <= 100
    a = random.randint(1, 89)
    b = random.randint(1, 100 - a)
    ans = a + b
    question_text = f"{a} + {b} = ?"
    options = generate_wrong_options(ans, 1, 100)
    return question_text, ans, options

def gen_sub_100():
    # a - b >= 0
    a = random.randint(10, 100)
    b = random.randint(1, a)
    ans = a - b
    question_text = f"{a} - {b} = ?"
    options = generate_wrong_options(ans, 0, 100)
    return question_text, ans, options

def gen_mult_table():
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    ans = a * b
    question_text = f"{a} * {b} = ?"
    options = generate_wrong_options(ans, 4, 81)
    return question_text, ans, options

def gen_div_basics():
    # Exact division
    b = random.randint(2, 9)
    ans = random.randint(2, 9)
    a = b * ans
    question_text = f"{a} : {b} = ?"
    options = generate_wrong_options(ans, 1, 9)
    return question_text, ans, options

def gen_sequences_2sinf():
    step = random.randint(2, 5)
    start = random.randint(1, 20)
    seq = [start + i*step for i in range(4)]
    ans = seq[3]
    question_text = f"Ketma-ketlikni davom ettiring: {seq[0]}, {seq[1]}, {seq[2]}, ... ?"
    options = [ans, ans+step, ans-step]
    return question_text, ans, options

def gen_perimeter():
    if random.random() < 0.5:
        # Square
        a = random.randint(1, 10)
        ans = 4 * a
        question_text = f"Kvadratning tomoni {a} sm. Uning perimetrini toping."
    else:
        # Rectangle
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        while a == b: b = random.randint(1, 10)
        ans = 2 * (a + b)
        question_text = f"To'g'ri to'rtburchakning tomonlari {a} sm va {b} sm. Perimetrini toping."

    options = generate_wrong_options(ans, 4, 100)
    return question_text, ans, options

def gen_time_clock():
    h = random.randint(1, 12)
    m = random.choice([0, 15, 30, 45])

    if m == 0:
        time_str = f"{h}:00"
        ans = f"Soat {h} bo'ldi"
    elif m == 30:
        time_str = f"{h}:30"
        ans = f"{h} yarim"
    else:
        time_str = f"{h}:{m}"
        ans = f"{h} dan {m} minut o'tdi"

    question_text = f"Soatdagi vaqtni toping: {time_str}"
    # Fakes are hard to generate generically for text, so randomizing logic
    f1 = f"{h+1}:00"
    f2 = f"{h-1}:30"
    options = [ans, f1, f2]
    return question_text, ans, options

def gen_weight_kg():
    # Simple addition of weights
    w1 = random.randint(1, 50)
    w2 = random.randint(1, 50)
    ans = w1 + w2
    item1 = get_item()
    item2 = get_item()
    question_text = f"{item1} {w1} kg, {item2} {w2} kg. Ikkolasi birgalikda qancha?"
    options = generate_wrong_options(ans, 2, 100)
    return question_text, ans, options

def gen_order_ops():
    # a + (b - c) or a - (b + c)
    if random.random() < 0.5:
        a = random.randint(10, 50)
        b = random.randint(10, 20)
        c = random.randint(1, 9)
        # a + (b - c)
        ans = a + (b - c)
        question_text = f"{a} + ({b} - {c}) = ?"
    else:
        a = random.randint(30, 80)
        b = random.randint(1, 10)
        c = random.randint(1, 10)
        # a - (b + c)
        ans = a - (b + c)
        question_text = f"{a} - ({b} + {c}) = ?"

    options = generate_wrong_options(ans, 0, 100)
    return question_text, ans, options

def gen_compare_2sinf():
    a = random.randint(10, 99)
    b = random.randint(10, 99)
    while a == b: b = random.randint(10, 99)
    question_text = f"{a} ... {b}. Qaysi belgi qo'yiladi?"
    if a > b: ans = ">"
    elif a < b: ans = "<"
    else: ans = "="
    options = [">", "<", "="]
    return question_text, ans, options

def gen_money_uzs():
    prices = [100, 200, 500, 1000]
    p = random.choice(prices)
    count = random.randint(2, 5)
    total = p * count
    item = get_item()
    question_text = f"Bitta {item} {p} so'm turadi. {count} ta {item} qancha turadi?"
    ans = total
    options = generate_wrong_options(ans, 200, 5000)
    return question_text, ans, options

def gen_length_measure():
    # conversion dm -> sm or m -> dm
    if random.random() < 0.5:
        dm = random.randint(1, 9)
        ans = dm * 10
        question_text = f"{dm} dm necha sm?"
    else:
        m = random.randint(1, 9)
        ans = m * 10
        question_text = f"{m} m necha dm?"
    options = generate_wrong_options(ans, 10, 100)
    return question_text, ans, options

def gen_geo_properties():
    shapes = [
        ("Uchburchak", 3), ("Kvadrat", 4), ("To'g'ri to'rtburchak", 4), ("Beshburchak", 5), ("Oltiburchak", 6)
    ]
    s, v = random.choice(shapes)
    question_text = f"{s}ning nechta uchi bor?"
    ans = v
    # Select correct answer and 2 distinct wrong answers
    all_opts = {3, 4, 5, 6}
    if v in all_opts:
        all_opts.remove(v)
    wrong = random.sample(list(all_opts), 2)
    options = [ans] + wrong
    return question_text, ans, options

def gen_even_odd_100():
    n = random.randint(10, 99)
    question_text = f"{n} soni juftmi yoki toqmi?"
    ans = "Juft" if n % 2 == 0 else "Toq"
    options = ["Juft", "Toq"]
    return question_text, ans, options

def gen_equations_simple():
    # x + a = b
    a = random.randint(1, 50)
    b = random.randint(a + 1, 99)
    x = b - a
    question_text = f"Tenglamani yeching: x + {a} = {b}"
    ans = x
    options = generate_wrong_options(ans, 1, 99)
    return question_text, ans, options

def gen_logic_age():
    names = get_names(2)
    age1 = random.randint(7, 12)
    diff = random.randint(2, 5)
    age2 = age1 + diff
    question_text = f"{names[0]} {age1} yoshda. {names[1]} undan {diff} yosh katta. {names[1]} necha yoshda?"
    ans = age2
    options = generate_wrong_options(ans, 5, 20)
    return question_text, ans, options

def gen_fractions_simple():
    # Concept of half and quarter
    if random.random() < 0.5:
        question_text = "Butunning yarmi qanday yoziladi?"
        ans = "1/2"
        options = ["1/2", "1/4", "1/3"]
    else:
        question_text = "Butunning choragi (to'rtdan biri) qanday yoziladi?"
        ans = "1/4"
        options = ["1/2", "1/4", "3/4"]
    return question_text, ans, options

def gen_mult_div_word():
    # Simple word problems
    if random.random() < 0.5:
        # Mult
        per_box = random.randint(2, 10)
        boxes = random.randint(2, 5)
        item = get_item()
        question_text = f"Har bir qutida {per_box} tadan {item} bor. {boxes} ta qutida jami nechta {item} bor?"
        ans = per_box * boxes
    else:
        # Div
        total = random.randint(4, 20)
        kids = random.randint(2, 5)
        # Ensure divisibility
        total = total - (total % kids)
        if total == 0: total = kids * 2

        question_text = f"{total} ta konfetni {kids} nafar bolaga teng bo'lib berilsa, har biriga nechtadan tegadi?"
        ans = total // kids

    options = generate_wrong_options(ans, 1, 100)
    return question_text, ans, options

def gen_mixed_ops():
    # a * b + c or a * b - c
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    c = random.randint(1, 20)
    if random.random() < 0.5:
        ans = a * b + c
        question_text = f"{a} * {b} + {c} = ?"
    else:
        # ensure positive
        prod = a * b
        if c > prod: c = prod - 1
        ans = prod - c
        question_text = f"{a} * {b} - {c} = ?"

    options = generate_wrong_options(ans, 0, 100)
    return question_text, ans, options

def generate_2sinf_topic_questions(topic, count=10):
    questions = []

    generator_map = {
        "Ikki xonali sonlar (1-100)": gen_2_digits_100,
        "Yuzlik ichida qo'shish (Analog)": gen_add_100,
        "Yuzlik ichida ayirish (Analog)": gen_sub_100,
        "Ko'paytirish jadvali (Dinamik)": gen_mult_table,
        "Bo'lish asoslari (Mantiqiy)": gen_div_basics,
        "Sonli ketma-ketliklar": gen_sequences_2sinf,
        "Perimetr hisoblash (To'rtburchak)": gen_perimeter,
        "Vaqt: Soat va minutlar": gen_time_clock,
        "Og'irlik: kg va gramm": gen_weight_kg,
        "Qavsli amallar tartibi": gen_order_ops,
        "Taqqoslash (Katta, kichik, teng)": gen_compare_2sinf,
        "Pul birliklari (So'm)": gen_money_uzs,
        "Uzunlik o'lchovlari (sm, dm, m)": gen_length_measure,
        "Geometrik shakllar xossalari": gen_geo_properties,
        "Juft va toq sonlar (100 gacha)": gen_even_odd_100,
        "Tenglamalar (Noma'lum qo'shiluvchini topish)": gen_equations_simple,
        "Mantiqiy masalalar (Yoshga doir)": gen_logic_age,
        "Kasr tushunchasi (Yarim, chorak)": gen_fractions_simple,
        "Ko'paytirish va bo'lish (Matnli)": gen_mult_div_word,
        "Murakkab ifodalar": gen_mixed_ops
    }

    gen_func = generator_map.get(topic)

    # Fallback to general 2nd grade mix if specific topic not found
    if not gen_func:
        # Default fallback
        gen_func = gen_add_100

    seen = set()
    attempts = 0
    max_attempts = count * 10

    while len(questions) < count and attempts < max_attempts:
        attempts += 1
        try:
            q_text, ans, options = gen_func()
        except Exception as e:
            print(f"Error in {topic}: {e}")
            continue

        if q_text in seen:
            continue
        seen.add(q_text)

        formatted_options, answer_str = format_options(ans, options)

        questions.append({
            "question": q_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "2sinf_analog"
        })

    random.shuffle(questions)
    return questions


# --- 2nd & 3rd Grade + Mukammal Generators ---

def generate_2sinf_jadvalli(count=10):
    questions = []
    seen = set()
    attempts = 0
    max_attempts = count * 10

    while len(questions) < count and attempts < max_attempts:
        attempts += 1
        n1 = random.randint(2, 9)
        n2 = random.randint(2, 9)
        question_text = f"{n1} x {n2} = ?"

        if question_text in seen:
            continue
        seen.add(question_text)

        ans = n1 * n2
        options = generate_wrong_options(ans, 4, 81, 2)
        formatted_options, answer_str = format_options(ans, options)
        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "2sinf_jadvalli"
        })
    random.shuffle(questions)
    return questions

def generate_2sinf_onliklar(count=10):
    questions = []
    seen = set()
    attempts = 0
    max_attempts = count * 10

    while len(questions) < count and attempts < max_attempts:
        attempts += 1
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

        if question_text in seen:
            continue
        seen.add(question_text)

        options = generate_wrong_options(ans, 10, 100, 2)
        formatted_options, answer_str = format_options(ans, options)
        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "2sinf_onliklar"
        })
    random.shuffle(questions)
    return questions

def generate_2sinf_matnli(count=10):
    questions = []
    seen = set()
    attempts = 0
    max_attempts = count * 10

    while len(questions) < count and attempts < max_attempts:
        attempts += 1
        names = get_names(2)
        q_type = random.choice(['fabric', 'logic', 'money', 'time'])

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

        elif q_type == 'logic':
             age1 = random.randint(7, 15)
             diff = random.randint(2, 5)
             age2 = age1 + diff
             question_text = f"{names[0]} {age1} yoshda. {names[1]} undan {diff} yosh katta. {names[1]} necha yoshda?"
             ans = age2

        elif q_type == 'money':
            total_money = random.choice([50, 100, 200, 500, 1000])
            price = random.randint(1, total_money // 10) * 10
            question_text = f"{names[0]}da {total_money} so'm bor edi. U {price} so'mga muzqaymoq oldi. Qancha puli qoldi?"
            ans = total_money - price

        else: # time
            start_hour = random.randint(8, 18)
            duration = random.randint(1, 4)
            end_hour = start_hour + duration
            question_text = f"Dars soat {start_hour}:00 da boshlandi va {duration} soat davom etdi. Dars soat nechida tugadi?"
            ans = end_hour

        if question_text in seen:
            continue
        seen.add(question_text)

        options = generate_wrong_options(ans, 1, 2000 if q_type=='money' else 100, 2)
        formatted_options, answer_str = format_options(ans, options)

        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "2sinf_matnli"
        })
    random.shuffle(questions)
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
    seen = set()
    attempts = 0
    max_attempts = count * 10

    while len(questions) < count and attempts < max_attempts:
        attempts += 1
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

        if question_text in seen:
            continue
        seen.add(question_text)

        options = generate_wrong_options(ans, 0, 500, 2)
        formatted_options, answer_str = format_options(ans, options)

        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "mukammal"
        })
    random.shuffle(questions)
    return questions

def generate_olympiad_questions(count=10):
    questions = []
    seen = set()
    attempts = 0
    max_attempts = count * 10

    while len(questions) < count and attempts < max_attempts:
        attempts += 1
        q_type = random.choice(['logic', 'chain', 'heads_legs'])

        if q_type == 'logic':
            names = get_names(2)
            n1 = random.randint(20, 50)
            n2 = random.randint(20, 50)
            question_text = f"{names[0]}da {n1} ta, {names[1]}da {n2} ta olma bor. {names[0]}da {names[1]}ga qaraganda nechta ko'p yoki kam olma bor (farqi)?"
            ans = abs(n1 - n2)

        elif q_type == 'chain':
            start = random.randint(1, 20)
            step = random.randint(2, 9)
            seq = [start + i*step for i in range(5)]
            missing_idx = random.randint(1, 4)
            ans = seq[missing_idx]
            seq[missing_idx] = "?"
            question_text = f"Sonli zanjirni davom ettiring: {', '.join(map(str, seq))}"

        else: # heads_legs
            rabbits = random.randint(1, 5)
            chickens = random.randint(1, 10)
            heads = rabbits + chickens
            legs = (rabbits * 4) + (chickens * 2)
            question_text = f"Hovlida tovuqlar va quyonlar yuribdi. Ularning jami boshlari soni {heads} ta, oyoqlari soni {legs} ta. Nechta quyon bor?"
            ans = rabbits

        if question_text in seen:
            continue
        seen.add(question_text)

        options = generate_wrong_options(ans, 0, 100, 2)
        formatted_options, answer_str = format_options(ans, options)

        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "olympiad"
        })
    random.shuffle(questions)
    return questions


# --- Mukammal Matematika Generators ---

def gen_logic_add_sub():
    # Type 1: Consecutive numbers sum
    if random.random() < 0.33:
        n = random.randint(10, 50)
        # Sum of 3 consecutive integers = 3*x
        total = 3 * n
        question_text = f"Uchta ketma-ket kelgan natural sonlarning yig'indisi {total} ga teng. Bu sonlarning eng kichigini toping."
        ans = n - 1
        options = [n-1, n, n+1]
    # Type 2: Balance logic
    elif random.random() < 0.66:
        val = random.randint(20, 100)
        diff = random.randint(5, 15)
        # A + diff = val, B - diff = val
        # A = val - diff, B = val + diff
        question_text = f"A soniga {diff} ni qo'shsak {val} bo'ladi. B sonidan {diff} ni ayirsak ham {val} bo'ladi. Qaysi son katta: A yoki B?"
        ans = "B"
        options = ["A", "B", "Ikkisi teng"]
    # Type 3: Missing digit (simplified as find X)
    else:
        # X + Y = Z
        x = random.randint(10, 50)
        y = random.randint(10, 50)
        z = x + y
        # Hide one
        question_text = f"O'ylangan songa {y} ni qo'shib, yig'indidan {x} ni ayirsak, natija 20 bo'ldi. O'ylangan sonni toping."
        # (N + y) - x = 20 => N = 20 + x - y
        ans = 20 + x - y
        options = generate_wrong_options(ans, 0, 100)

    return question_text, ans, options

def gen_logic_mult_div():
    # Type 1: X * A / B = C
    if random.random() < 0.5:
        a = random.randint(2, 5)
        b = random.randint(2, 5)
        c = random.randint(10, 50)
        # X * a / b = c => X = c * b / a
        # Ensure integer
        while (c * b) % a != 0:
            c = random.randint(10, 50)
        ans = (c * b) // a
        question_text = f"O'ylangan sonni {a} ga ko'paytirib, {b} ga bo'lsak, {c} hosil bo'ldi. O'ylangan sonni toping."
        options = generate_wrong_options(ans, 1, 100)
    # Type 2: Factor logic
    else:
        # Product of two numbers is P. One is A. If A is increased by 2... too complex?
        # A * B = P.
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        p = a * b
        question_text = f"Ikki sonning ko'paytmasi {p} ga teng. Agar birinchi ko'paytuvchi {a} ga teng bo'lsa, ikkinchi ko'paytuvchini toping."
        ans = b
        options = generate_wrong_options(ans, 1, 20)
    return question_text, ans, options

def gen_complex_four_ops():
    # (A + B) * C - D
    a = random.randint(2, 20)
    b = random.randint(2, 20)
    c = random.randint(2, 5)
    d = random.randint(1, 50)
    ans = (a + b) * c - d
    question_text = f"Ifodaning qiymatini toping: ({a} + {b}) * {c} - {d} = ?"
    options = generate_wrong_options(ans, 0, 200)
    return question_text, ans, options

def gen_place_value_logic():
    # Type 1: How many tens
    if random.random() < 0.5:
        n = random.randint(100, 999)
        question_text = f"{n} sonida nechta o'nlik bor? (Diqqat: jami o'nliklar soni so'ralmoqda, xona birligi emas)"
        ans = n // 10
        options = [n // 10, (n % 100) // 10, n // 100]
    # Type 2: Swap digits
    else:
        digits = random.sample(range(1, 10), 3)
        n = digits[0]*100 + digits[1]*10 + digits[2]
        swapped = digits[2]*100 + digits[1]*10 + digits[0]
        question_text = f"{n} sonining yuzlar va birlar xonasidagi raqamlari o'rnini almashtirsak, hosil bo'lgan son qanchaga o'zgaradi?"
        ans = abs(n - swapped)
        options = generate_wrong_options(ans, 0, 1000)
    return question_text, ans, options

def gen_compare_large_numbers():
    # Compare expressions
    a = random.randint(1000, 5000)
    b = random.randint(100, 999)
    res1 = a + b

    c = random.randint(1000, 5000)
    d = random.randint(100, 999)
    res2 = c + d

    question_text = f"Taqqislang: {a} + {b} ... {c} + {d}"
    if res1 > res2: ans = ">"
    elif res1 < res2: ans = "<"
    else: ans = "="
    options = [">", "<", "="]
    return question_text, ans, options

def gen_rounding_logic():
    targets = [100, 200, 300, 400, 500]
    t = random.choice(targets)

    # Generate 3 numbers, one rounds to t
    # Range for rounding to t (nearest 100): t-50 to t+49
    correct = random.randint(t - 49, t + 49)

    # Wrongs
    w1 = random.randint(t + 51, t + 140)
    w2 = random.randint(t - 150, t - 51)

    cands = [correct, w1, w2]
    random.shuffle(cands)

    question_text = f"Qaysi son yuzliklargacha yaxlitlanganda {t} ga teng bo'ladi?"
    ans = correct
    options = cands
    return question_text, ans, options

def gen_geometry_lines():
    # Type 1: Definitions
    if random.random() < 0.5:
        definitions = [
            ("To'g'ri chiziq", "Boshi ham, oxiri ham yo'q"),
            ("Nur", "Boshi bor, lekin oxiri yo'q"),
            ("Kesma", "Boshi ham, oxiri ham bor")
        ]
        ans_name, ans_desc = random.choice(definitions)
        question_text = f"Geometrik shakl ta'rifi: {ans_desc}. Bu nima?"
        ans = ans_name
        options = ["To'g'ri chiziq", "Nur", "Kesma"]
    # Type 2: Counting segments on a line with points
    else:
        n_points = random.randint(3, 5) # A, B, C, D...
        # Number of segments from n collinear points is n*(n-1)/2
        ans = (n_points * (n_points - 1)) // 2
        question_text = f"To'g'ri chiziqda {n_points} ta nuqta belgilandi. Bu nuqtalar yordamida jami nechta kesma hosil bo'ladi?"
        options = generate_wrong_options(ans, 1, 20)
    return question_text, ans, options

def gen_polyline_length():
    segments = random.randint(3, 5)
    lengths = [random.randint(2, 10) for _ in range(segments)]
    total = sum(lengths)
    lengths_str = ", ".join(map(str, lengths))
    question_text = f"Siniq chiziq {segments} ta kesmadan iborat. Ularning uzunliklari: {lengths_str} (sm). Siniq chiziqning umumiy uzunligini toping."
    ans = total
    options = generate_wrong_options(ans, 5, 100)
    return question_text, ans, options

def gen_polygon_perimeter():
    # Regular or irregular
    if random.random() < 0.5:
        # Regular
        sides = random.randint(5, 8)
        side_len = random.randint(3, 10)
        ans = sides * side_len
        shape_names = {5: "Beshburchak", 6: "Oltiburchak", 7: "Yettiburchak", 8: "Sakkizburchak"}
        name = shape_names.get(sides, f"{sides}-burchak")
        question_text = f"Muntazam {name}ning tomoni {side_len} sm. Uning perimetrini toping."
    else:
        # Triangle or Quad with mixed sides
        sides = [random.randint(5, 15) for _ in range(4)]
        ans = sum(sides)
        s_str = ", ".join(map(str, sides))
        question_text = f"To'rtburchakning tomonlari {s_str} sm. Uning perimetrini toping."

    options = generate_wrong_options(ans, 10, 200)
    return question_text, ans, options

def gen_rect_square_complex():
    # Type 1: Given Perimeter, find side (Square)
    if random.random() < 0.33:
        a = random.randint(5, 20)
        p = 4 * a
        question_text = f"Kvadratning perimetri {p} sm ga teng. Uning tomonini toping."
        ans = a
        options = generate_wrong_options(ans, 1, 50)
    # Type 2: Given Area, find side (Square)
    elif random.random() < 0.66:
        a = random.randint(4, 12)
        area = a * a
        question_text = f"Kvadratning yuzi {area} kv. sm. Uning perimetrini toping."
        ans = 4 * a
        options = generate_wrong_options(ans, 10, 100)
    # Type 3: Rect perimeter and one side, find area
    else:
        a = random.randint(5, 15)
        b = random.randint(5, 15)
        p = 2 * (a + b)
        question_text = f"To'g'ri to'rtburchakning perimetri {p} sm, bir tomoni esa {a} sm. Uning yuzini toping."
        ans = a * b
        options = generate_wrong_options(ans, 10, 300)
    return question_text, ans, options

def gen_time_leap_year():
    # Type 1: Leap year check
    if random.random() < 0.5:
        base_year = random.choice([2000, 2004, 2008, 2012, 2016, 2020, 2024])
        # Generate options: one leap, others not
        # Or asking "Which year is leap?"
        cands = []
        # Add one leap year
        leap = base_year + random.choice([-4, 0, 4, 8])
        cands.append(leap)
        # Add non-leap years
        while len(cands) < 3:
            y = leap + random.randint(1, 3)
            if y % 4 != 0:
                cands.append(y)

        random.shuffle(cands)
        question_text = f"Quyidagi yillardan qaysi biri kabisa yili (366 kun)?"
        ans = leap
        options = cands
    # Type 2: Time calculation
    else:
        # 1 asr = 100 yil, 1 yil = 12 oy...
        # "2 sutka necha soat?"
        d = random.randint(2, 5)
        ans = d * 24
        question_text = f"{d} sutka necha soatga teng?"
        options = generate_wrong_options(ans, 24, 200)
    return question_text, ans, options

def gen_river_motion():
    # V_down = V_boat + V_stream
    # V_up = V_boat - V_stream
    v_boat = random.randint(15, 30)
    v_stream = random.randint(2, 5)

    if random.random() < 0.5:
        # Downstream
        question_text = f"Katerning turg'un suvdagi tezligi {v_boat} km/soat, daryo oqimining tezligi {v_stream} km/soat. Katerning oqim bo'ylab tezligini toping."
        ans = v_boat + v_stream
        options = [v_boat + v_stream, v_boat - v_stream, v_boat]
    else:
        # Upstream
        question_text = f"Katerning turg'un suvdagi tezligi {v_boat} km/soat, daryo oqimining tezligi {v_stream} km/soat. Katerning oqimga qarshi tezligini toping."
        ans = v_boat - v_stream
        options = [v_boat + v_stream, v_boat - v_stream, v_boat]
    return question_text, ans, options

def gen_logic_algorithms():
    # Sequence or simple algorithm
    # Type 1: If-Then logic
    if random.random() < 0.5:
        # A > B, B > C -> A ? C
        names = get_names(3)
        question_text = f"{names[0]} {names[1]}dan baland. {names[1]} {names[2]}dan baland. Eng baland kim?"
        ans = names[0]
        options = names
    # Type 2: Simple alg step
    else:
        # Input -> +3 -> *2 -> Output. Find Output given Input.
        inp = random.randint(1, 10)
        add = random.randint(1, 5)
        mult = random.randint(2, 4)
        out = (inp + add) * mult
        question_text = f"Algoritm bajarilishini hisoblang: Kirish soni {inp}. 1-qadam: {add} ni qo'shish. 2-qadam: Natijani {mult} ga ko'paytirish. Chiqish soni necha?"
        ans = out
        options = generate_wrong_options(ans, 1, 100)
    return question_text, ans, options

def gen_logic_traps():
    # Logic 1: Candles
    if random.random() < 0.5:
        n = random.randint(5, 15)
        m = random.randint(2, n - 1)
        question_text = f"Xonada {n} ta sham yonib turgan edi. {m} tasi o'chirildi, qolganlari esa oxirigacha yonib tugadi. Xonada nechta sham qoldi?"
        ans = m
        options = [m, n, n - m]
    # Logic 2: Sticks/Cuts
    else:
        pieces = random.randint(3, 10)
        cuts = pieces - 1
        question_text = f"Uzun taxtani {pieces} bo'lakka bo'lish uchun uni necha joyidan arralash kerak?"
        ans = cuts
        options = [cuts, pieces, pieces + 1]

    return question_text, ans, options

def gen_reverse_method():
    # ((x + a) * b) - c = d  -> Reverse: (d + c) / b - a = x
    x = random.randint(1, 20)
    a = random.randint(1, 20)
    b = random.randint(2, 5)
    c = random.randint(1, 20)

    d = ((x + a) * b) - c

    question_text = f"Men bir son o'yladim. Unga {a} ni qo'shdim, hosil bo'lgan sonni {b} ga ko'paytirdim va {c} ni ayirdim. Natijada {d} chiqdi. Men qanday son o'yladim?"
    ans = x
    options = generate_wrong_options(ans, 1, 50)
    return question_text, ans, options

def gen_venn_diagram():
    # Sets: A, B, Both
    both = random.randint(2, 10)
    only_a = random.randint(5, 15)
    only_b = random.randint(5, 15)

    total_a = only_a + both
    total_b = only_b + both
    total = only_a + only_b + both

    subjects_pool = [
        ("shaxmat", "shashka", "o'ynaydi"),
        ("futbol", "voleybol", "o'ynaydi"),
        ("ingliz tili", "rus tili", "biladi"),
        ("suzish", "yugurish", "bilan shug'ullanadi"),
        ("matematika", "fizika", "fani to'garagiga qatnashadi")
    ]
    s1, s2, verb = random.choice(subjects_pool)

    # Adjust verb grammar if needed (simple suffix logic or just string formatting)
    # The verb usually goes at the end.
    # "20 nafari shaxmatni, 15 nafari shashkani o'ynaydi."
    # "20 nafari ingliz tilini, 15 nafari rus tilini biladi."

    # Need correct accusative suffixes (-ni).
    # Simple heuristic: add 'ni' if ends in vowel, 'ni' otherwise (uzbek cases are complex).
    # To be safe, manual suffixes in tuple? Or just assume '-ni' works generally or omit object marker if ambiguous.
    # "Sinfdagi o'quvchilarning {total_a} nafari {s1}, {total_b} nafari {s2} {verb}."
    # Let's fix suffixes manually for best quality.

    if s1.endswith(('a', 'i', 'o', 'u', 'e', 'o\'')):
        s1_acc = s1 + "ni"
    else:
        s1_acc = s1 + "ni" # Generally -ni works, sometimes -ni after consonant too.

    if s2.endswith(('a', 'i', 'o', 'u', 'e', 'o\'')):
        s2_acc = s2 + "ni"
    else:
        s2_acc = s2 + "ni"

    q_type = random.choice(['only_one', 'total', 'both'])

    base_text = f"Sinfdagi o'quvchilarning {total_a} nafari {s1_acc}, {total_b} nafari {s2_acc} {verb}. {both} nafari esa ikkalasini ham {verb}."

    if q_type == 'only_one':
        question_text = f"{base_text} Nechta o'quvchi faqat {s1_acc} {verb}?"
        ans = only_a
    elif q_type == 'total':
        question_text = f"{base_text} Sinfda jami nechta o'quvchi bor (agar hamma hech bo'lmasa bitta o'yin o'ynasa)?"
        ans = total
    else:
        # Given total, find both (variation)
        question_text = f"Sinfda {total} nafar o'quvchi bor. {total_a} kishi {s1_acc}, {total_b} kishi {s2_acc} {verb}. Nechta kishi ikkalasini ham {verb}?"
        ans = both

    options = generate_wrong_options(ans, 1, 50)
    return question_text, ans, options

def gen_train_tunnel():
    # L_train + L_tunnel = v * t
    v = random.randint(10, 30) # m/s
    t = random.randint(20, 60) # seconds
    total_dist = v * t

    l_train = random.randint(100, 400)
    l_tunnel = total_dist - l_train

    # Ensure tunnel length is positive and reasonable
    while l_tunnel < 100:
        v = random.randint(15, 25)
        t = random.randint(30, 80)
        total_dist = v * t
        l_train = random.randint(100, 300)
        l_tunnel = total_dist - l_train

    if random.random() < 0.5:
        # Find time
        question_text = f"Uzunligi {l_train} metr bo'lgan poezd uzunligi {l_tunnel} metr bo'lgan tunneldan {v} m/s tezlik bilan o'tmoqda. Poezd tunneldan to'liq chiqib ketishi uchun qancha vaqt ketadi?"
        ans = t
    else:
        # Find train length
        question_text = f"Uzunligi {l_tunnel} metr bo'lgan tunneldan {v} m/s tezlikda harakatlanayotgan poezd {t} sekundda to'liq o'tib bo'ldi. Poezdning uzunligini toping."
        ans = l_train

    options = generate_wrong_options(ans, 10, 1000)
    return question_text, ans, options

def gen_work_efficiency():
    # Pairs (t1, t2) where result is integer
    pairs = [
        (3, 6, 2), (6, 12, 4), (10, 15, 6), (12, 24, 8),
        (20, 30, 12), (10, 40, 8), (4, 12, 3), (6, 3, 2), # Reverse order
        (5, 20, 4), (12, 4, 3)
    ]
    t1, t2, res = random.choice(pairs)
    names = get_names(2)

    question_text = f"{names[0]} bir ishni {t1} soatda, {names[1]} esa shu ishni {t2} soatda bajaradi. Agar ular birgalikda ishlasalar, ishni necha soatda tugatadilar?"
    ans = res
    options = generate_wrong_options(ans, 1, 50)
    return question_text, ans, options

def gen_combinatorics():
    n = random.randint(3, 10)
    ans = (n * (n - 1)) // 2
    question_text = f"{n} nafar do'st uchrashganda hamma bir-biri bilan qo'l berib ko'rishdi. Jami qo'l berib ko'rishishlar soni nechta bo'lgan?"
    options = generate_wrong_options(ans, 1, 100)
    return question_text, ans, options

def gen_cube_surfaces():
    n = random.randint(3, 6)
    q_type = random.choice(['3_face', '2_face', '1_face', '0_face'])

    base_text = f"Kubning sirti qizil rangga bo'yaldi va u {n}x{n}x{n} o'lchamdagi kichik kubchalarga bo'lindi."

    if q_type == '3_face':
        question_text = f"{base_text} Nechta kichik kubchaning 3 ta tomoni bo'yalgan?"
        ans = 8
    elif q_type == '2_face':
        question_text = f"{base_text} Nechta kichik kubchaning 2 ta tomoni bo'yalgan?"
        ans = 12 * (n - 2)
    elif q_type == '1_face':
        question_text = f"{base_text} Nechta kichik kubchaning 1 ta tomoni bo'yalgan?"
        ans = 6 * ((n - 2) ** 2)
    else:
        question_text = f"{base_text} Nechta kichik kubchaning hech qaysi tomoni bo'yalmagan?"
        ans = (n - 2) ** 3

    options = generate_wrong_options(ans, 0, 216)
    if ans == 8: # Fix options for constant answer
        options = [8, 12, 6]

    return question_text, ans, options

def gen_roman_logic():
    map_roman = {
        1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X",
        11: "XI", 12: "XII", 13: "XIII", 14: "XIV", 15: "XV", 16: "XVI", 17: "XVII", 18: "XVIII", 19: "XIX", 20: "XX",
        30: "XXX", 40: "XL", 50: "L", 60: "LX", 100: "C"
    }
    # Operations: + or -
    keys = list(map_roman.keys())
    valid_pairs = []

    # Precompute valid pairs to avoid loops
    for k1 in keys:
        for k2 in keys:
            if k1 + k2 in map_roman:
                valid_pairs.append((k1, k2, '+'))
            if k1 - k2 in map_roman:
                valid_pairs.append((k1, k2, '-'))

    n1, n2, op = random.choice(valid_pairs)

    if op == '+':
        res = n1 + n2
        question_text = f"{map_roman[n1]} + {map_roman[n2]} = ?"
    else:
        res = n1 - n2
        question_text = f"{map_roman[n1]} - {map_roman[n2]} = ?"

    ans = map_roman[res]

    # Fake options
    fakes = []
    attempts = 0
    while len(fakes) < 2 and attempts < 20:
        attempts += 1
        fake_val = res + random.choice([-1, 1, -2, 2, -5, 5])
        if fake_val in map_roman and map_roman[fake_val] != ans and map_roman[fake_val] not in fakes:
            fakes.append(map_roman[fake_val])

    # Fallback fakes
    if len(fakes) < 2:
        fakes = ["II", "V"] # Generic fallback

    options = [ans] + fakes
    return question_text, ans, options

def gen_floors_intervals_mukammal():
    f_start = 1
    f_mid = random.randint(3, 5)

    intervals_mid = f_mid - f_start
    steps_per_interval = random.randint(10, 20)
    steps_mid = intervals_mid * steps_per_interval

    f_target = random.randint(6, 12)
    intervals_target = f_target - f_start
    ans = intervals_target * steps_per_interval

    name = random.choice(["Zulmira", "Malika", "Anvar", "Sardor"])
    question_text = f"{name} {f_start}-qavatdan {f_mid}-qavatga chiqish uchun {steps_mid} ta zina bosib o'tdi. U {f_start}-qavatdan {f_target}-qavatga chiqish uchun nechta zina bosib o'tishi kerak?"

    # Common trap: calculate based on floors directly (steps_mid / f_mid * f_target)
    trap = (steps_mid // f_mid) * f_target
    options = [ans, trap, ans + steps_per_interval]

    return question_text, ans, options

def gen_number_secrets():
    # Digits
    digits = random.sample(range(1, 10), 3) # No 0 to keep it simple for 3-digit
    digits_sorted = sorted(digits)

    min_num = int("".join(map(str, digits_sorted)))
    max_num = int("".join(map(str, digits_sorted[::-1])))

    q_type = random.choice(['max', 'min', 'sum'])

    digits_str = ", ".join(map(str, digits))

    if q_type == 'max':
        question_text = f"Quyidagi raqamlardan foydalanib yozish mumkin bo'lgan eng katta 3 xonali sonni toping: {digits_str}"
        ans = max_num
    elif q_type == 'min':
        question_text = f"Quyidagi raqamlardan foydalanib yozish mumkin bo'lgan eng kichik 3 xonali sonni toping: {digits_str}"
        ans = min_num
    else:
        question_text = f"Quyidagi raqamlardan tuzilgan eng katta va eng kichik 3 xonali sonlar yig'indisini toping: {digits_str}"
        ans = max_num + min_num

    options = generate_wrong_options(ans, 100, 2000)
    return question_text, ans, options

def generate_mukammal_topic_questions(topic, count=10):
    questions = []

    generator_map = {
        "1. Qo‘shish va ayirishga doir mantiqiy masalalar": gen_logic_add_sub,
        "2. Ko‘paytirish va bo‘lishga doir mantiqiy masalalar": gen_logic_mult_div,
        "3. To‘rt amalga doir murakkab masalalar": gen_complex_four_ops,
        "4. Raqamlar va natural sonlar siri": gen_number_secrets,
        "5. Xona birliklari va razryadlar mantiqi": gen_place_value_logic,
        "6. Ko‘p xonali sonlarni taqqoslash (Mantiqiy)": gen_compare_large_numbers,
        "7. Natural sonlarni yaxlitlash mantiqi": gen_rounding_logic,
        "8. Rim raqamlari (Gugurt cho'pi jumboqlari)": gen_roman_logic,
        "9. Geometriya: To‘g‘ri chiziq, nur va kesma": gen_geometry_lines,
        "10. Siniq chiziq va uning uzunligi": gen_polyline_length,
        "11. Ko‘pburchaklar va ularning perimetri": gen_polygon_perimeter,
        "12. To‘g‘ri to‘rtburchak va kvadrat (Murakkab)": gen_rect_square_complex,
        "13. Vaqt va vaqt birliklari (Kabisa yili mantiqi)": gen_time_leap_year,
        "14. Mantiqiy savollar: Shamlar va tayoqchalar": gen_logic_traps,
        "15. Harakatga doir: Poezd va tunnel": gen_train_tunnel,
        "16. Daryo oqimi bo‘ylab va qarshi harakat": gen_river_motion,
        "17. Ish unumdorligi (Birgalikda ishlash)": gen_work_efficiency,
        "18. Geometriya: Yuza va hajm (3D tasavvur)": gen_cube_surfaces,
        "19. To‘plamlar va Venn diagrammasi": gen_venn_diagram,
        "20. Mantiqiy xulosalar va algoritmlar": gen_logic_algorithms
    }

    gen_func = generator_map.get(topic)

    # Fallback
    if not gen_func:
        gen_func = gen_logic_traps

    seen = set()
    attempts = 0
    max_attempts = count * 10

    while len(questions) < count and attempts < max_attempts:
        attempts += 1
        try:
            q_text, ans, options = gen_func()
        except Exception as e:
            print(f"Error in {topic}: {e}")
            continue

        if q_text in seen:
            continue
        seen.add(q_text)

        formatted_options, answer_str = format_options(ans, options)

        questions.append({
            "question": q_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "mukammal_new"
        })

    random.shuffle(questions)
    return questions

# --- Admin Panel ---
def show_admin_panel():
    st.markdown("<h2 style='text-align: center; color: #0072CE;'>Admin Panel</h2>", unsafe_allow_html=True)
    st.write("O'quvchilar ro'yxati va ma'lumotlarini tahrirlash.")

    df = get_all_students()

    if df.empty:
        st.info("Hozircha o'quvchilar yo'q.")
        return

    # Configure columns
    edited_df = st.data_editor(
        df,
        column_config={
            "student_id": st.column_config.NumberColumn("ID", disabled=True),
            "full_name": "F.I.O",
            "phone": "Telefon",
            "attendance_count": st.column_config.NumberColumn("Darslar soni", min_value=0),
            "balance": st.column_config.NumberColumn("Balans", format="%d so'm"),
            "homework_status": st.column_config.TextColumn("Uy vazifalari", disabled=True),
            "registration_date": st.column_config.DatetimeColumn("Ro'yxatdan o'tgan sana", disabled=True),
        },
        hide_index=True,
        use_container_width=True,
        key="admin_editor"
    )

    if st.button("O'zgarishlarni saqlash"):
        conn = sqlite3.connect('math_quiz.db')
        c = conn.cursor()

        for index, row in edited_df.iterrows():
            c.execute("""UPDATE students
                         SET full_name=?, phone=?, attendance_count=?, balance=?
                         WHERE student_id=?""",
                      (row['full_name'], row['phone'], row['attendance_count'], row['balance'], row['student_id']))

        conn.commit()
        conn.close()
        st.success("Ma'lumotlar saqlandi!")
        time.sleep(1)
        st.rerun()

# --- Main Generator Dispatcher ---

def generate_quiz(topic_name, count=10):
    # 1-sinf Specific Topics (The 20 new topics)
    if topic_name in TOPICS_1SINF:
        return generate_1sinf_topic_questions(topic_name, count)

    # 2-sinf Specific Topics
    elif topic_name in TOPICS_2SINF:
        return generate_2sinf_topic_questions(topic_name, count)

    # 3-sinf Specific Topics
    elif topic_name in TOPICS_3SINF:
        return generate_3sinf_topic_questions(topic_name, count)

    # Mukammal Specific Topics
    elif topic_name in TOPICS_MUKAMMAL:
        return generate_mukammal_topic_questions(topic_name, count)

    # Legacy / Generic Fallbacks
    elif topic_name == "Jadvalli ko'paytirish":
        return generate_2sinf_jadvalli(count)
    elif topic_name == "O'nliklar bilan ishlash":
        return generate_2sinf_onliklar(count)
    elif topic_name == "Matnli masalalar":
        return generate_2sinf_matnli(count)
    elif "2-sinf" in topic_name:
         return generate_2sinf_questions(count)

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
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'global_auth' not in st.session_state:
        st.session_state.global_auth = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False

def check_login():
    if st.session_state.get('authenticated', False):
        return True

    st.markdown("<h1 style='text-align: center; color: #0072CE;'>Smart Learning Center</h1>", unsafe_allow_html=True)

    if os.path.exists("logo.png"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image("logo.png", use_container_width=True)

    # Step 1: Global Password
    if not st.session_state.get('global_auth', False):
        st.markdown("<h3 style='text-align: center;'>Platformaga kirish uchun parolni kiriting</h3>", unsafe_allow_html=True)
        password = st.text_input("Parol", type="password")
        if st.button("Kirish"):
            if password == "Smart2026":
                st.session_state.global_auth = True
                st.rerun()
            else:
                st.error("Xato parol!")
        return False

    # Step 2: User Identification
    st.markdown("<h3 style='text-align: center;'>Shaxsiy kabinetga kirish</h3>", unsafe_allow_html=True)

    phone = st.text_input("Telefon raqamingiz (masalan: 901234567)", key="phone_input")

    if st.button("Tekshirish"):
        if phone:
            student = get_student_by_phone(phone)
            if student:
                # Login existing user
                st.session_state.user_id = student[0]
                st.session_state.user_name = student[1]
                st.session_state.phone = student[2]
                st.session_state.is_admin = ("sardorbek" in student[1].strip().lower())
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.session_state.show_register = True
                st.session_state.reg_phone = phone
        else:
            st.warning("Telefon raqamni kiriting!")

    if st.session_state.get('show_register', False):
        st.warning("Siz ro'yxatdan o'tmagansiz. Iltimos, ismingizni kiriting.")
        full_name = st.text_input("Ism va Familiya", key="reg_name")
        if st.button("Ro'yxatdan o'tish"):
            if full_name and st.session_state.reg_phone:
                if register_student(full_name, st.session_state.reg_phone):
                    student = get_student_by_phone(st.session_state.reg_phone)
                    st.session_state.user_id = student[0]
                    st.session_state.user_name = student[1]
                    st.session_state.phone = student[2]
                    st.session_state.is_admin = ("sardorbek" in student[1].strip().lower())
                    st.session_state.authenticated = True
                    st.success("Ro'yxatdan o'tdingiz!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Xatolik yuz berdi yoki bu raqam allaqachon mavjud.")
            else:
                st.warning("Ism va familiyani kiriting!")

    return False

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
    elif st.session_state.current_view == 'mukammal':
        if st.session_state.quiz_state == 'playing' and 'topic' in st.session_state:
             title = st.session_state.topic
        else:
             title = "Mukammal Matematika (Olimpiada darajasi)"

    st.markdown(f"<h1 style='text-align: center;'>{subtitle}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>{title}</h3>", unsafe_allow_html=True)
    st.write("---")

def run_quiz_interface(topics_list):
    if st.session_state.quiz_state == 'welcome':
        name = st.text_input("Ismingizni kiriting:", key="user_name_input")
        topic = st.sidebar.selectbox("Mavzuni tanlang:", topics_list)

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

             # Database tracking for Mukammal
             if st.session_state.get('user_id') and st.session_state.current_view == 'mukammal':
                 result_entry = {
                     "topic": st.session_state.topic,
                     "score": st.session_state.score,
                     "total": st.session_state.total_questions,
                     "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                 }
                 add_homework_result(st.session_state.user_id, result_entry)

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
    random.seed(time.time())
    initialize_session()
    init_db()

    if not check_login():
        return

    # Sidebar Logo
    st.sidebar.image("logo.png", use_container_width=True)

    # Sidebar Title - Sardorbek Jo'raboyev muallifligidagi Mukammal Matematika platformasi (Gold)
    st.sidebar.markdown(
        """<div style="text-align: center; margin-bottom: 20px;">
            <p style="color: #FFD700; font-weight: bold;">Sardorbek Jo'raboyev muallifligidagi Mukammal Matematika platformasi</p>
        </div>""", unsafe_allow_html=True
    )

    st.sidebar.title("Menyu")
    if st.sidebar.button("🏠 Bosh sahifa", use_container_width=True): set_view('home')
    if st.sidebar.button("1-sinf", use_container_width=True): set_view('1-sinf')
    if st.sidebar.button("2-sinf", use_container_width=True): set_view('2-sinf')
    if st.sidebar.button("3-sinf", use_container_width=True): set_view('3-sinf')
    st.sidebar.markdown("---")
    if st.sidebar.button("🏆 Mukammal Matematika", use_container_width=True): set_view('mukammal')

    if st.session_state.get('is_admin'):
        st.sidebar.markdown("---")
        if st.sidebar.button("⚙️ Admin Panel", use_container_width=True):
            set_view('admin')

    color = "#0072CE"
    if st.session_state.current_view == '1-sinf': color = "#28a745"
    elif st.session_state.current_view == '2-sinf': color = "#003366"
    elif st.session_state.current_view == '3-sinf': color = "#0072CE"
    elif st.session_state.current_view == 'mukammal': color = "#FF4500"
    elif st.session_state.current_view == 'admin': color = "#333333"

    inject_css(color, is_home=(st.session_state.current_view == 'home'))

    if st.session_state.current_view == 'admin' and st.session_state.get('is_admin'):
        show_admin_panel()
    elif st.session_state.current_view != 'home':
        show_header()

    if st.session_state.current_view == 'home':
        _, col2, _ = st.columns([1, 1, 1])
        with col2:
            st.image("logo.png", use_container_width=True)

        st.markdown("<h3 style='text-align: center;'>Mukammal Matematika</h3>", unsafe_allow_html=True)
        st.write("---")

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
        run_quiz_interface(TOPICS_1SINF)

    elif st.session_state.current_view == '2-sinf':
        run_quiz_interface(TOPICS_2SINF)

    elif st.session_state.current_view == '3-sinf':
        run_quiz_interface(TOPICS_3SINF)

    elif st.session_state.current_view == 'mukammal':
        run_quiz_interface(TOPICS_MUKAMMAL)

if __name__ == "__main__":
    main()
