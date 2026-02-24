import streamlit as st
import random
import time
import os
import io
import json
import base64
import datetime
from PIL import Image, ImageDraw, ImageFont

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

# --- Generators Logic ---
DYNAMIC_TOPICS = [
    "1-sinf Matematika",
    "2-sinf Matematika",
    "Mantiqiy masalalar",
    "Sonli zanjirlar",
    "Geometrik hisob-kitoblar",
    "3-sinf Mukammal Matematika",
    "Sonlar olami",
    "Sodda yig'indi",
    "Mantiqiy o'yinlar",
    "Jadvalli ko'paytirish",
    "O'nliklar bilan ishlash",
    "Matnli masalalar",
    "Matnli masalalar (3-sinf)",
    "Olimpiada masalalari"
]

def get_names(n=2):
    names = ["Ali", "Vali", "Sadiya", "Karim", "Lola", "Zebo", "Anvar", "Dilnoza", "Jasur", "Malika"]
    return random.sample(names, n)

def get_item():
    items = ["daftar", "qalam", "olma", "kitob", "shar", "gul", "konfet"]
    return random.choice(items)

def generate_1sinf_questions(count=10):
    questions = []
    for _ in range(count):
        names = get_names(2)
        item = get_item()
        q_type = random.choice(['add', 'sub'])

        if q_type == 'add':
            n1 = random.randint(1, 10)
            n2 = random.randint(1, 10)
            # Sum is max 20, so no check needed
            question_text = f"{names[0]}da {n1} ta {item} bor edi, unga yana {n2} ta {item} berishdi. Jami nechta?"
            ans = n1 + n2
        else: # sub
            n1 = random.randint(5, 20)
            n2 = random.randint(1, 10)
            # Ensure n1 > n2
            while n2 >= n1:
                n2 = random.randint(1, n1 - 1)
            question_text = f"{names[0]}da {n1} ta {item} bor edi. U {names[1]}ga {n2} tasini berdi. {names[0]}da nechta {item} qoldi?"
            ans = n1 - n2

        # Options
        options = {ans}
        while len(options) < 3:
            fake = ans + random.randint(-3, 3)
            if fake >= 0 and fake != ans:
                options.add(fake)

        opts_list = list(options)
        random.shuffle(opts_list)

        formatted_options = []
        answer_str = ""
        labels = ["A", "B", "C"]

        for i, val in enumerate(opts_list):
            opt_str = f"{labels[i]}) {val}"
            formatted_options.append(opt_str)
            if val == ans:
                answer_str = opt_str

        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "1sinf"
        })
    return questions

def generate_2sinf_questions(count=10):
    questions = []
    for _ in range(count):
        names = get_names(2)
        q_type = random.choice(['fabric', 'logic', 'arithmetic'])

        if q_type == 'fabric':
            # Example: 40 meters -> 20 dresses.
            # Dresses count
            dresses = random.randint(2, 20)
            # Material per dress
            per_dress = random.randint(2, 5)
            total_material = dresses * per_dress

            if random.random() < 0.5:
                question_text = f"{total_material} metr matodan {dresses} ta ko'ylak tikishdi. Bitta ko'ylak uchun necha metr mato ketgan?"
                ans = per_dress
            else:
                question_text = f"Bitta ko'ylak uchun {per_dress} metr mato kerak. {total_material} metr matodan nechta ko'ylak tikish mumkin?"
                ans = dresses

        elif q_type == 'logic':
             # Simple logic: Age difference, or comparisons
             age1 = random.randint(7, 15)
             diff = random.randint(2, 5)
             age2 = age1 + diff
             question_text = f"{names[0]} {age1} yoshda. {names[1]} undan {diff} yosh katta. {names[1]} necha yoshda?"
             ans = age2

        else: # Arithmetic mix up to 100
            op = random.choice(['add', 'sub'])
            if op == 'add':
                n1 = random.randint(10, 50)
                n2 = random.randint(10, 50)
                question_text = f"{n1} ga {n2} ni qo'shing."
                ans = n1 + n2
            else:
                n1 = random.randint(20, 100)
                n2 = random.randint(10, n1)
                question_text = f"{n1} dan {n2} ni ayiring."
                ans = n1 - n2

        # Options
        options = {ans}
        while len(options) < 3:
            fake = ans + random.randint(-5, 5)
            if fake >= 0 and fake != ans:
                options.add(fake)

        opts_list = list(options)
        random.shuffle(opts_list)

        formatted_options = []
        answer_str = ""
        labels = ["A", "B", "C"]

        for i, val in enumerate(opts_list):
            opt_str = f"{labels[i]}) {val}"
            formatted_options.append(opt_str)
            if val == ans:
                answer_str = opt_str

        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "2sinf"
        })
    return questions

