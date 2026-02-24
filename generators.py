import random

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
        return generate_3sinf_word_problems(count)

    # Mukammal / Olimpiada
    elif "Olimpiada masalalari" in topic_name:
        return generate_olympiad_questions(count)

    # Legacy mapping for backward compatibility
    elif "Mukammal" in topic_name or "Dinamik generator" in topic_name:
        return generate_3sinf_word_problems(count)

    # Legacy / General
    elif "Mantiqiy" in topic_name:
        return generate_logical_questions(count)
    elif "Sonli zanjirlar" in topic_name:
        return generate_number_chain_questions(count)
    elif "Geometrik" in topic_name:
        return generate_geometry_questions(count)
    else:
        return []

if __name__ == "__main__":
    # Simple test
    print(generate_quiz("Mantiqiy masalalar", 1))
