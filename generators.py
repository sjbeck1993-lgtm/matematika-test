import random

DYNAMIC_TOPICS = [
    "Mantiqiy masalalar",
    "Sonli zanjirlar",
    "Geometrik hisob-kitoblar"
]

def get_names(n=2):
    names = ["Ali", "Vali", "Sadiya", "Karim", "Lola", "Zebo", "Anvar", "Dilnoza", "Jasur", "Malika"]
    return random.sample(names, n)

def get_item():
    items = ["daftar", "qalam", "olma", "kitob", "shar", "gul", "konfet"]
    return random.choice(items)

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

def generate_quiz(topic_name, count=10):
    if "Mantiqiy" in topic_name:
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
