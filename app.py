import tkinter as tk
from tkinter import ttk, messagebox, font
import json
import random
import time
import os

class HamRadioTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Тест за Радиолюбители - Клас 2 (КРС)")
        self.root.geometry("950x700")
        self.root.minsize(850, 600)

        # Load questions
        self.questions_data = self.load_questions()

        # Test State
        self.test_questions = []
        self.user_answers = {}    # {q_index: 'А'/'Б'/'В'/'Г'}
        self.flagged_questions = set() # {q_index}
        self.current_q_index = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.timer_running = False
        self.is_review_mode = False
        self.review_only_wrong = False
        self.review_indices = []
        self.review_pos = 0
        self.current_image = None  # Reference to prevent garbage collection

        # Configure Styles
        self.setup_styles()

        # Container frame
        self.container = ttk.Frame(self.root, padding="15")
        self.container.pack(fill=tk.BOTH, expand=True)

        # Show Main Menu
        self.show_main_menu()

    def load_questions(self):
        project_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(project_dir, "class2", "questions.json")
        if not os.path.exists(json_path):
            messagebox.showerror("Грешка", "Файлът 'class2/questions.json' не е намерен! Моля, стартирайте първо extract_questions.py")
            return []
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Грешка", f"Неуспешно зареждане на въпросите: {e}")
            return []

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Colors
        self.BG_COLOR = "#F4F6F9"
        self.PRIMARY_COLOR = "#2C3E50"
        self.ACCENT_COLOR = "#2980B9"
        self.SUCCESS_COLOR = "#27AE60"
        self.DANGER_COLOR = "#C0392B"

        self.root.configure(bg=self.BG_COLOR)

        # Fonts
        self.title_font = font.Font(family="Segoe UI", size=18, weight="bold")
        self.header_font = font.Font(family="Segoe UI", size=13, weight="bold")
        self.question_font = font.Font(family="Segoe UI", size=12)
        self.option_font = font.Font(family="Segoe UI", size=11)

        # TTK Style overrides
        self.style.configure("TFrame", background=self.BG_COLOR)
        self.style.configure("Header.TLabel", background=self.BG_COLOR, foreground=self.PRIMARY_COLOR, font=self.title_font)
        self.style.configure("SubHeader.TLabel", background=self.BG_COLOR, foreground="#555555", font=self.option_font)
        self.style.configure("Badge.TLabel", background=self.ACCENT_COLOR, foreground="white", font=font.Font(size=10, weight="bold"), padding=5)

        self.style.configure("Primary.TButton", font=font.Font(size=11, weight="bold"), background=self.ACCENT_COLOR, foreground="white")
        self.style.map("Primary.TButton", background=[("active", "#1F618D")])

        self.style.configure("Success.TButton", font=font.Font(size=11, weight="bold"), background=self.SUCCESS_COLOR, foreground="white")
        self.style.map("Success.TButton", background=[("active", "#1E8449")])

        self.style.configure("Nav.TButton", font=self.option_font)
        self.style.configure("Flag.TButton", font=self.option_font)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ==================== MAIN MENU ====================
    def show_main_menu(self):
        self.clear_container()
        self.timer_running = False

        # Main Title
        title_lbl = ttk.Label(self.container, text="Изпитна система за радиолюбители (Клас 2)", style="Header.TLabel")
        title_lbl.pack(pady=(10, 5))

        sub_lbl = ttk.Label(self.container, text="Подготовка за изпит пред Комисия за регулиране на съобщенията (КРС)", style="SubHeader.TLabel")
        sub_lbl.pack(pady=(0, 20))

        # Info Card Frame
        info_frame = tk.Frame(self.container, bg="white", bd=1, relief=tk.RIDGE, padx=20, pady=15)
        info_frame.pack(fill=tk.X, pady=10)

        info_text = (
            "📌 Изисквания за официалния изпит:\n"
            "   • Изпитът съдържа 60 въпроса (28 от Раздел 1, 13 от Раздел 2, 19 от Раздел 3).\n"
            "   • За успешно полагане са необходими минимум 80% верни отговора (поне 48 верни от 60).\n"
            "   • Всички верни отговори са скрити, а вариантите на отговор се разбъркват.\n"
            "   • След предаване на теста получавате детайлен преглед на грешките."
        )
        tk.Label(info_frame, text=info_text, bg="white", fg="#222222", font=self.option_font, justify=tk.LEFT).pack(anchor="w")

        # Test Mode Selection Frame
        mode_frame = tk.LabelFrame(self.container, text=" Изберете режим на теста ", bg=self.BG_COLOR, font=self.header_font, padx=20, pady=15)
        mode_frame.pack(fill=tk.X, pady=20)

        self.selected_mode = tk.StringVar(value="official_60")

        modes = [
            ("official_60", "🏆 Официален симулиран изпит (60 въпроса - 80% за преминаване)", "28 от Раздел 1, 13 от Раздел 2, 19 от Раздел 3"),
            ("razdel_1", "📘 Раздел 1: Електротехника и радиотехника (111 въпроса)", "Всички въпроси от Раздел 1"),
            ("razdel_2", "📗 Раздел 2: Кодове, правила и процедури (53 въпроса)", "Всички въпроси от Раздел 2"),
            ("razdel_3", "📙 Раздел 3: Нормативна уредба (73 въпроса)", "Всички въпроси от Раздел 3"),
            ("all_questions", "📚 Пълен конспект (Всички 237 въпроса)", "Всички налични въпроси от трите раздела")
        ]

        for val, label_text, desc in modes:
            r_frame = tk.Frame(mode_frame, bg=self.BG_COLOR)
            r_frame.pack(fill=tk.X, pady=5)

            rb = tk.Radiobutton(r_frame, text=label_text, value=val, variable=self.selected_mode,
                                font=font.Font(family="Segoe UI", size=11, weight="bold"),
                                bg=self.BG_COLOR, activebackground=self.BG_COLOR, selectcolor=self.BG_COLOR)
            rb.pack(anchor="w")

            desc_lbl = tk.Label(r_frame, text=f"   {desc}", font=font.Font(size=9), fg="#666666", bg=self.BG_COLOR)
            desc_lbl.pack(anchor="w")

        # Start Button Frame
        btn_frame = ttk.Frame(self.container)
        btn_frame.pack(pady=20)

        start_btn = ttk.Button(btn_frame, text="🚀 ЗАПОЧНИ ТЕСТА", style="Primary.TButton", command=self.start_test)
        start_btn.pack(ipadx=20, ipady=8)

    def prepare_question(self, q):
        q_copy = dict(q)
        keep_original_order = (q.get('razdel'), q.get('q_num')) in {
            (2, 24), (2, 25), (2, 45), (2, 53), (3, 3), (3, 23), (3, 49), (3, 63), (3, 67)
        }
        if not keep_original_order and not q.get('has_image') and q.get('options'):
            orig_opts = q['options']
            keys = ['А', 'Б', 'В', 'Г']
            avail_keys = [k for k in keys if k in orig_opts]
            vals = [orig_opts[k] for k in avail_keys]
            correct_val = orig_opts.get(q['correct_answer'])

            shuffled_vals = list(vals)
            random.shuffle(shuffled_vals)

            new_options = {}
            new_correct_ans = q['correct_answer']
            for k, v in zip(avail_keys, shuffled_vals):
                new_options[k] = v
                if v == correct_val:
                    new_correct_ans = k

            q_copy['options'] = new_options
            q_copy['correct_answer'] = new_correct_ans
        return q_copy

    # ==================== START TEST ====================
    def start_test(self):
        mode = self.selected_mode.get()
        all_q = self.questions_data

        if not all_q:
            messagebox.showerror("Грешка", "Няма заредени въпроси!")
            return

        if mode == "official_60":
            r1 = [q for q in all_q if q['razdel'] == 1]
            r2 = [q for q in all_q if q['razdel'] == 2]
            r3 = [q for q in all_q if q['razdel'] == 3]

            q1 = random.sample(r1, min(28, len(r1)))
            q2 = random.sample(r2, min(13, len(r2)))
            q3 = random.sample(r3, min(19, len(r3)))

            selected = q1 + q2 + q3
            random.shuffle(selected)
            self.test_questions = [self.prepare_question(q) for q in selected]
        elif mode == "razdel_1":
            selected = [q for q in all_q if q['razdel'] == 1]
            random.shuffle(selected)
            self.test_questions = [self.prepare_question(q) for q in selected]
        elif mode == "razdel_2":
            selected = [q for q in all_q if q['razdel'] == 2]
            random.shuffle(selected)
            self.test_questions = [self.prepare_question(q) for q in selected]
        elif mode == "razdel_3":
            selected = [q for q in all_q if q['razdel'] == 3]
            random.shuffle(selected)
            self.test_questions = [self.prepare_question(q) for q in selected]
        else: # all_questions
            selected = list(all_q)
            random.shuffle(selected)
            self.test_questions = [self.prepare_question(q) for q in selected]

        self.user_answers = {}
        self.flagged_questions = set()
        self.current_q_index = 0
        self.start_time = time.time()
        self.timer_running = True
        self.is_review_mode = False
        self.review_only_wrong = False
        self.review_indices = []
        self.review_pos = 0

        self.build_test_ui()
        self.update_question_display()
        self.update_timer()

    # ==================== TEST UI ====================
    def build_test_ui(self):
        self.clear_container()

        # Top Bar: Header info & Timer & Submit button
        top_bar = tk.Frame(self.container, bg=self.PRIMARY_COLOR, padx=15, pady=10)
        top_bar.pack(fill=tk.X)

        self.q_progress_lbl = tk.Label(top_bar, text="Въпрос 1 от 80", font=font.Font(family="Segoe UI", size=12, weight="bold"), fg="white", bg=self.PRIMARY_COLOR)
        self.q_progress_lbl.pack(side=tk.LEFT)

        self.timer_lbl = tk.Label(top_bar, text="⏱ 00:00", font=font.Font(family="Segoe UI", size=12, weight="bold"), fg="#F1C40F", bg=self.PRIMARY_COLOR)
        self.timer_lbl.pack(side=tk.LEFT, padx=30)

        submit_btn = tk.Button(top_bar, text="Предай теста", font=font.Font(size=10, weight="bold"), bg=self.SUCCESS_COLOR, fg="white", activebackground="#1E8449", activeforeground="white", command=self.confirm_submit)
        submit_btn.pack(side=tk.RIGHT)

        # Question Section Badge & Title
        self.section_lbl = tk.Label(self.container, text="", font=font.Font(size=10, weight="bold"), fg=self.ACCENT_COLOR, bg=self.BG_COLOR, anchor="w")
        self.section_lbl.pack(fill=tk.X, pady=(10, 5))

        # Question Text Area Frame
        q_frame = tk.Frame(self.container, bg="white", bd=1, relief=tk.RIDGE, padx=15, pady=15)
        q_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Scrollable Question Canvas/Frame
        self.q_text_lbl = tk.Label(q_frame, text="", font=self.question_font, bg="white", fg="#111111", justify=tk.LEFT, wraplength=800)
        self.q_text_lbl.pack(anchor="w", pady=(0, 10))

        # Image Display Label
        self.img_lbl = tk.Label(q_frame, bg="white")
        self.img_lbl.pack(anchor="w", pady=5)

        # Options Frame
        self.options_frame = tk.Frame(q_frame, bg="white")
        self.options_frame.pack(fill=tk.X, pady=10)

        self.selected_opt_var = tk.StringVar(value="")

        self.opt_widgets = {}
        for opt_key in ['А', 'Б', 'В', 'Г']:
            opt_btn_frame = tk.Frame(self.options_frame, bg="white", padx=4, pady=2)
            opt_btn_frame.pack(fill=tk.X, pady=2)

            rb = tk.Radiobutton(
                opt_btn_frame,
                text="",
                value=opt_key,
                variable=self.selected_opt_var,
                font=self.option_font,
                bg="#F8F9F9",
                activebackground="#EAECEE",
                selectcolor="#F8F9F9",
                wraplength=750,
                justify=tk.LEFT,
                command=self.on_option_selected
            )
            rb.pack(anchor="w", fill=tk.X)

            # Bind frame click to radio button select
            opt_btn_frame.bind("<Button-1>", lambda e, k=opt_key: self.select_option_by_key(k))

            self.opt_widgets[opt_key] = {
                'frame': opt_btn_frame,
                'rb': rb
            }

        # Bottom Bar Controls
        bottom_bar = tk.Frame(self.container, bg=self.BG_COLOR, pady=10)
        bottom_bar.pack(fill=tk.X)

        self.prev_btn = ttk.Button(bottom_bar, text="◄ Предишен", style="Nav.TButton", command=self.prev_question)
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.flag_btn = ttk.Button(bottom_bar, text="🚩 Маркирай", style="Flag.TButton", command=self.toggle_flag)
        self.flag_btn.pack(side=tk.LEFT, padx=5)

        self.grid_btn = ttk.Button(bottom_bar, text="📊 Карта на въпросите", style="Nav.TButton", command=self.show_question_grid_modal)
        self.grid_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = ttk.Button(bottom_bar, text="Следващ ►", style="Nav.TButton", command=self.next_question)
        self.next_btn.pack(side=tk.RIGHT, padx=5)

    def select_option_by_key(self, opt_key):
        if self.is_review_mode:
            return
        self.selected_opt_var.set(opt_key)
        self.on_option_selected()

    def on_option_selected(self):
        if self.is_review_mode:
            return
        ans = self.selected_opt_var.get()
        if ans:
            self.user_answers[self.current_q_index] = ans
            self.highlight_selected_option()

    def highlight_selected_option(self):
        ans = self.selected_opt_var.get()
        for k, w in self.opt_widgets.items():
            if k == ans:
                w['frame'].configure(bg="#E8F8F5", highlightbackground=self.ACCENT_COLOR, highlightthickness=1)
                w['rb'].configure(bg="#E8F8F5", activebackground="#E8F8F5")
            else:
                w['frame'].configure(bg="#F8F9F9", highlightthickness=0)
                w['rb'].configure(bg="#F8F9F9", activebackground="#EAECEE")

    def update_question_display(self):
        if not self.test_questions:
            return

        q = self.test_questions[self.current_q_index]
        total_q = len(self.test_questions)

        # Progress header
        if self.is_review_mode and self.review_only_wrong:
            total_wrong = len(self.review_indices)
            self.q_progress_lbl.config(text=f"Грешен въпрос {self.review_pos + 1} от {total_wrong} (Въпрос #{self.current_q_index + 1})")
        else:
            self.q_progress_lbl.config(text=f"Въпрос {self.current_q_index + 1} от {total_q}")

        self.section_lbl.config(text=f"📌 {q['razdel_title']} — Въпрос №{q['q_num']}")

        # Question text
        # Diagram crops contain the complete question and answer figures.
        if q.get('has_image'):
            self.q_text_lbl.pack_forget()
        else:
            self.q_text_lbl.config(text=f"{self.current_q_index + 1}. {q['question']}")
            self.q_text_lbl.pack(anchor="w", pady=(0, 10))

        # Native Tkinter PhotoImage for PNG
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), q.get('image_path', ''))
        if q.get('has_image') and q.get('image_path') and os.path.exists(image_path):
            try:
                self.current_image = tk.PhotoImage(file=image_path)
                self.img_lbl.config(image=self.current_image)
                self.img_lbl.pack(anchor="w", pady=5)
            except Exception as e:
                print(f"Error loading image: {e}")
                self.img_lbl.pack_forget()
        else:
            self.img_lbl.pack_forget()

        # Saved answer
        saved_ans = self.user_answers.get(self.current_q_index, "")
        self.selected_opt_var.set(saved_ans)

        # Populate options
        opts = q.get('options', {})
        for opt_key in ['А', 'Б', 'В', 'Г']:
            w = self.opt_widgets[opt_key]
            if opt_key in opts and opts[opt_key]:
                w['rb'].config(text=f"{opt_key}. {opts[opt_key]}", state=tk.NORMAL if not self.is_review_mode else tk.DISABLED)
                w['frame'].pack(fill=tk.X, pady=4)
            elif q.get('has_image'):
                # For diagram options without text
                w['rb'].config(text=f"Символ {opt_key}", state=tk.NORMAL if not self.is_review_mode else tk.DISABLED)
                w['frame'].pack(fill=tk.X, pady=4)
            else:
                w['frame'].pack_forget()

        # Review mode visual feedback
        if self.is_review_mode:
            correct_ans = q['correct_answer']
            user_ans = saved_ans

            for opt_key in ['А', 'Б', 'В', 'Г']:
                w = self.opt_widgets[opt_key]
                if opt_key == correct_ans:
                    w['frame'].configure(bg="#D4EFDF", highlightbackground=self.SUCCESS_COLOR, highlightthickness=2)
                    w['rb'].configure(bg="#D4EFDF", text=f"✔ {w['rb'].cget('text')}")
                elif opt_key == user_ans and user_ans != correct_ans:
                    w['frame'].configure(bg="#FADBD8", highlightbackground=self.DANGER_COLOR, highlightthickness=2)
                    w['rb'].configure(bg="#FADBD8", text=f"✖ {w['rb'].cget('text')}")
                else:
                    w['frame'].configure(bg="#F8F9F9", highlightthickness=0)
                    w['rb'].configure(bg="#F8F9F9")
        else:
            self.highlight_selected_option()

        # Update flag button
        if self.current_q_index in self.flagged_questions:
            self.flag_btn.config(text="🚩 Маркиран", style="Flag.TButton")
        else:
            self.flag_btn.config(text="🏳 Маркирай", style="Flag.TButton")

        # Enable/Disable Prev / Next
        if self.is_review_mode and self.review_only_wrong:
            self.prev_btn.config(state=tk.NORMAL if self.review_pos > 0 else tk.DISABLED)
            if self.review_pos == len(self.review_indices) - 1:
                self.next_btn.config(text="Затвори прегледа 🏁")
            else:
                self.next_btn.config(text="Следващ ►")
        elif self.is_review_mode:
            self.prev_btn.config(state=tk.NORMAL if self.current_q_index > 0 else tk.DISABLED)
            if self.current_q_index == total_q - 1:
                self.next_btn.config(text="Затвори прегледа 🏁")
            else:
                self.next_btn.config(text="Следващ ►")
        else:
            self.prev_btn.config(state=tk.NORMAL if self.current_q_index > 0 else tk.DISABLED)
            if self.current_q_index == total_q - 1:
                self.next_btn.config(text="Предай 🏁")
            else:
                self.next_btn.config(text="Следващ ►")

    def prev_question(self):
        if self.is_review_mode and self.review_only_wrong:
            if self.review_pos > 0:
                self.review_pos -= 1
                self.current_q_index = self.review_indices[self.review_pos]
                self.update_question_display()
        else:
            if self.current_q_index > 0:
                self.current_q_index -= 1
                self.update_question_display()

    def next_question(self):
        if self.is_review_mode and self.review_only_wrong:
            if self.review_pos < len(self.review_indices) - 1:
                self.review_pos += 1
                self.current_q_index = self.review_indices[self.review_pos]
                self.update_question_display()
            else:
                self.show_results()
        elif self.is_review_mode:
            if self.current_q_index < len(self.test_questions) - 1:
                self.current_q_index += 1
                self.update_question_display()
            else:
                self.show_results()
        else:
            if self.current_q_index < len(self.test_questions) - 1:
                self.current_q_index += 1
                self.update_question_display()
            else:
                self.confirm_submit()

    def toggle_flag(self):
        if self.current_q_index in self.flagged_questions:
            self.flagged_questions.remove(self.current_q_index)
        else:
            self.flagged_questions.add(self.current_q_index)
        self.update_question_display()

    def update_timer(self):
        if not self.timer_running:
            return
        self.elapsed_time = int(time.time() - self.start_time)
        mins = self.elapsed_time // 60
        secs = self.elapsed_time % 60
        self.timer_lbl.config(text=f"⏱ {mins:02d}:{secs:02d}")
        self.root.after(1000, self.update_timer)

    # ==================== QUESTION NAVIGATION GRID ====================
    def show_question_grid_modal(self):
        modal = tk.Toplevel(self.root)
        modal.title("Карта на въпросите")
        modal.geometry("550x450")
        modal.transient(self.root)
        modal.grab_set()

        top_lbl = tk.Label(modal, text="Преглед на въпросите и състояние", font=self.header_font, pady=10)
        top_lbl.pack()

        # Legend
        leg_frame = tk.Frame(modal, pady=5)
        leg_frame.pack()

        if self.is_review_mode:
            tk.Label(leg_frame, text="■ Верен", bg="#27AE60", fg="white", padx=5).pack(side=tk.LEFT, padx=5)
            tk.Label(leg_frame, text="■ Грешен", bg="#C0392B", fg="white", padx=5).pack(side=tk.LEFT, padx=5)
            tk.Label(leg_frame, text="■ Пропуснат", bg="#7F8C8D", fg="white", padx=5).pack(side=tk.LEFT, padx=5)
        else:
            tk.Label(leg_frame, text="■ Отговорен", bg="#27AE60", fg="white", padx=5).pack(side=tk.LEFT, padx=5)
            tk.Label(leg_frame, text="■ Неотговорен", bg="#EAECEE", fg="#333333", padx=5).pack(side=tk.LEFT, padx=5)
            tk.Label(leg_frame, text="■ Маркиран", bg="#F39C12", fg="white", padx=5).pack(side=tk.LEFT, padx=5)

        # Grid canvas frame
        canvas_frame = tk.Frame(modal)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        canvas = tk.Canvas(canvas_frame, bg="white")
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        indices_to_show = self.review_indices if (self.is_review_mode and self.review_only_wrong) else list(range(len(self.test_questions)))

        cols = 8
        for i_pos, idx in enumerate(indices_to_show):
            row = i_pos // cols
            col = i_pos % cols
            q = self.test_questions[idx]

            if self.is_review_mode:
                u_ans = self.user_answers.get(idx)
                if u_ans == q['correct_answer']:
                    bg_c = "#27AE60"
                    fg_c = "white"
                elif u_ans is not None:
                    bg_c = "#C0392B"
                    fg_c = "white"
                else:
                    bg_c = "#7F8C8D"
                    fg_c = "white"
            else:
                is_ans = idx in self.user_answers
                is_flag = idx in self.flagged_questions
                bg_c = "#27AE60" if is_ans else "#EAECEE"
                fg_c = "white" if is_ans else "#333333"
                if is_flag:
                    bg_c = "#F39C12"
                    fg_c = "white"

            is_curr = idx == self.current_q_index
            border_w = 2 if is_curr else 1
            border_c = "#2980B9" if is_curr else "#CCCCCC"

            btn = tk.Button(
                scrollable_frame,
                text=f"{idx+1}",
                bg=bg_c,
                fg=fg_c,
                font=font.Font(size=9, weight="bold"),
                width=5,
                height=2,
                relief=tk.SOLID,
                bd=border_w,
                command=lambda i=idx: [self.jump_to_question(i), modal.destroy()]
            )
            btn.grid(row=row, column=col, padx=4, pady=4)

    def jump_to_question(self, index):
        self.current_q_index = index
        if self.is_review_mode and self.review_only_wrong and index in self.review_indices:
            self.review_pos = self.review_indices.index(index)
        self.update_question_display()

    # ==================== SUBMIT & RESULTS ====================
    def confirm_submit(self):
        if self.is_review_mode:
            self.show_main_menu()
            return

        unanswered = len(self.test_questions) - len(self.user_answers)
        msg = "Сигурни ли сте, че искате да предадете теста?"
        if unanswered > 0:
            msg = f"Имате {unanswered} неотговорени въпроса!\n" + msg

        if messagebox.askyesno("Предаване на тест", msg):
            self.timer_running = False
            self.show_results()

    def show_results(self):
        self.clear_container()

        total_q = len(self.test_questions)
        correct_count = 0

        for idx, q in enumerate(self.test_questions):
            u_ans = self.user_answers.get(idx)
            if u_ans and u_ans == q['correct_answer']:
                correct_count += 1

        pct = (correct_count / total_q) * 100 if total_q > 0 else 0
        passed = pct >= 80.0

        # Result Header Banner
        banner_bg = self.SUCCESS_COLOR if passed else self.DANGER_COLOR
        status_text = "ПОЛОЖЕН ИЗПИТ! (PASS)" if passed else "НЕПОЛОЖЕН ИЗПИТ (FAIL)"

        banner = tk.Frame(self.container, bg=banner_bg, pady=20, padx=20)
        banner.pack(fill=tk.X, pady=(0, 20))

        status_lbl = tk.Label(banner, text=status_text, font=font.Font(family="Segoe UI", size=22, weight="bold"), fg="white", bg=banner_bg)
        status_lbl.pack()

        sub_text = f"Резултат: {correct_count} от {total_q} верни отговора ({pct:.1f}%)"
        sub_lbl = tk.Label(banner, text=sub_text, font=font.Font(family="Segoe UI", size=14), fg="white", bg=banner_bg)
        sub_lbl.pack(pady=(5, 0))

        # Detailed Stats Card
        stats_card = tk.Frame(self.container, bg="white", bd=1, relief=tk.RIDGE, padx=20, pady=15)
        stats_card.pack(fill=tk.X, pady=10)

        mins = self.elapsed_time // 60
        secs = self.elapsed_time % 60
        time_str = f"{mins:02d}:{secs:02d}"

        req_text = f"Минимум за преминаване: 80% верни отговора ({int(total_q * 0.8)} от {total_q})"

        stats_info = (
            f"📊 Детайли от изпита:\n\n"
            f"  • Верни отговори: {correct_count}\n"
            f"  • Грешни отговори: {len(self.user_answers) - correct_count}\n"
            f"  • Неотговорени: {total_q - len(self.user_answers)}\n"
            f"  • Изминало време: {time_str}\n"
            f"  • {req_text}"
        )

        tk.Label(stats_card, text=stats_info, font=self.option_font, bg="white", justify=tk.LEFT).pack(anchor="w")

        # Action buttons frame
        act_frame = ttk.Frame(self.container)
        act_frame.pack(pady=25)

        rev_all_btn = ttk.Button(act_frame, text="🔍 Преглед на всички въпроси", style="Nav.TButton", command=lambda: self.enter_review_mode(only_wrong=False))
        rev_all_btn.pack(side=tk.LEFT, padx=5, ipadx=5, ipady=5)

        rev_wrong_btn = ttk.Button(act_frame, text="❌ Преглед само на грешките", style="Primary.TButton", command=lambda: self.enter_review_mode(only_wrong=True))
        rev_wrong_btn.pack(side=tk.LEFT, padx=5, ipadx=5, ipady=5)

        new_btn = ttk.Button(act_frame, text="🔄 Нов тест", style="Success.TButton", command=self.show_main_menu)
        new_btn.pack(side=tk.LEFT, padx=5, ipadx=5, ipady=5)

    def enter_review_mode(self, only_wrong=False):
        if only_wrong:
            wrong_indices = [idx for idx, q in enumerate(self.test_questions) if self.user_answers.get(idx) != q['correct_answer']]
            if not wrong_indices:
                messagebox.showinfo("Информация", "Поздравления! Нямате сбъркани въпроси.")
                return
            self.is_review_mode = True
            self.review_only_wrong = True
            self.review_indices = wrong_indices
            self.review_pos = 0
            self.current_q_index = self.review_indices[0]
        else:
            self.is_review_mode = True
            self.review_only_wrong = False
            self.review_indices = list(range(len(self.test_questions)))
            self.review_pos = 0
            self.current_q_index = 0

        self.build_test_ui()
        self.update_question_display()

def main():
    root = tk.Tk()
    app = HamRadioTestApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
