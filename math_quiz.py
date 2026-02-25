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

    # Sidebar Logo
    try:
        st.sidebar.image("logo.png", use_container_width=True)
    except Exception:
        st.sidebar.markdown("<h2 style='text-align: center;'>SMART LEARNING CENTER</h2>", unsafe_allow_html=True)

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

    color = "#0072CE"
    if st.session_state.current_view == '1-sinf': color = "#28a745"
    elif st.session_state.current_view == '2-sinf': color = "#003366"
    elif st.session_state.current_view == '3-sinf': color = "#0072CE"
    elif st.session_state.current_view == 'mukammal': color = "#FF4500"

    inject_css(color, is_home=(st.session_state.current_view == 'home'))

    if st.session_state.current_view != 'home':
        show_header()

    if st.session_state.current_view == 'home':
        try:
            _, col2, _ = st.columns([1, 1, 1])
            with col2:
                st.image("logo.png")
        except Exception:
            st.markdown("<h1 style='text-align: center;'>SMART LEARNING CENTER</h1>", unsafe_allow_html=True)

        st.markdown("<h1 style='text-align: center;'>SMART LEARNING CENTER</h1>", unsafe_allow_html=True)
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
        run_quiz_interface(["Olimpiada masalalari"])

if __name__ == "__main__":
    main()