def generate_logical_questions(count=10):
    questions = []
    for _ in range(count):
        q_type = random.choice([1, 2, 3])
        names = get_names(2)
        item = get_item()

        if q_type == 1: # Addition
            n1 = random.randint(5, 20)
            n2 = random.randint(5, 20)
            question_text = f"{names[0]}da {n1} ta {item}, {names[1]}da {n2} ta {item} bor. Ikkalasida jami nechta {item} bor?"
            ans = n1 + n2
        elif q_type == 2: # Subtraction
            n1 = random.randint(10, 30)
            n2 = random.randint(1, n1 - 1)
            question_text = f"{names[0]}da {n1} ta {item} bor edi. U {names[1]}ga {n2} tasini berdi. {names[0]}da nechta {item} qoldi?"
            ans = n1 - n2
        else: # Comparison
            n1 = random.randint(10, 50)
            n2 = random.randint(10, 50)
            while n1 == n2:
                n2 = random.randint(10, 50)

            diff = abs(n1 - n2)
            if n1 > n2:
                question_text = f"{names[0]}da {n1} ta, {names[1]}da {n2} ta {item} bor. {names[0]}da {names[1]}ga qaraganda nechta ko'p {item} bor?"
            else:
                question_text = f"{names[0]}da {n1} ta, {names[1]}da {n2} ta {item} bor. {names[0]}da {names[1]}ga qaraganda nechta kam {item} bor?"
            ans = diff

        # Generate options
        options = {ans}
        while len(options) < 3:
            fake = ans + random.randint(-5, 5)
            if fake > 0 and fake != ans:
                options.add(fake)

        opts_list = list(options)
        random.shuffle(opts_list)

        # Format options as A) 10, B) 12, etc.
        formatted_options = []
        answer_str = ""
        labels = ["A", "B", "C"]

        for i, val in enumerate(opts_list):
            opt_str = f"{labels[i]}) {val}"
            formatted_options.append(opt_str)
            if val == ans:
                answer_str = opt_str

        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "logic"
        })
    return questions

def generate_number_chain_questions(count=10):
    questions = []
    for _ in range(count):
        start = random.randint(1, 20)
        step = random.randint(2, 9)
        length = 5

        # 80% Arithmetic, 20% Geometric (simple)
        if random.random() < 0.8:
            seq = [start + i*step for i in range(length)]
            q_type = "arithmetic"
        else:
            step = random.randint(2, 3) # Keep multiplier small
            seq = [start * (step**i) for i in range(length)]
            q_type = "geometric"

        missing_idx = random.randint(1, length-1) # Don't hide first element usually
        ans = seq[missing_idx]
        seq_display = [str(x) for x in seq]
        seq_display[missing_idx] = "?"

        question_text = f"Sonli zanjirni davom ettiring: {', '.join(seq_display)}"

        # Options
        options = {ans}
        while len(options) < 3:
            fake = ans + random.randint(-step, step)
            if fake != ans and fake > 0:
                options.add(fake)

        opts_list = list(options)
        random.shuffle(opts_list)

        formatted_options = []
        answer_str = ""
        labels = ["A", "B", "C"]

        for i, val in enumerate(opts_list):
            opt_str = f"{labels[i]}) {val}"
            formatted_options.append(opt_str)
            if val == ans:
                answer_str = opt_str

        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "chain"
        })
    return questions

