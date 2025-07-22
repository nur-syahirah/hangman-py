import tkinter as tk
from tkinter import messagebox
import random
import os 
import string

# -----------------------------------------------------------------------------
# Game Logic
# -----------------------------------------------------------------------------
class HangmanGame:
    def __init__(self, words = None, max_attempts=6):
        self.words = words or []
        self.max_attempts = max_attempts
        self.reset()
    
    def reset(self):
        if not self.words:
            self.word = ""
        else:
            self.word = random.choice(self.words).lower()
        self.guessed = set()
        self.attempts = self.max_attempts

    def guess(self, letter):
        letter = letter.lower()
        if letter in self.guessed:
            return "already"
        self.guessed.add(letter)
        if letter not in self.word:
            self.attempts -= 1
            return "wrong"
        return "correct"
    
    def is_won(self):
        return all(letter in self.guessed for letter in self.word)
    
    def is_lost(self):
        return self.attempts <= 0
    
    def display_word(self):
        return ' '.join(letter if letter in self.guessed else '_' for letter in self.word)
    
    def display_guesses(self):
        upper_letters = (letter.upper() for letter in sorted(self.guessed))
        return "Guessed: " + " ".join(upper_letters)
    
    @staticmethod
    def get_categories(folder='wordlists'):
        # Return list of filenames without .txt
        try:
            return [os.path.splitext(f)[0]
                    for f in os.listdir(folder)
                    if f.endswith('.txt')]
        except FileNotFoundError:
            return []
    
    @staticmethod
    def load_words(category, folder="wordlists"):
        path = os.path.join(folder, f"{category}.txt")
        try:
            with open(path, encoding="utf-8") as f:
                return [w.strip() for w in f if w.strip()]
        except FileNotFoundError:
            # Fallback list
            return ["python", "java", "kotlin", "javascript"]

# -----------------------------------------------------------------------------
# UI & UX Setup
# ---------------------------------------------------------------------------

#Create the main application window
root = tk.Tk()
root.title("Hangman Game")
root.configure(bg="lightblue")

# Category Dropdown
raw_cats = HangmanGame.get_categories()
display_to_file = {"Choose Category": None}
for name in raw_cats:
    display_name = name.capitalize()
    display_to_file[display_name] = name

selected_category = tk.StringVar(value="Choose Category")
category_menu = tk.OptionMenu(root, selected_category, *display_to_file.keys())
category_menu.config(font=("Comic Sans MS", 16), bg="lightblue", fg="black", width=12, justify="center")
category_menu.pack(pady=5, expand=True)

# Instructions
instruction_text = (
    "Instructions:\n"
    "1) Select a category from the above.\n"
    "2) Guess one letter at a time by pressing a key or clicking the keyboard below.\n"
    "3) 6 wrong attempts = Game Over.\n"
    "4) Press Reset to start over."
)

instruction_lbl = tk.Label(
    root,
    text=instruction_text,
    font=("Comic Sans MS", 16),
    justify="left",
    padx=10,
    pady=10,
    bg="lightyellow",
    fg="black",
    border=4,
    relief="ridge"
)
instruction_lbl.pack(pady=(0,10))

# Canvas for hangman
canvas = tk.Canvas(root, width=300, height=300, bg="white")
canvas.create_line(50, 250, 250, 250, width=4, fill="black")   # base
canvas.create_line(200, 250, 200, 100, width=4, fill="black")  # post
canvas.create_line(100, 100, 200, 100, width=4, fill="black")  # beam
canvas.create_line(150, 100, 150, 125, width=2, fill="black")  # rope
canvas.pack()

# Word, attempts, guesses
word_lbl     = tk.Label(root, text="", font=("Comic Sans MS", 24), bg="lightblue", fg="black")
attempts_lbl = tk.Label(root, text="", font=("Comic Sans MS", 16), bg="lightblue", fg="black")
guessed_lbl  = tk.Label(root, text="", font=("Comic Sans MS", 16), bg="lightblue", fg="black")

for widget in (word_lbl, attempts_lbl, guessed_lbl):
    widget.pack(pady=3)

