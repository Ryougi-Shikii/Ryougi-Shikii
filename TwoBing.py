import pyautogui
import pyperclip
import random
import string
import time
import keyboard

# ── CONFIG ──────────────────────────────────────────────────────────────────
MIN_WORD_LENGTH     = 4
MAX_WORD_LENGTH     = 10
STARTUP_DELAY       = 8
NUM_SEARCHES        = 30
MIN_SEARCH_DELAY    = 15
MAX_SEARCH_DELAY    = 18
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

def do_search(query):
    pyperclip.copy(query)
    #pyautogui.hotkey("ctrl", "e")
    wait_with_pause(random.uniform(1.0, 1.5))
    #pyautogui.hotkey("ctrl", "v")
    wait_with_pause(random.uniform(1.0, 1.5))
    #pyautogui.press("enter")
    wait_with_pause(random.uniform(0.5, 1.0))

def switch_browser():
    #pyautogui.hotkey("alt", "tab")
    wait_with_pause(random.uniform(0.8, 1.4))

# ── GENERATE SEARCHES ────────────────────────────────────────────────────────
b1_searches = [random_phrase() for _ in range(NUM_SEARCHES)]
b2_searches = [random_phrase() for _ in range(NUM_SEARCHES)]

# ── START ────────────────────────────────────────────────────────────────────
print(f"Controls: [{PAUSE_KEY.upper()}] Pause/Resume   [{STOP_KEY.upper()}] Stop")
print(f"Have both browsers open. Focus Browser 1 before countdown ends!")
print(f"Starting in {STARTUP_DELAY} seconds...")
wait_with_pause(STARTUP_DELAY)

# ── INTERLEAVED LOOP ─────────────────────────────────────────────────────────
# Pattern each iteration:
#   1. Search on Browser 1
#   2. Alt+tab → Browser 2, search there
#   3. Alt+tab → Browser 1, wait remaining delay
#   4. Repeat

for i in range(NUM_SEARCHES):
    while paused:
        time.sleep(0.2)

    delay = round(random.uniform(MIN_SEARCH_DELAY, MAX_SEARCH_DELAY), 1)

    # ── Browser 1 ────────────────────────────────────────────────────────────
    print(f"\n[{i+1}/{NUM_SEARCHES}] Browser 1: '{b1_searches[i]}'")
    do_search(b1_searches[i])
    delay -= 4.0

    # ── Switch to Browser 2 and search ───────────────────────────────────────
    print(f"  ↔  Switching to Browser 2...")
    switch_browser()
    delay -= 1.4
    print(f"[{i+1}/{NUM_SEARCHES}] Browser 2: '{b2_searches[i]}'")
    do_search(b2_searches[i])
    delay -= 4.0

    # ── Switch back to Browser 1 ──────────────────────────────────────────────
    print(f"  ↔  Switching back to Browser 1...")
    switch_browser()
    delay -= 1.4

    # ── Wait remaining delay before next round ────────────────────────────────
    print(f"  ⏳ Next round in {delay}s...")
    wait_with_pause(delay)

print("\nDone! 30 searches completed on each browser.")


# do_search      -> 2.5 - 4.0
# switch_browser -> 0.8 - 1.4