def generate_geometry_questions(count=10):
    questions = []
    for _ in range(count):
        shape = random.choice(["square", "rectangle"])

        if shape == "square":
            a = random.randint(2, 15)
            if random.random() < 0.5:
                question_text = f"Kvadratning tomoni {a} sm. Uning perimetrini toping."
                ans = 4 * a
            else:
                question_text = f"Kvadratning tomoni {a} sm. Uning yuzini toping."
                ans = a * a
        else: # rectangle
            a = random.randint(2, 12)
            b = a + random.randint(1, 5)
            if random.random() < 0.5:
                question_text = f"To'g'ri to'rtburchakning tomonlari {a} sm va {b} sm. Uning perimetrini toping."
                ans = 2 * (a + b)
            else:
                question_text = f"To'g'ri to'rtburchakning tomonlari {a} sm va {b} sm. Uning yuzini toping."
                ans = a * b

        # Options
        options = {ans}
        while len(options) < 3:
            fake = ans + random.randint(-5, 5) * random.choice([1, 2])
            if fake > 0 and fake != ans:
                options.add(fake)

        opts_list = list(options)
        random.shuffle(opts_list)

        formatted_options = []
        answer_str = ""
        labels = ["A", "B", "C"]

        for i, val in enumerate(opts_list):
            opt_str = f"{labels[i]}) {val}"
            formatted_options.append(opt_str)
            if val == ans:
                answer_str = opt_str

        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "geometry"
        })
    return questions

def generate_3sinf_word_problems(count=10):
    questions = []
    names_list = ["Ali", "Sadiya", "Vali", "Madina"]
    items_list = ["daftar", "qalam", "kitob", "olma", "konfet", "shar", "gul"]

    for _ in range(count):
        name1 = random.choice(names_list)
        name2 = random.choice([n for n in names_list if n != name1])
        item = random.choice(items_list)
        q_type = random.choice(['add', 'sub', 'mult', 'div'])

        if q_type == 'add':
            n1 = random.randint(10, 100)
            n2 = random.randint(10, 100)
            question_text = f"{name1} {n1} ta {item} oldi va yana {n2} ta oldi. Hammasi qancha?"
            ans = n1 + n2
        elif q_type == 'sub':
            n1 = random.randint(20, 100)
            n2 = random.randint(10, n1 - 10)
            question_text = f"{name1}da {n1} ta {item} bor edi. U {name2}ga {n2} tasini berdi. {name1}da nechta {item} qoldi?"
            ans = n1 - n2
        elif q_type == 'mult':
            n1 = random.randint(2, 10)
            n2 = random.randint(2, 10)
            # Make sure product is within reasonable range, though logic allows larger
            question_text = f"{name1}da {n1} ta quti bor. Har bir qutida {n2} tadan {item} bor. Jami nechta {item} bor?"
            ans = n1 * n2
        else: # div
            total = random.randint(10, 100)
            divisor = random.randint(2, 10)
            # Ensure divisibility
            while total % divisor != 0:
                total = random.randint(10, 100)

            question_text = f"{name1} {total} ta {item}ni {divisor} ta do'stiga teng bo'lib berdi. Har biriga nechtadan tegdi?"
            ans = total // divisor

        # Options
        options = {ans}
        while len(options) < 3:
            fake = ans + random.randint(-5, 5)
            if fake > 0 and fake != ans:
                options.add(fake)

        opts_list = list(options)
        random.shuffle(opts_list)

        formatted_options = []
        answer_str = ""
        labels = ["A", "B", "C"]

        for i, val in enumerate(opts_list):
            opt_str = f"{labels[i]}) {val}"
            formatted_options.append(opt_str)
            if val == ans:
                answer_str = opt_str

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
        choice = random.choice(['logic', 'chain', 'geometry'])
        if choice == 'logic':
            pool = generate_logical_questions(1)
        elif choice == 'chain':
            pool = generate_number_chain_questions(1)
        else:
            pool = generate_geometry_questions(1)

        if pool:
            q = pool[0]
            # q['type'] = 'olympiad' # Override type - keep original type
            questions.append(q)
    return questions

