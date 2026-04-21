import pyautogui
import pyperclip
import random
import string
import time
import keyboard

# ── CONFIG ──────────────────────────────────────────────────────────────────
MIN_WORD_LENGTH     = 4
MAX_WORD_LENGTH     = 9
STARTUP_DELAY       = 8
NUM_SEARCHES        = 30
MIN_SEARCH_DELAY    = 12
MAX_SEARCH_DELAY    = 16
PAUSE_KEY           = "p"
STOP_KEY            = "q"
# ────────────────────────────────────────────────────────────────────────────

paused = False

def toggle_pause():
    global paused
    paused = not paused
    print("\n⏸  PAUSED — press P again to resume" if paused else "\n▶  RESUMED")

def stop_script():
    print("\n⛔ STOPPED by user.")
    raise SystemExit

keyboard.add_hotkey(PAUSE_KEY, toggle_pause)
keyboard.add_hotkey(STOP_KEY, stop_script)

def wait_with_pause(seconds):
    elapsed = 0
    while elapsed < seconds:
        while paused:
            time.sleep(0.2)
        time.sleep(0.2)
        elapsed += 0.2

def random_word():
    length = random.randint(MIN_WORD_LENGTH, MAX_WORD_LENGTH)
    return "".join(random.choice(string.ascii_lowercase) for _ in range(length))

def random_phrase():
    word_count = random.randint(1, 5)
    return " ".join(random_word() for _ in range(word_count))

searches = [random_phrase() for _ in range(NUM_SEARCHES)]

print(f"Controls: [{PAUSE_KEY.upper()}] Pause/Resume   [{STOP_KEY.upper()}] Stop")
print(f"Starting in {STARTUP_DELAY} seconds — click your browser window now!")
wait_with_pause(STARTUP_DELAY)

for i, query in enumerate(searches, 1):
    while paused:
        time.sleep(0.2)

    delay = round(random.uniform(MIN_SEARCH_DELAY, MAX_SEARCH_DELAY), 1)
    print(f"[{i}/{len(searches)}] Searching: '{query}'  (next in {delay}s)")

    pyperclip.copy(query)

    pyautogui.hotkey("ctrl", "e")
    wait_with_pause(random.uniform(1.4, 2.0))

    pyautogui.hotkey("ctrl", "v")
    wait_with_pause(random.uniform(1.0, 1.4))

    pyautogui.press("enter")
    wait_with_pause(delay)

print("Done! All sites visited.")