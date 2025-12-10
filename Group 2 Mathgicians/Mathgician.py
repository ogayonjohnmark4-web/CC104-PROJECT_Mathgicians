import tkinter as tk
from PIL import Image, ImageTk
import random
import pygame

# ---------------- MULTIPLE CHOICE GENERATOR ----------------
def generate_choices(correct):
    choices = [correct]
    while len(choices) < 4:
        wrong = random.randint(correct - 20, correct + 20)
        if wrong != correct and wrong not in choices:
            choices.append(wrong)
    random.shuffle(choices)
    return choices
# ------------------------------------------------------------

easy = {
    64: "8 × 8",
    58: "23 + 35",
    85: "425 ÷ 5",
    287: "137 + 150",
    63: "7 × 9",
    17: "85 ÷ 5",
    96: "8 × 12",
    221: "56 + 165",
    790: "1650 - 860",
    420: "456 - 36"
}

hard_questions = [
    "( 8 + 4 * 3 )",
    "( (6 + 2) * 5 )",
    "( 12 / (3 * 2) )",
    "( 7 + 2^3 * 2 )",
    "( (18 - 6) * 3 + 4 )",
    "( 5 * (9 - 4)^2 )",
    "( 30 / 5 + 6 * 2 )",
    "( (10 + 2) / (4 - 2) * 3 )",
    "( 16 - 2 (3^2 - 5) )",
    "( (8 / 2) * (6 - 1)^2 )"
]

hard_answers = [20, 40, 2, 23, 40, 125, 18, 18, 8, 100]

