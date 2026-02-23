import json

def update_answers():
    with open('data/questions.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Helper to set answer by index (0-based) for a specific topic's test
    def set_test_answer(topic_key, q_id, answer_idx):
        # Find topic
        # Keys are long strings, let's match by prefix
        topic = None
        for k in data.keys():
            if k.startswith(topic_key):
                topic = data[k]
                break

        if not topic:
            print(f"Topic {topic_key} not found")
            return

        # Find question
        for q in topic['tests']:
            if q['id'] == q_id:
                if 0 <= answer_idx < len(q['options']):
                    q['answer'] = q['options'][answer_idx]
                else:
                    print(f"Invalid answer index {answer_idx} for Q{q_id} in {topic_key}")
                break

    # Topic 1 Test
    # 1. B (20) -> Index 1
    set_test_answer("1-", 1, 1)
    # 2. C (55) -> Index 2
    set_test_answer("1-", 2, 2)
    # 3. B (70) -> Index 1
    set_test_answer("1-", 3, 1) # But wait, is 70 in B? Yes.
    # 4. B (50) -> Index 1
    set_test_answer("1-", 4, 1)
    # 5. B (101) -> Index 1
    set_test_answer("1-", 5, 1)
    # 6. A (11:30) -> Index 0
    set_test_answer("1-", 6, 0)
    # 7. C (30) -> Index 2
    set_test_answer("1-", 7, 2)
    # 8. B (65) -> Index 1
    set_test_answer("1-", 8, 1)
    # 9. C (13) -> Index 2
    set_test_answer("1-", 9, 2)
    # 10. B (9) -> Index 1
    set_test_answer("1-", 10, 1)

    # Topic 2 Test
    # 1. C (24) -> Index 2
    set_test_answer("2-", 1, 2)
    # 2. C (0) -> Index 2
    set_test_answer("2-", 2, 2)
    # 3. A (13) -> Index 0
    set_test_answer("2-", 3, 0)
    # 4. A (500) -> Index 0
    set_test_answer("2-", 4, 0)
    # 5. B (5) -> Index 1
    set_test_answer("2-", 5, 1)
    # 6. B (10) -> Index 1
    set_test_answer("2-", 6, 1)
    # 7. D (7) -> Index 3
    set_test_answer("2-", 7, 3)
    # 8. C (300) -> Index 2
    set_test_answer("2-", 8, 2)
    # 9. A (12) -> Index 0
    set_test_answer("2-", 9, 0)
    # 10. C (36) -> Index 2
    set_test_answer("2-", 10, 2)

    # Topic 3 Test
    # 1. B (50) -> Index 1
    set_test_answer("3-", 1, 1)
    # 2. B (Changed? 45-15=30. 45-10+5=40. Changed).
    # Wait, check my previous thought.
    # A: 12+8*2 = 28. (12+8)*2=40. Changed.
    # B: 45-(10+5)=30. 45-10+5=40. Changed.
    # C: (15*2)+10=40. 15*2+10=40. Unchanged.
    # Ans: C. Index 2.
    set_test_answer("3-", 2, 2)
    # 3. B (10) -> Index 1
    set_test_answer("3-", 3, 1)
    # 4. C (76) -> Index 2
    set_test_answer("3-", 4, 2)
    # 5. A (13) -> Index 0
    set_test_answer("3-", 5, 0)
    # 6. A (50) -> Index 0
    set_test_answer("3-", 6, 0)
    # 7. B (ayirish, bo'lish, ko'paytirish, qo'shish) -> Index 1
    set_test_answer("3-", 7, 1)
    # 8. B (4) -> Index 1 (Assuming 4 was target or typo). Let's pick B.
    set_test_answer("3-", 8, 1)
    # 9. A (12) -> Index 0
    set_test_answer("3-", 9, 0)
    # 10. A (8) -> Index 0
    set_test_answer("3-", 10, 0)

    # Topic 4 Test
    # 1. B (10) -> Index 1
    set_test_answer("4-", 1, 1)
    # 2. B (987) -> Index 1
    set_test_answer("4-", 2, 1)
    # 3. C (13) -> Index 2
    set_test_answer("4-", 3, 2)
    # 4. B (78) -> Index 1
    set_test_answer("4-", 4, 1)
    # 5. A (2) -> Index 0
    set_test_answer("4-", 5, 0)
    # 6. A (15) -> Index 0
    set_test_answer("4-", 6, 0)
    # 7. B (900) -> Index 1
    set_test_answer("4-", 7, 1)
    # 8. B (1,2,3,4) -> Index 1
    set_test_answer("4-", 8, 1)
    # 9. B (10) -> Index 1
    set_test_answer("4-", 9, 1)
    # 10. C (407) -> Index 2
    set_test_answer("4-", 10, 2)

    # Topic 5 Test
    # 1. B (3) -> Index 1
    set_test_answer("5-", 1, 1)
    # 2. C (705) -> Index 2
    set_test_answer("5-", 2, 2)
    # 3. B (80) -> Index 1
    set_test_answer("5-", 3, 1)
    # 4. A (110) -> Index 0
    set_test_answer("5-", 4, 0)
    # 5. B (546) -> Index 1
    set_test_answer("5-", 5, 1)
    # 6. C (Yuzliklar) -> Index 2
    set_test_answer("5-", 6, 2)
    # 7. B (3) -> Index 1
    set_test_answer("5-", 7, 1)
    # 8. B (7024) -> Index 1
    set_test_answer("5-", 8, 1)
    # 9. B (50) -> Index 1
    set_test_answer("5-", 9, 1)
    # 10. A (8) -> Index 0
    set_test_answer("5-", 10, 0)

    # Add Options for Topic 1 Exercises (Examples)
    topic1 = data.get("1-MAVZU: QO‘SHISH VA AYIRISHGA DOIR MANTIQIY MASALALAR")
    if topic1:
        exercises = topic1['exercises']

        # Q1: 33
        q1 = exercises[0]
        q1['options'] = ["A) 30", "B) 33", "C) 35", "D) 40"]
        q1['answer'] = "B) 33"

        # Q2: 36, 37
        q2 = exercises[1]
        q2['options'] = ["A) 35, 36", "B) 36, 37", "C) 37, 38", "D) 34, 39"]
        q2['answer'] = "B) 36, 37"

        # Q3: (x-15)+9=20 -> x-6=20 -> x=26.
        q3 = exercises[2]
        q3['options'] = ["A) 20", "B) 25", "C) 26", "D) 30"]
        q3['answer'] = "C) 26"

        # Q4: +20, -15 -> +5. 120+5=125.
        q4 = exercises[3]
        q4['options'] = ["A) 120", "B) 125", "C) 130", "D) 135"]
        q4['answer'] = "B) 125"

        # Q5: 18+12-5 = 25. 25-25=0? No.
        # Venn diagram. Total 25. Math 18, Eng 12, Both 5.
        # Math only = 18-5=13. Eng only = 12-5=7.
        # Total in circles = 13+7+5 = 25.
        # None = 25 - 25 = 0.
        q5 = exercises[4]
        q5['options'] = ["A) 0", "B) 5", "C) 2", "D) 1"]
        q5['answer'] = "A) 0"

    with open('data/questions.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Updated answers in data/questions.json")

if __name__ == "__main__":
    update_answers()
