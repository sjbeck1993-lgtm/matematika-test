import re
import json

def parse_questions(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    topics = {}
    current_topic_key = None
    current_mode = None # 'exercises' or 'test'
    current_question = None

    # Regex patterns
    # Handles: "1- MAVZU: ...", "12-	MAVZU: ...", "2-\nMAVZU: ..."
    # We will look for "MAVZU:"
    mavzu_pattern = re.compile(r'MAVZU:\s*(.+)', re.IGNORECASE)

    # Pattern for "N-" on its own line or start of MAVZU line
    # Handles "1-", "[ 1-"
    number_pattern = re.compile(r'^\s*\[?\s*(\d+)-\s*')

    # Mode patterns
    mode_exercises_pattern = re.compile(r'^\s*I\.\s*Mashqlar', re.IGNORECASE)
    mode_test_pattern = re.compile(r'^\s*II\.\s*TEST', re.IGNORECASE)

    # Question start: "1. ..."
    question_start_pattern = re.compile(r'^\s*(\d+)\.\s*(.+)')

    # Buffer for handling split lines
    pending_number = None

    for line in lines:
        original_line = line
        line = line.strip()
        if not line:
            continue

        # Check for "N-" standalone
        # Be careful not to match "1- misol" if that exists?
        # The format seems to be "2-" at end of line or start of line.
        # But wait, "2-" is basically "2. ..." without dot? No, it's for MAVZU.

        # Check if this line is a Topic line
        mavzu_match = mavzu_pattern.search(line)
        if mavzu_match:
            title = mavzu_match.group(1).strip(' ]')

            # Look for number in this line
            num_match = number_pattern.match(line)
            topic_num = None
            if num_match:
                topic_num = num_match.group(1)
            elif pending_number:
                topic_num = pending_number
                pending_number = None
            else:
                # Maybe number is embedded in title or we missed it?
                # Assume previous topic + 1?
                # For now let's hope we caught it.
                pass

            if topic_num:
                current_topic_key = f"{topic_num}-MAVZU: {title}"
                topics[current_topic_key] = {'exercises': [], 'tests': []}
                current_mode = None
                current_question = None
                continue

        # Check for potential pending number "2-"
        # But only if it's not a question "2. ..."
        # And usually implies next line is MAVZU.
        if re.match(r'^\d+-\s*$', line):
            pending_number = line.split('-')[0].strip()
            continue

        # Check for Mode
        if mode_exercises_pattern.search(line):
            current_mode = 'exercises'
            current_question = None
            continue
        if mode_test_pattern.search(line):
            current_mode = 'test'
            current_question = None
            continue

        # Check for Question Start
        q_match = question_start_pattern.match(line)
        if q_match:
            # New question
            q_num = int(q_match.group(1))
            q_text = q_match.group(2)

            current_question = {
                'id': q_num,
                'question': q_text,
                'options': [],
                'answer': None
            }

            if current_topic_key and current_mode:
                if current_mode == 'exercises':
                    topics[current_topic_key]['exercises'].append(current_question)
                elif current_mode == 'test':
                    topics[current_topic_key]['tests'].append(current_question)

            # Also check if options are in this line
            # But we process options later or append line?
            # Let's append line content to 'question' just in case options are there?
            # q_text already has the rest of line.

            # Clear pending number if we found a question (it wasn't a topic number)
            pending_number = None
            continue

        # Continuation or Options
        if current_question:
            # Check if this line looks like options A) ...
            # Append to question text, will parse later
            current_question['question'] += " " + line

    # Post-processing options
    for topic_name, topic_data in topics.items():
        for q in topic_data['tests']:
            full_text = q['question']

            # Heuristic: Split by " A) ", " B) ", etc.
            # But also handle newline separated options.
            # Replace newlines with spaces first
            full_text = full_text.replace('\n', ' ')

            # Extract main question and options
            # Find the first occurrence of "A)" or "A. "
            # Text uses "A)"

            # Regex find iter
            # Pattern: (A\)|B\)|C\)|D\))

            # We want to split the string such that we get:
            # Q text
            # A) opt A
            # B) opt B
            # ...

            parts = re.split(r'\s([A-D])\)', " " + full_text)
            # parts[0] = question
            # parts[1] = 'A'
            # parts[2] = text for A
            # parts[3] = 'B'
            # parts[4] = text for B

            if len(parts) >= 9: # Q + 4*(Label+Val) = 1 + 8 = 9
                q['question'] = parts[0].strip()
                q['options'] = []

                # Reconstruct options
                # A
                opt_a = f"A) {parts[2].strip()}"
                opt_b = f"B) {parts[4].strip()}"
                opt_c = f"C) {parts[6].strip()}"
                opt_d = f"D) {parts[8].strip()}"

                # Check for garbage in last option (like next Topic header)
                # If next Topic started on same line (which we handled via lines iteration,
                # but if my line reader missed it?)
                # Actually, `lines` iteration separates lines.
                # `full_text` was built from lines.
                # If "2- MAVZU" was appended to `current_question['question']` because regex didn't catch it...
                # We need to clean `opt_d`.

                # Heuristic: if opt_d contains "MAVZU", truncate?
                # Or relying on improved parser loop to NOT append MAVZU line to question.

                q['options'] = [opt_a, opt_b, opt_c, opt_d]
            else:
                # Maybe formatting is different?
                # Just keep full text as question if we can't parse options?
                # But we need options list for UI.
                pass

    return topics

if __name__ == "__main__":
    data = parse_questions('data/raw_questions.txt')
    with open('data/questions.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Parsing complete. Found {len(data)} topics.")