class Mongmama:
    def __init__(self):
        self.high_score = 0
        self.score = 0
        self.lives = 3
        self.current_question_index = 0
        self.questions = []

        # Initialize main window
        self.window = tk.Tk()
        self.window.title("Mathgicians")

        # Full screen using screen width/height
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        self.window.geometry(f"{screen_w}x{screen_h}+0+0")

        # Background image
        bg_image = Image.open("Matatics.png")
        self.bg_image = bg_image.resize((screen_w, screen_h))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        background_label = tk.Label(self.window, image=self.bg_photo)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Center frame
        self.center_frame = tk.Frame(self.window, bg="white")
        self.center_frame.pack(expand=True)

        # Sound
        pygame.mixer.init()
        pygame.mixer.music.load("BG.MP3")
        pygame.mixer.music.play(loops=-1)
        self.correct_sound = pygame.mixer.Sound("correct.mp3")
        self.wrong_sound = pygame.mixer.Sound("FAHH Sound Effect.mp3")
        self.bg_volume = 0.5
        pygame.mixer.music.set_volume(self.bg_volume)

        # Title
        self.quest_label = tk.Label(self.center_frame, text="Mathgicians",
                                    font=("Papyrus", 70, "bold"), bg="white")
        self.quest_label.pack(pady=10)

        # Start buttons
        self.start_button = tk.Button(self.center_frame, text="Start",
                                      font=("Comic Sans MS", 40),
                                      command=self.show_difficulty)
        self.start_button.pack()
        self.easy_button = tk.Button(self.center_frame, text="Easy",
                                     font=("Comic Sans MS", 35),
                                     command=lambda: self.select_difficulty("easy"))
        self.hard_button = tk.Button(self.center_frame, text="Hard",
                                     font=("Comic Sans MS", 35),
                                     command=lambda: self.select_difficulty("hard"))

        # HUD: High score top-left, Lives top-right (hidden initially)
        self.high_score_label = tk.Label(self.window,
                                         text=f"High Score: {self.load_high_score()}",
                                         font=("Comic Sans MS", 40), bg="white")
        self.high_score_label.place(x=20, y=20)
        self.lives_text_label = tk.Label(self.window,
                                         text="❤❤❤",
                                         font=("Arial Black", 45), bg="white", fg="#d00000")
        self.lives_text_label.place_forget()  # hide initially

        # Center stack: question number → question → score → result
        self.question_number = tk.Label(self.center_frame, text="", font=("Impact", 32), bg="white")
        self.question_label = tk.Label(self.center_frame, text="", font=("Comic Sans MS", 40, "bold"),
                                       bg="white", pady=20)
        self.score_label = tk.Label(self.center_frame, text=f"Score: {self.score}", font=("Arial Black", 30), bg="white")
        self.result_label = tk.Label(self.center_frame, text="", font=("Comic Sans MS", 28, "bold"), bg="white")

        # Hard mode input
        self.answer_entry = tk.Entry(self.center_frame, width=25, font=("Comic Sans MS", 25))
        self.answer_entry.bind("<Return>", self.checker)
        self.check_button = tk.Button(self.center_frame, text="Check", font=("Comic Sans MS", 25),
                                      command=self.checker)

        # Multiple choice buttons
        self.choice_frame = tk.Frame(self.center_frame, bg="white")
        self.choice_buttons = []
        for i in range(4):
            btn = tk.Button(self.choice_frame, text="", font=("Comic Sans MS", 22), width=10,
                            command=lambda i=i: self.choose_option(i))
            btn.grid(row=0, column=i, padx=10, pady=10)
            self.choice_buttons.append(btn)
        self.choice_frame.pack_forget()

        # Next button
        self.next_button = tk.Button(self.center_frame, text="Next Question", font=("Comic Sans MS", 25),
                                     command=self.next_question)
        self.next_button.pack_forget()

        # Restart/Exit
        self.restart_button = tk.Button(self.center_frame, text="Restart Quiz", font=("Comic Sans MS", 25),
                                        command=self.restart_quiz)
        self.exit_button = tk.Button(self.center_frame, text="Exit", font=("Comic Sans MS", 25),
                                     command=self.exit_game)

        self.window.mainloop()

    # ------------------- SCORE & HIGH SCORE -------------------
    def save_score_to_file(self):
        with open("score.txt", "a") as file:
            file.write(f"Score: {self.score}/{len(self.questions)}\n")

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as file:
                return int(file.read().strip())
        except:
            with open("highscore.txt", "w") as file:
                file.write("0")
            return 0

    def save_high_score(self, new_score):
        with open("highscore.txt", "w") as file:
            file.write(str(new_score))

    # ------------------- QUIZ FLOW -------------------
    def show_difficulty(self):
        self.start_button.pack_forget()
        self.easy_button.pack(padx=10, pady=1)
        self.hard_button.pack(padx=10, pady=1)

    def select_difficulty(self, difficulty):
        self.easy_button.pack_forget()
        self.hard_button.pack_forget()
        self.difficulty = difficulty
        self.lives_text_label.place(x=self.window.winfo_screenwidth() - 200, y=20)  # show lives
        self.start_quiz()

    def start_quiz(self):
        if self.difficulty == "easy":
            self.questions = list(easy.items())
        else:
            self.questions = list(zip(hard_answers, hard_questions))
        random.shuffle(self.questions)

        self.score = 0
        self.lives = 3
        self.current_question_index = 0

        # Center stack
        self.question_number.pack(pady=10)
        self.question_label.pack(pady=10)
        self.score_label.pack(pady=5)  # score below question
        self.result_label.pack(pady=5)

        self.next_question()  # first question

    # ---------------- MULTIPLE CHOICE ----------------
    def choose_option(self, index):
        choice = self.current_choices[index]
        for btn in self.choice_buttons:
            btn.config(state=tk.DISABLED)  # disable after answering
        self.next_button.pack()  # show next button

        # Lower background volume
        pygame.mixer.music.set_volume(self.bg_volume * 0.3)

        if choice == self.current_correct_answer:
            self.score += 1
            self.result_label.config(text="Correct!", fg="green")
            self.correct_sound.play()
        else:
            self.lives -= 1
            self.result_label.config(text=f"Wrong! Answer: {self.current_correct_answer}", fg="red")
            self.wrong_sound.play()

        self.score_label.config(text=f"Score: {self.score}")
        self.lives_text_label.config(text="❤" * self.lives)

        if self.lives <= 0:
            self.finish_quiz()  # end game immediately if no lives

    def next_question(self):
        # Restore background volume
        pygame.mixer.music.set_volume(self.bg_volume)

        # hide next button and re-enable multiple choice buttons
        self.next_button.pack_forget()
        for btn in self.choice_buttons:
            btn.config(state=tk.NORMAL)

        if self.current_question_index >= len(self.questions):
            self.finish_quiz()
            return

        correct_answer, question_text = self.questions[self.current_question_index]
        self.current_correct_answer = correct_answer

        self.question_label.config(text=question_text)
        self.result_label.config(text="")
        self.question_number.config(text=f"QUESTION {self.current_question_index + 1} / {len(self.questions)}")
        self.lives_text_label.config(text="❤" * self.lives)

        if self.difficulty == "easy":
            choices = generate_choices(correct_answer)
            self.current_choices = choices
            self.choice_frame.pack()
            for i, btn in enumerate(self.choice_buttons):
                btn.config(text=str(choices[i]))
            # Hide hard mode entry/check if easy
            self.answer_entry.pack_forget()
            self.check_button.pack_forget()
        else:
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.pack(pady=10)  # show entry for hard mode
            self.check_button.pack()          # show check button
            self.answer_entry.focus_set()     # auto-focus
            self.choice_frame.pack_forget()   # hide choices in hard mode

        self.current_question_index += 1

    def finish_quiz(self):
        self.question_number.pack_forget()
        self.question_label.pack_forget()
        self.score_label.pack_forget()
        self.result_label.pack_forget()
        self.choice_frame.pack_forget()
        self.answer_entry.pack_forget()
        self.check_button.pack_forget()
        self.next_button.pack_forget()

        self.save_score_to_file()
        if self.score > self.high_score:
            self.save_high_score(self.score)
            self.high_score_label.config(text=f"High Score: {self.score}")

        self.question_label.config(text="GAME OVER!" if self.lives == 0 else "QUIZ FINISHED!")
        self.question_label.pack()
        self.restart_button.pack(pady=10)
        self.exit_button.pack(pady=10)

    # ---------------- RESTART & EXIT ----------------
    def restart_quiz(self):
        self.score = 0
        self.lives = 3
        self.current_question_index = 0
        self.difficulty = None
        self.restart_button.pack_forget()
        self.exit_button.pack_forget()
        self.start_button.pack()
        self.high_score_label.config(text=f"High Score: {self.load_high_score()}")
        self.question_label.pack_forget()
        self.result_label.config(text="")  # remove any "GAME OVER!" label
        self.lives_text_label.place_forget()  # hide lives on start
        self.choice_frame.pack_forget()
        self.answer_entry.pack_forget()
        self.check_button.pack_forget()

    def exit_game(self):
        self.window.quit()
        self.window.destroy()

    # ---------------- HARD MODE CHECKER ----------------
    def checker(self, event=None):
        if self.difficulty == "easy":
            return

        # Lower background volume
        pygame.mixer.music.set_volume(self.bg_volume * 0.3)

        try:
            ans = int(self.answer_entry.get())
            correct_answer, _ = self.questions[self.current_question_index - 1]
            if ans == correct_answer:
                self.score += 1
                self.result_label.config(text="Correct!", fg="green")
                self.correct_sound.play()
            else:
                self.lives -= 1
                self.result_label.config(text=f"Wrong! Answer is {correct_answer}", fg="red")
                self.wrong_sound.play()

            self.score_label.config(text=f"Score: {self.score}")
            self.lives_text_label.config(text="❤" * self.lives)

            # Hide entry and check button after checking
            self.answer_entry.pack_forget()
            self.check_button.pack_forget()

            # Show next button to proceed
            self.next_button.pack()

            if self.lives <= 0:
                self.finish_quiz()

        except ValueError:
            self.result_label.config(text="Invalid input", fg="red")

Mongmama()
