import pypdf
import pymupdf
import glob
import re
import json
import os

CHAR_MAP = {
    'A': 'А', 'B': 'Б', 'В': 'В', 'Г': 'Г',
    'a': 'А', 'b': 'Б', 'V': 'В', 'G': 'Г'
}

RAZDEL_TITLES = {
    1: 'Раздел 1 – Електротехника и радиотехника',
    2: 'Раздел 2 – Кодове и радиолюбителски съкращения. Правила и процедури',
    3: 'Раздел 3 – Нормативна уредба'
}
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_DIR, 'class2')
IMAGE_DIR = os.path.join(DATA_DIR, 'images')

def clean_text(t):
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    text = ' '.join(lines)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_embedded_images():
    os.makedirs(IMAGE_DIR, exist_ok=True)
    for pdf_path in sorted(glob.glob(os.path.join(DATA_DIR, '*.pdf'))):
        doc = pymupdf.open(pdf_path)
        stem = os.path.splitext(os.path.basename(pdf_path))[0]
        for page_number, page in enumerate(doc, start=1):
            for image_number, image_info in enumerate(page.get_images(full=True), start=1):
                xref = image_info[0]
                image = doc.extract_image(xref)
                extension = image['ext']
                image_path = os.path.join(IMAGE_DIR, f'{stem}_p{page_number}_img{image_number}.{extension}')
                with open(image_path, 'wb') as image_file:
                    image_file.write(image['image'])
                print(f"Extracted embedded image: {image_path}")

def extract_diagram_images():
    os.makedirs(IMAGE_DIR, exist_ok=True)
    pdf_path = os.path.join(DATA_DIR, 'class_2_razdel_1.pdf')
    if not os.path.exists(pdf_path):
        print(f"Warning: {pdf_path} not found for diagram extraction.")
        return

    doc = pymupdf.open(pdf_path)

    for q_num in range(45, 56):
        next_q = q_num + 1
        found = False
        for pno in range(len(doc)):
            page = doc[pno]
            rects = page.search_for(f'{q_num}.')
            if rects:
                y0 = max(0, rects[0].y0 - 5)
                if next_q <= 55:
                    next_rects = page.search_for(f'{next_q}.')
                    if next_rects:
                        y1 = next_rects[0].y0 - 5
                    else:
                        y1 = page.rect.height - 40
                else:
                    s56 = page.search_for('56.')
                    y1 = s56[0].y0 - 5 if s56 else page.rect.height - 40

                crop_rect = pymupdf.Rect(40, y0, 560, y1)
                pix = page.get_pixmap(clip=crop_rect, dpi=150)
                img_path = os.path.join(IMAGE_DIR, f'q{q_num}.png')
                pix.save(img_path)
                print(f"Saved diagram image for Q{q_num}: {img_path}")
                found = True
                break

