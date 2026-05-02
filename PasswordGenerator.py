import tkinter as tk
from tkinter import messagebox
import random
import string

try:
    import pyperclip  # optional: for clipboard copy
except ImportError:
    pyperclip = None

# ── Color palette (cyber dark theme) ──────────────────────────────────────────
BG        = "#030C14"   # deep dark background
PANEL     = "#071A28"   # slightly lighter panel
CYAN      = "#00F5D4"   # main accent
CYAN_DIM  = "#006E60"   # muted accent
TEXT      = "#C8F0EA"   # soft body text
WEAK      = "#FF4D6D"   # red   → weak
MEDIUM    = "#FFB703"   # amber → medium
STRONG    = "#00F5D4"   # cyan  → strong

FONT_MONO  = ("Courier New", 11)
FONT_LABEL = ("Courier New", 9)
FONT_TITLE = ("Courier New", 18, "bold")
FONT_PASS  = ("Courier New", 14, "bold")


# ── Helpers ────────────────────────────────────────────────────────────────────

def build_charset(use_lower, use_upper, use_digits, use_symbols):
    charset = ""
    if use_lower:  charset += string.ascii_lowercase
    if use_upper:  charset += string.ascii_uppercase
    if use_digits: charset += string.digits
    if use_symbols: charset += string.punctuation
    return charset


def generate_password(length, use_lower, use_upper, use_digits, use_symbols):
    charset = build_charset(use_lower, use_upper, use_digits, use_symbols)
    if not charset:
        return ""

    # Guarantee at least one char from each selected category
    required = []
    if use_lower:  required.append(random.choice(string.ascii_lowercase))
    if use_upper:  required.append(random.choice(string.ascii_uppercase))
    if use_digits: required.append(random.choice(string.digits))
    if use_symbols: required.append(random.choice(string.punctuation))

    rest = [random.choice(charset) for _ in range(length - len(required))]
    pool = required + rest
    random.shuffle(pool)
    return "".join(pool)


def score_password(password):
    """Return (score 0-5, label, color)."""
    score = 0
    if len(password) >= 8:  score += 1
    if len(password) >= 14: score += 1
    if any(c in string.ascii_uppercase for c in password): score += 1
    if any(c in string.digits for c in password):          score += 1
    if any(c in string.punctuation for c in password):     score += 1

    if score <= 2:   return score, "WEAK",   WEAK
    elif score <= 3: return score, "MEDIUM", MEDIUM
    else:            return score, "STRONG", STRONG


# ── Main App ───────────────────────────────────────────────────────────────────

class PasswordGeneratorApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("PassGen // Cybersecurity Tool")
        self.resizable(False, False)
        self.configure(bg=BG)

        # State vars
        self.length_var    = tk.IntVar(value=16)
        self.use_lower     = tk.BooleanVar(value=True)
        self.use_upper     = tk.BooleanVar(value=True)
        self.use_digits    = tk.BooleanVar(value=True)
        self.use_symbols   = tk.BooleanVar(value=True)
        self.password_var  = tk.StringVar(value="")

        self._build_ui()
        self._generate()          # generate one on startup

    # ── UI BUILD ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        pad = dict(padx=28)

        # ── Header ────────────────────────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=28, pady=(24, 6))

        tk.Label(header, text="// PASSGEN", font=FONT_TITLE,
                 bg=BG, fg=CYAN).pack(anchor="w")
        tk.Label(header, text="SECURE PASSWORD GENERATOR  ·  EMTE1011",
                 font=FONT_LABEL, bg=BG, fg=CYAN_DIM).pack(anchor="w")

        self._divider()

        # ── Password display ───────────────────────────────────────────────────
        disp_frame = tk.Frame(self, bg=PANEL, bd=0, highlightthickness=1,
                              highlightbackground=CYAN_DIM)
        disp_frame.pack(fill="x", padx=28, pady=(0, 6))

        tk.Label(disp_frame, text="GENERATED PASSWORD",
                 font=FONT_LABEL, bg=PANEL, fg=CYAN_DIM,
                 anchor="w").pack(fill="x", padx=14, pady=(10, 2))

        self.pass_label = tk.Label(
            disp_frame, textvariable=self.password_var,
            font=FONT_PASS, bg=PANEL, fg=CYAN,
            wraplength=380, justify="left", anchor="w"
        )
        self.pass_label.pack(fill="x", padx=14, pady=(0, 10))

        # ── Strength bar ───────────────────────────────────────────────────────
        strength_frame = tk.Frame(self, bg=BG)
        strength_frame.pack(fill="x", padx=28, pady=(0, 14))

        tk.Label(strength_frame, text="STRENGTH:",
                 font=FONT_LABEL, bg=BG, fg=CYAN_DIM).pack(side="left")

        self.strength_label = tk.Label(
            strength_frame, text="—",
            font=("Courier New", 9, "bold"), bg=BG, fg=CYAN
        )
        self.strength_label.pack(side="left", padx=(8, 16))

        # Five pip squares
        self.pips = []
        for _ in range(5):
            pip = tk.Label(strength_frame, text="■", font=("Courier New", 10),
                           bg=BG, fg=CYAN_DIM)
            pip.pack(side="left", padx=2)
            self.pips.append(pip)

        self._divider()

        # ── Controls ───────────────────────────────────────────────────────────
        ctrl = tk.Frame(self, bg=BG)
        ctrl.pack(fill="x", **pad, pady=(4, 0))

        # Length slider
        tk.Label(ctrl, text="LENGTH:", font=FONT_LABEL,
                 bg=BG, fg=CYAN_DIM, anchor="w").grid(
                     row=0, column=0, sticky="w", pady=4)

        self.length_display = tk.Label(ctrl, text=str(self.length_var.get()),
                                       font=("Courier New", 9, "bold"),
                                       bg=BG, fg=CYAN, width=4)
        self.length_display.grid(row=0, column=2, sticky="w")

        slider = tk.Scale(
            ctrl, from_=6, to=40,
            orient="horizontal", variable=self.length_var,
            command=self._on_length_change,
            bg=BG, fg=CYAN, troughcolor=PANEL,
            highlightthickness=0, activebackground=CYAN,
            sliderrelief="flat", bd=0,
            showvalue=False, length=240
        )
        slider.grid(row=0, column=1, padx=(10, 6))

        # Checkboxes
        options = [
            ("LOWERCASE  a-z",  self.use_lower),
            ("UPPERCASE  A-Z",  self.use_upper),
            ("DIGITS     0-9",  self.use_digits),
            ("SYMBOLS  !@#$%",  self.use_symbols),
        ]
        for i, (label, var) in enumerate(options, start=1):
            cb = tk.Checkbutton(
                ctrl, text=label, variable=var,
                font=FONT_LABEL, bg=BG, fg=TEXT,
                selectcolor=BG, activebackground=BG, activeforeground=CYAN,
                highlightthickness=0,
                command=self._generate
            )
            # Custom checkmark color via indicator
            cb.config(
                indicatoron=True,
                offrelief="flat", relief="flat"
            )
            cb.grid(row=i, column=0, columnspan=3, sticky="w", pady=3)

        self._divider()

        # ── Buttons ────────────────────────────────────────────────────────────
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(fill="x", padx=28, pady=(4, 24))

        self._make_btn(btn_frame, "⟳  GENERATE",  self._generate,
                       bg=CYAN, fg=BG).pack(side="left", padx=(0, 10))

        self._make_btn(btn_frame, "⎘  COPY",       self._copy,
                       bg=PANEL, fg=CYAN, border_color=CYAN_DIM).pack(side="left", padx=(0, 10))

        self._make_btn(btn_frame, "✕  CLEAR",      self._clear,
                       bg=PANEL, fg=WEAK, border_color=WEAK).pack(side="left")

    # ── Utility widgets ────────────────────────────────────────────────────────

    def _divider(self):
        tk.Frame(self, bg=CYAN_DIM, height=1).pack(fill="x", padx=28, pady=10)

    def _make_btn(self, parent, text, cmd, bg, fg, border_color=None):
        f = tk.Frame(parent, bg=border_color or bg, padx=1, pady=1)
        btn = tk.Button(
            f, text=text, command=cmd,
            font=("Courier New", 9, "bold"),
            bg=bg, fg=fg,
            activebackground=fg, activeforeground=bg,
            relief="flat", bd=0, padx=14, pady=8,
            cursor="hand2"
        )
        btn.pack()
        return f

    # ── Logic ──────────────────────────────────────────────────────────────────

    def _on_length_change(self, val):
        self.length_display.config(text=str(int(float(val))))
        self._generate()

    def _generate(self, *_):
        length = self.length_var.get()

        if not (self.use_lower.get() or self.use_upper.get() or self.use_digits.get() or self.use_symbols.get()):
            messagebox.showwarning("No charset", "Please select at least one character type.")
            self.password_var.set("")
            self._update_strength("")
            return

        pw = generate_password(
            length,
            self.use_lower.get(),
            self.use_upper.get(),
            self.use_digits.get(),
            self.use_symbols.get()
        )
        if not pw:
            messagebox.showwarning("No charset", "Please select at least one character type.")
            return
        self.password_var.set(pw)
        self._update_strength(pw)

    def _update_strength(self, pw):
        score, label, color = score_password(pw)
        self.strength_label.config(text=label, fg=color)
        for i, pip in enumerate(self.pips):
            pip.config(fg=color if i < score else CYAN_DIM)

    def _copy(self):
        pw = self.password_var.get()
        if not pw:
            return

        if pyperclip is not None:
            try:
                pyperclip.copy(pw)
                self.pass_label.config(fg=STRONG)
                self.after(800, lambda: self.pass_label.config(fg=CYAN))
                return
            except Exception:
                pass

        # fallback if pyperclip not installed or fails
        self.clipboard_clear()
        self.clipboard_append(pw)
        self.update()

    def _clear(self):
        self.password_var.set("")
        self.strength_label.config(text="—", fg=CYAN)
        for pip in self.pips:
            pip.config(fg=CYAN_DIM)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = PasswordGeneratorApp()
    app.mainloop()