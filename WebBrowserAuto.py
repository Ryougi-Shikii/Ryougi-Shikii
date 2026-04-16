import pyautogui
import pyperclip
import random
import string
import time

# ── CONFIG ──────────────────────────────────────────────────────────────────
MIN_WORD_LENGTH     = 4
MAX_WORD_LENGTH     = 10
DELAY_BETWEEN_SITES = 15
STARTUP_DELAY       = 8
NUM_SEARCHES        = 30
# ────────────────────────────────────────────────────────────────────────────

def random_word():
    length = random.randint(MIN_WORD_LENGTH, MAX_WORD_LENGTH)
    return "".join(random.choice(string.ascii_lowercase) for _ in range(length))

def random_phrase():
    word_count = random.randint(1, 4)
    return " ".join(random_word() for _ in range(word_count))

searches = [random_phrase() for _ in range(NUM_SEARCHES)]

print(f"Starting in {STARTUP_DELAY} seconds — click your browser window now!")
time.sleep(STARTUP_DELAY)

for i, query in enumerate(searches, 1):
    print(f"[{i}/{len(searches)}] Searching: {query}")

    pyperclip.copy(query)

    pyautogui.hotkey("ctrl", "e")
    time.sleep(1.3)

    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)

    pyautogui.press("enter")
    time.sleep(DELAY_BETWEEN_SITES)

print("Done! All sites visited.")