def generate_1sinf_sonlar(count=10):
    questions = []
    for _ in range(count):
        q_type = random.choice(['compare', 'sequence'])
        if q_type == 'compare':
            n1 = random.randint(1, 20)
            n2 = random.randint(1, 20)
            while n1 == n2:
                n2 = random.randint(1, 20)

            question_text = f"{n1} va {n2}: qaysi biri katta?"
            if n1 > n2:
                ans = str(n1)
            else:
                ans = str(n2)

            options = [str(n1), str(n2), "="]
            random.shuffle(options)
        else:
            # Simple sequence 1, 2, 3, ?
            start = random.randint(1, 15)
            seq = [start, start+1, start+2, start+3]
            missing_idx = 3
            ans = str(seq[missing_idx])
            seq_display = [str(x) for x in seq]
            seq_display[missing_idx] = "?"
            question_text = f"Ketma-ketlikni to'ldiring: {', '.join(seq_display)}"

            opts = {ans}
            while len(opts) < 3:
                fake = str(int(ans) + random.randint(-2, 2))
                if fake != ans and int(fake) > 0:
                    opts.add(fake)
            options = list(opts)
            random.shuffle(options)

        formatted_options = []
        answer_str = ""
        labels = ["A", "B", "C"]

        for i, val in enumerate(options):
            opt_str = f"{labels[i]}) {val}"
            formatted_options.append(opt_str)
            if val == ans:
                answer_str = opt_str

        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "1sinf_sonlar"
        })
    return questions

def generate_1sinf_yigindi(count=10):
    questions = []
    for _ in range(count):
        n1 = random.randint(1, 10)
        n2 = random.randint(1, 10)
        question_text = f"{n1} + {n2} = ?"
        ans = n1 + n2

        options = {ans}
        while len(options) < 3:
            fake = ans + random.randint(-3, 3)
            if fake >= 0 and fake != ans:
                options.add(fake)

        opts_list = list(options)
        random.shuffle(opts_list)

        formatted_options = []
        answer_str = ""
        labels = ["A", "B", "C"]

        for i, val in enumerate(opts_list):
            opt_str = f"{labels[i]}) {val}"
            formatted_options.append(opt_str)
            if val == ans:
                answer_str = opt_str

        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "1sinf_yigindi"
        })
    return questions

def generate_1sinf_mantiq(count=10):
    questions = []
    for _ in range(count):
        q_type = random.choice(['odd_one', 'logic'])

        if q_type == 'odd_one':
            cats = [
                (["olma", "nok", "uzum"], "sabzi"),
                (["mushuk", "kuchuk", "sigir"], "chumoli"),
                (["qalam", "daftar", "o'chirgich"], "to'p"),
                (["mashina", "avtobus", "poyezd"], "uy")
            ]
            cat, odd = random.choice(cats)

            c_items = random.sample(cat, 2)
            options = c_items + [odd]
            random.shuffle(options)

            question_text = f"Qaysi biri ortiqcha: {', '.join(options)}?"
            ans = odd

        else:
            question_text = "Qizil olma yashil olmadan shirinroq. Yashil olma sariq olmadan shirinroq. Qaysi biri eng shirin?"
            ans = "Qizil olma"
            options = ["Qizil olma", "Yashil olma", "Sariq olma"]
            random.shuffle(options)

        formatted_options = []
        answer_str = ""
        labels = ["A", "B", "C"]

        for i, val in enumerate(options):
            opt_str = f"{labels[i]}) {val}"
            formatted_options.append(opt_str)
            if val == ans:
                answer_str = opt_str

        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "1sinf_mantiq"
        })
    return questions

