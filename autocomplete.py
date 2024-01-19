import keyboard
from fuzzywuzzy import process
import logging

# from t import print
from terminal import Font

logging.getLogger("root").setLevel(level=logging.ERROR)

key_mean = {
    "space": " ",
    "backspace": "\b \b",
    "enter": "\n",
    "up": "\033[1A",
    "down": "\033[1B",
    "left": "\033[1C",
    "right": "\033[1D",
}

options = {"CFEPWDR-HB", "CFEPWDR-PR", "APLM-MELKU"}
print("Enter prodID: ", end="", flush=True)

prod_id = ""

choice_idx = 0
reset = False
while True:
    if keyboard.is_pressed("esc"):
        break
    if not prod_id and not reset:
        choice_idx = 0
        reset = True
    choices = process.extract(prod_id, choices=options)
    key = keyboard.read_event(True)
    # print(key)
    if key.event_type == "up":
        continue
    if keyboard.is_modifier(key.name):
        continue
    key_str = key_mean.get(key.name, key.name)
    if key_str == "esc":
        break
    if key_str == "\n":
        print(f"\033[{len(prod_id)}D", end="")
        print(choices[choice_idx][0], end="")
        print(key_str, end="")
        prod_id = choices[choice_idx][0]
        break
    if key.name in ["up", "down", "right", "left"]:
        if key.name == "down":
            choice_idx = (choice_idx + 1) % len(choices)
            print(f"\033[{len(prod_id)}D", end="")
            print(" " + Font.faint_font + choices[choice_idx][0], end="", flush=True)
            print(f"\033[{len(choices[choice_idx][0])}D", end="")
            print(Font.reset_font + prod_id, end="", flush=True)
        continue
    if key.name in ["tab", "right"]:
        print(f"\033[{len(prod_id)}D", end="")
        prod_id = choices[choice_idx][0]
        # print(" " + Font.faint_font + choices[choice_idx][0], end="", flush=True)
        # print(f"\033[{len(choices[choice_idx][0])}D", end="")
        print(Font.reset_font + prod_id, end="", flush=True)
        continue
    if key.name != "backspace":
        prod_id += key_str.upper()
        print(f"\033[{len(prod_id)}D", end="")
    else:
        reset = False
        print(f"\033[{len(prod_id)+1}D", end="")
        prod_id = prod_id[:-1]

    print(" " + Font.faint_font + choices[choice_idx][0], end="", flush=True)
    print(f"\033[{len(choices[choice_idx][0])}D", end="")
    print(Font.reset_font + prod_id, end="", flush=True)

print(f"PROD ID you entered is: {prod_id}")