# Keyboard
keyboard_frame = tk.Frame(root, bg="lightblue")
keyboard_frame.pack(pady=10)
letter_buttons = {}
# -----------------------------------------------------------------------------
# Hangman Steps for Animation
# -----------------------------------------------------------------------------
hangman_steps = [
    lambda: canvas.create_oval(125,125,175,175, tags="hangman", outline="black"),     # head
    lambda: canvas.create_line(150,175,150,225, tags="hangman", fill="black"),     # body
    lambda: canvas.create_line(150,185,120,205, tags="hangman", fill="black"),     # left arm
    lambda: canvas.create_line(150,185,180,205, tags="hangman", fill="black"),     # right arm
    lambda: canvas.create_line(150,225,120,250, tags="hangman", fill="black"),     # left leg
    lambda: canvas.create_line(150,225,180,250, tags="hangman", fill="black")      # right leg
]

def draw_static_hangman():
    canvas.delete("hangman")
    wrong = game.max_attempts - game.attempts
    for i in range(wrong):
        hangman_steps[i]()

def animate_step(idx, delay=200):
    # draw existing parts, then animate the new part
    draw_static_hangman()
    root.after(delay, hangman_steps[idx])

# -----------------------------------------------------------------------------
# Game & UI Helpers
# -----------------------------------------------------------------------------
game = HangmanGame([])

def update_ui():
    word_lbl.config(text=game.display_word().upper())
    attempts_lbl.config(text=f"Attempts left: {game.attempts}")
    guessed_lbl.config(text=game.display_guesses())

def set_buttons_state(state):
    for btn in letter_buttons.values():
        btn.config(state=state)

def start_game():
    disp = selected_category.get()
    fname = display_to_file.get(disp)

    canvas.delete("hangman")

    if not fname:
        game.words = []
        game.reset()
        update_ui()
        draw_static_hangman()
        set_buttons_state(tk.DISABLED)
        return
    
    game.words = HangmanGame.load_words(fname)
    game.reset()
    update_ui()
    set_buttons_state(tk.NORMAL)

def reset_game():
    canvas.delete("hangman")
    start_game()

# -----------------------------------------------------------------------------
# Event Handlers
# -----------------------------------------------------------------------------
# Handle letter clicks
def on_letter_click(letter):
    if letter in game.guessed:
        messagebox.showwarning(
            "Already guessed",
            f"You’ve already tried '{letter.upper()}'"
        )
        return

    result = game.guess(letter)
    letter_buttons[letter].config(state=tk.DISABLED)
    update_ui()
    root.update_idletasks()

    if result == "wrong":
        idx = game.max_attempts - game.attempts - 1
        if game.is_lost():
            draw_static_hangman()
            messagebox.showinfo("Game Over", f"The word was '{game.word}'.")
            reset_game()
        else:
            animate_step(idx)

    elif result == "correct":
        draw_static_hangman()
        if game.is_won():
            messagebox.showinfo("You win!", "Congratulations! You guessed the word!")
            reset_game()

# Keyboard Typing
def on_key_press(event):
    ch = event.char.lower()
    if ch in letter_buttons:
        on_letter_click(ch)

# -----------------------------------------------------------------------------
# Bindings & Build
# -----------------------------------------------------------------------------
selected_category.trace_add('write', lambda *_: start_game())

# Keypress binding
root.bind("<Key>", on_key_press)
root.focus_set()

# Build A–Z keyboard
for idx, ch in enumerate(string.ascii_uppercase):
    btn = tk.Button(
        keyboard_frame, 
        text=ch, 
        font=("Comic Sans MS", 14), 
        width=4,
        command=lambda letter=ch: on_letter_click(letter.lower())
    )
    btn.grid(row=idx // 9, column=idx % 9, padx=2, pady=2)
    letter_buttons[ch.lower()] = btn

set_buttons_state(tk.DISABLED)

# Reset Button
reset_btn = tk.Button(
    root,
    text="Reset",
    font=("Comic Sans MS", 16),
    command=reset_game
)
reset_btn.pack(pady=(5,15))

# Initialize UI
start_game()

# Start main loop
root.geometry("700x800")     # width x height in pixels
root.resizable(False, False) 
root.mainloop()