def generate_2sinf_jadvalli(count=10):
    questions = []
    for _ in range(count):
        n1 = random.randint(2, 9)
        n2 = random.randint(2, 9)
        question_text = f"{n1} x {n2} = ?"
        ans = n1 * n2

        options = {ans}
        while len(options) < 3:
            fake = ans + random.randint(-5, 5)
            if fake > 0 and fake != ans:
                options.add(fake)
        options = list(options)
        random.shuffle(options)

        formatted_options = []
        answer_str = ""
        labels = ["A", "B", "C"]
        for i, val in enumerate(options):
            opt_str = f"{labels[i]}) {val}"
            formatted_options.append(opt_str)
            if val == ans:
                answer_str = opt_str

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

        options = {ans}
        while len(options) < 3:
            fake = ans + random.randint(-10, 10)
            if fake > 0 and fake != ans:
                options.add(fake)
        options = list(options)
        random.shuffle(options)

        formatted_options = []
        answer_str = ""
        labels = ["A", "B", "C"]
        for i, val in enumerate(options):
            opt_str = f"{labels[i]}) {val}"
            formatted_options.append(opt_str)
            if val == ans:
                answer_str = opt_str

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

        options = {ans}
        while len(options) < 3:
            fake = ans + random.randint(-3, 3)
            if fake > 0 and fake != ans:
                options.add(fake)
        options = list(options)
        random.shuffle(options)

        formatted_options = []
        answer_str = ""
        labels = ["A", "B", "C"]
        for i, val in enumerate(options):
            opt_str = f"{labels[i]}) {val}"
            formatted_options.append(opt_str)
            if val == ans:
                answer_str = opt_str

        questions.append({
            "question": question_text,
            "options": formatted_options,
            "answer": answer_str,
            "type": "2sinf_matnli"
        })
    return questions

def get_3rd_grade_questions(count=10):
    return generate_3sinf_word_problems(count)

def get_advanced_questions(count=10):
    return generate_olympiad_questions(count)

def generate_quiz(topic_name, count=10):
    # 1-sinf
    if topic_name == "Sonlar olami":
        return generate_1sinf_sonlar(count)
    elif topic_name == "Sodda yig'indi":
        return generate_1sinf_yigindi(count)
    elif topic_name == "Mantiqiy o'yinlar":
        return generate_1sinf_mantiq(count)
    elif "1-sinf" in topic_name: # Fallback or Legacy
        return generate_1sinf_questions(count)

    # 2-sinf
    elif topic_name == "Jadvalli ko'paytirish":
        return generate_2sinf_jadvalli(count)
    elif topic_name == "O'nliklar bilan ishlash":
        return generate_2sinf_onliklar(count)
    elif topic_name == "Matnli masalalar":
        return generate_2sinf_matnli(count)
    elif "2-sinf" in topic_name: # Fallback or Legacy
        return generate_2sinf_questions(count)

    # 3-sinf
    elif "Matnli masalalar (3-sinf)" in topic_name:
        return get_3rd_grade_questions(count)

    # Mukammal / Olimpiada
    elif "Olimpiada masalalari" in topic_name:
        return get_advanced_questions(count)

    # Legacy mapping for backward compatibility
    elif "Mukammal" in topic_name or "Dinamik generator" in topic_name:
        return get_3rd_grade_questions(count)

    # Legacy / General
    elif "Mantiqiy" in topic_name:
        return generate_logical_questions(count)
    elif "Sonli zanjirlar" in topic_name:
        return generate_number_chain_questions(count)
    elif "Geometrik" in topic_name:
        return generate_geometry_questions(count)
    else:
        return []

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
    # Reset quiz state when switching views
    if 'quiz_questions' in st.session_state:
        st.session_state.quiz_questions = []
    if 'score' in st.session_state:
        st.session_state.score = 0
    if 'question_count' in st.session_state:
        st.session_state.question_count = 0
    if 'topic' in st.session_state:
        del st.session_state.topic
    if 'feedback' in st.session_state:
        del st.session_state.feedback
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

                    # Fallback if empty
                    if not pool:
                        if st.session_state.current_view == '3-sinf':
                            pool = get_3rd_grade_questions(5)
                        elif st.session_state.current_view == 'mukammal':
                            pool = get_advanced_questions(5)

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