def parse_pdf_files():
    all_questions = []

    pdf_files = sorted(glob.glob(os.path.join(DATA_DIR, '*.pdf')))
    if not pdf_files:
        print("No PDF files found in class2/ folder!")
        return []

    for path in pdf_files:
        filename = os.path.basename(path)
        razdel_num = 1 if 'razdel_1' in filename else (2 if 'razdel_2' in filename else 3)
        razdel_title = RAZDEL_TITLES.get(razdel_num, f'Раздел {razdel_num}')

        reader = pypdf.PdfReader(path)
        full_text = ''
        for page in reader.pages:
            t = page.extract_text()
            lines = []
            for line in t.split('\n'):
                s = line.strip()
                # Exclude running headers and footers
                if s in ['КОМИСИЯ', 'ЗА РЕГУЛИРАНЕ', 'НА СЪОБЩЕНИЯТА', 'Радиолюбителски клас 2'] or 'Актуализиран конспект' in s or (s.isdigit() and len(s) <= 3):
                    continue
                lines.append(line)
            full_text += '\n'.join(lines) + '\n'

        q_matches = list(re.finditer(r'^\s*(\d+)\.\s*', full_text, re.MULTILINE))

        for i in range(len(q_matches)):
            q_num = int(q_matches[i].group(1))
            start = q_matches[i].start()
            end = q_matches[i+1].start() if i+1 < len(q_matches) else len(full_text)
            block = full_text[start:end].strip()

            # Find answer match inside parentheses e.g. (А), (Б), (В), (Г)
            ans_match = list(re.finditer(r'\(\s*([АБВГА-ДA-Da-d]|B)\s*\)', block))
            if not ans_match:
                print(f"Error: No answer match for Q{q_num} in {filename}")
                continue

            last_ans_match = ans_match[-1]
            raw_ans = last_ans_match.group(1).upper()
            ans = CHAR_MAP.get(raw_ans, raw_ans)

            header_text = block[:last_ans_match.start()].strip()
            header_text = re.sub(r'^\d+\.\s*', '', header_text)
            header_text = clean_text(header_text)

            options_part = block[last_ans_match.end():].strip()

            # Find options (А., Б., В., Г.)
            opt_matches = list(re.finditer(r'^\s*([АБВГА-ДA-D][\.\)])\s*', options_part, re.MULTILINE))
            options = {}
            for idx in range(len(opt_matches)):
                raw_letter = opt_matches[idx].group(1)[0]
                letter = CHAR_MAP.get(raw_letter, raw_letter)
                opt_start = opt_matches[idx].end()
                opt_end = opt_matches[idx+1].start() if idx+1 < len(opt_matches) else len(options_part)
                opt_val = clean_text(options_part[opt_start:opt_end])
                opt_val = opt_val.rstrip('.;').rstrip()
                options[letter] = opt_val

            is_image_q = (razdel_num == 1 and 45 <= q_num <= 55)
            q_id = f"r{razdel_num}_q{q_num}"

            item = {
                'id': q_id,
                'razdel': razdel_num,
                'razdel_title': razdel_title,
                'q_num': q_num,
                'question': header_text,
                'correct_answer': ans,
                'options': options,
                'has_image': is_image_q,
                'image_path': f'class2/images/q{q_num}.png' if is_image_q else None
            }
            all_questions.append(item)

    return all_questions

def main():
    print("Extracting embedded PDF images...")
    extract_embedded_images()

    print("Extracting diagram images...")
    extract_diagram_images()

    print("\nParsing questions from PDF files...")
    questions = parse_pdf_files()
    print(f"Total questions parsed: {len(questions)}")

    # Save complete questions database (with correct answers)
    with open(os.path.join(DATA_DIR, 'questions.json'), 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print("Saved complete questions database to 'class2/questions.json'")

    # Save public questions database (ANSWERS HIDDEN)
    questions_hidden = []
    for q in questions:
        q_copy = dict(q)
        del q_copy['correct_answer'] # Hide answer from test taker data structure
        questions_hidden.append(q_copy)

    with open(os.path.join(DATA_DIR, 'questions_hidden_answers.json'), 'w', encoding='utf-8') as f:
        json.dump(questions_hidden, f, ensure_ascii=False, indent=2)
    print("Saved answers-hidden question bank to 'class2/questions_hidden_answers.json'")

    # Save human-readable text document containing all questions (ANSWERS HIDDEN)
    with open(os.path.join(DATA_DIR, 'questions_formatted_no_answers.txt'), 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("   ИЗПИТНИ ВЪПРОСИ ЗА РАДИОЛЮБИТЕЛИ - КЛАС 2 (БЕЗ ОТГОВОРИ)\n")
        f.write("="*70 + "\n\n")

        current_razdel = None
        for q in questions:
            if q['razdel'] != current_razdel:
                current_razdel = q['razdel']
                f.write(f"\n\n{'='*70}\n")
                f.write(f"  {q['razdel_title'].upper()}\n")
                f.write(f"{'='*70}\n\n")

            f.write(f"{q['q_num']}. {q['question']}\n")
            if q['has_image']:
                f.write(f"   [Виж диаграмата/фигурата: {q['image_path']}]\n")
            for opt_key in ['А', 'Б', 'В', 'Г']:
                if opt_key in q['options']:
                    f.write(f"   {opt_key}. {q['options'][opt_key]}\n")
            f.write("\n")

    print("Saved human-readable document without answers to 'class2/questions_formatted_no_answers.txt'")
    print("\nExtraction finished successfully!")

if __name__ == '__main__':
    main()
