from tkinter import *
from tkinter import messagebox
import random

# Define colors and styles for a cleaner UI
BG_COLOR = "#0c0e1b"
PRIMARY_COLOR = "#4CAF50"
SECONDARY_COLOR = "#0c0e1b"
TEXT_COLOR = "#333333"
FONT = ("Helvetica", 12)
HEADER_FONT = ("Helvetica", 16, "bold")

class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Quiz App")
        self.master.geometry("800x500")
        self.master.configure(bg=BG_COLOR)

        self.questions = []
        self.answers = []
        self.qa_pairs = []
        self.current_qa_index = -1
        self.score = 0
        self.total_questions_asked = 0
        self.time_limit = None
        self.flashcard_mode = True

        self.load_data()
        self.create_main_menu()

    def load_data(self):
        try:
            with open("questions", "r") as qf:
                self.questions = [q.strip() for q in qf.readlines()]
            with open("answers", "r") as af:
                self.answers = [a.strip() for a in af.readlines()]
            assert len(self.questions) == len(self.answers)
            self.qa_pairs = list(zip(self.questions, self.answers))
        except:
            messagebox.showerror("Error", "Check 'questions' and 'answers' files.")
            self.master.destroy()

    def create_main_menu(self):
        self.main_frame = Frame(self.master, bg=BG_COLOR)
        self.main_frame.pack(expand=True, fill=BOTH)

        Label(self.main_frame, text="Welcome to the Quiz App", font=HEADER_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)

        # Mode selection
        Label(self.main_frame, text="Choose Mode:", font=FONT, bg=BG_COLOR).pack()
        self.mode_var = StringVar(value="flashcard")
        for text, val in [("Flashcards", "flashcard"), ("Multiple Choice", "multiple_choice")]:
            Radiobutton(self.main_frame, text=text, variable=self.mode_var, value=val,
                        font=FONT, bg=BG_COLOR, selectcolor=SECONDARY_COLOR).pack()

        # Flip option
        self.flip_var = BooleanVar()
        Checkbutton(self.main_frame, text="Flip Q/A", variable=self.flip_var,
                    font=FONT, bg=BG_COLOR).pack(pady=10)

        # Difficulty
        Label(self.main_frame, text="Select Difficulty:", font=FONT, bg=BG_COLOR).pack()
        self.difficulty_var = StringVar(value="unlimited")
        for text, val in [("Easy (10s)", "easy"), ("Hard (5s)", "hard"), ("Unlimited", "unlimited")]:
            Radiobutton(self.main_frame, text=text, variable=self.difficulty_var, value=val,
                        font=FONT, bg=BG_COLOR, selectcolor=SECONDARY_COLOR).pack()

        Button(self.main_frame, text="Start", font=FONT, bg=PRIMARY_COLOR, fg=SECONDARY_COLOR,
               command=self.start_quiz).pack(pady=20)

    def restart_quiz(self):
        if hasattr(self, 'timer_id'):
            self.master.after_cancel(self.timer_id)
        self.quiz_frame.pack_forget()
        self.create_main_menu()

    def start_quiz(self):
        self.set_difficulty()
        self.score = 0
        self.total_questions_asked = 0

        if self.flip_var.get():
            self.qa_pairs = [(b, a) for a, b in zip(self.questions, self.answers)]
        else:
            self.qa_pairs = list(zip(self.questions, self.answers))
        random.shuffle(self.qa_pairs)

        self.main_frame.pack_forget()
        self.create_quiz_ui()
        self.next_question()

    def set_difficulty(self):
        levels = {"easy": 10, "hard": 5, "unlimited": None}
        self.time_limit = levels[self.difficulty_var.get()]

    def create_quiz_ui(self):
        self.quiz_frame = Frame(self.master, bg=BG_COLOR)
        self.quiz_frame.pack(expand=True, fill=BOTH)

        self.question_label = Label(self.quiz_frame, text="", font=HEADER_FONT, wraplength=700, bg=BG_COLOR)
        self.question_label.pack(pady=20)

        self.answer_entry = Entry(
            self.quiz_frame,
            font=FONT,
            fg=TEXT_COLOR,
            bg="white",
            insertbackground=TEXT_COLOR,
            relief="solid",          # gives it a visible border
            bd=2,                    # border width
            highlightthickness=1,    # optional: shows border even when unfocused
            highlightbackground="#cccccc",  # border color when unfocused
            highlightcolor=PRIMARY_COLOR    # border color when focused
        )
        self.answer_entry.pack(pady=10)

        self.submit_btn = Button(self.quiz_frame, text="Submit", font=FONT, command=self.check_answer)
        self.submit_btn.pack(pady=5)

        self.show_answer_btn = Button(self.quiz_frame, text="Show Answer", font=FONT, command=self.show_answer)
        self.show_answer_btn.pack(pady=5)

        self.mc_buttons = []
        self.mc_frame = Frame(self.quiz_frame, bg=BG_COLOR)
        for i in range(4):
            btn = Button(self.mc_frame, text="", font=FONT, width=50,
                         command=lambda i=i: self.check_multiple_choice(i))
            btn.pack(pady=5)
            self.mc_buttons.append(btn)

        self.result_label = Label(self.quiz_frame, text="", font=FONT, bg=BG_COLOR)
        self.result_label.pack(pady=10)

        self.score_label = Label(self.quiz_frame, text="Score: 0/0", font=FONT, bg=BG_COLOR)
        self.score_label.pack()

        self.timer_label = Label(self.quiz_frame, text="", font=FONT, bg=BG_COLOR)
        self.timer_label.pack(pady=10)

        self.next_button = Button(self.quiz_frame, text="Next", font=FONT, command=self.next_question)
        self.next_button.pack(pady=10)

        self.restart_btn = Button(self.quiz_frame, text="Restart", font=FONT, bg="red", command=self.restart_quiz)
        self.restart_btn.pack(pady=10)

    def next_question(self):
        self.result_label.config(text="")
        self.answer_entry.config(state=NORMAL)
        self.submit_btn.config(state=NORMAL)
        self.show_answer_btn.config(state=NORMAL)
        self.answer_entry.delete(0, END)
        self.timer_label.config(text="")

        if hasattr(self, 'timer_id'):
            self.master.after_cancel(self.timer_id)

        if not self.qa_pairs:
            messagebox.showinfo("Quiz Completed", f"Score: {self.score}/{self.total_questions_asked}")
            self.quiz_frame.pack_forget()
            self.create_main_menu()
            return

        self.current_qa_index = (self.current_qa_index + 1) % len(self.qa_pairs)
        q, a = self.qa_pairs[self.current_qa_index]
        self.current_answer = a
        self.question_label.config(text=q)
        self.total_questions_asked += 1
        self.score_label.config(text=f"Score: {self.score}/{self.total_questions_asked}")

        if self.mode_var.get() == "flashcard":
            self.answer_entry.pack()
            self.submit_btn.pack()
            self.show_answer_btn.pack()
            self.mc_frame.pack_forget()
        else:
            self.answer_entry.pack_forget()
            self.submit_btn.pack_forget()
            self.show_answer_btn.pack_forget()
            self.mc_frame.pack()
            self.prepare_mc_options()

        if self.time_limit:
            self.run_timer(self.time_limit)

    def check_answer(self):
        user_answer = self.answer_entry.get().strip()
        correct = self.current_answer.strip()
        self.master.after_cancel(self.timer_id) if hasattr(self, 'timer_id') else None
        if user_answer.casefold() == correct.casefold():
            self.result_label.config(text="Correct!", fg="green")
            self.score += 1
        else:
            self.result_label.config(text=f"Wrong. Correct: {correct}", fg="red")
        self.answer_entry.config(state=DISABLED)
        self.submit_btn.config(state=DISABLED)
        self.show_answer_btn.config(state=DISABLED)

    def show_answer(self):
        self.result_label.config(text=f"Answer: {self.current_answer}", fg="blue")
        self.master.after_cancel(self.timer_id) if hasattr(self, 'timer_id') else None
        self.answer_entry.config(state=DISABLED)
        self.submit_btn.config(state=DISABLED)
        self.show_answer_btn.config(state=DISABLED)

    def prepare_mc_options(self):
        options = [self.current_answer] + random.sample(
            [a for q, a in self.qa_pairs if a != self.current_answer], k=min(3, len(self.qa_pairs) - 1))
        random.shuffle(options)
        for i, opt in enumerate(options):
            self.mc_buttons[i].config(text=opt, state=NORMAL)

    def check_multiple_choice(self, idx):
        selected = self.mc_buttons[idx].cget("text")
        correct = self.current_answer
        self.master.after_cancel(self.timer_id) if hasattr(self, 'timer_id') else None
        if selected.casefold() == correct.casefold():
            self.result_label.config(text="Correct!", fg="green")
            self.score += 1
        else:
            self.result_label.config(text=f"Wrong. Correct: {correct}", fg="red")
        for btn in self.mc_buttons:
            btn.config(state=DISABLED)

    def run_timer(self, time_left):
        self.timer_label.config(text=f"Time: {time_left}s")
        if time_left > 0:
            self.timer_id = self.master.after(1000, self.run_timer, time_left - 1)
        else:
            self.result_label.config(text=f"Time's up! Answer: {self.current_answer}", fg="orange")
            if self.mode_var.get() == "flashcard":
                self.answer_entry.config(state=DISABLED)
                self.submit_btn.config(state=DISABLED)
                self.show_answer_btn.config(state=DISABLED)
            else:
                for btn in self.mc_buttons:
                    btn.config(state=DISABLED)


root = Tk()
app = QuizApp(root)
root.mainloop()

