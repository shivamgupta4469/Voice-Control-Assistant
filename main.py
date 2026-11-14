import speech_recognition as sr
import pyttsx3
import webbrowser
import subprocess
import os
import urllib.parse
import ctypes
import time
import ast
import operator
import platform
import shutil
import pyperclip
import requests
import random
import tkinter as tk
import threading
import math
import pyperclip
import json
import threading
from pathlib import Path


# =========================================================
# SETTINGS
# =========================================================

recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True
recognizer.energy_threshold = 300
recognizer.pause_threshold = 0.8
recognizer.non_speaking_duration = 0.5
engine = pyttsx3.init()

engine.setProperty("rate", 170)
engine.setProperty("volume", 1.0)

# =========================================
# ANDROID PHONE CONTROL SETTINGS
# =========================================

SCRCPY_FOLDER = os.path.expandvars(
    r"%USERPROFILE%\Downloads\scrcpy-win64-v4.1\scrcpy-win64-v4.1"
)

ADB_PATH = os.path.join(
    SCRCPY_FOLDER,
    "adb.exe"
)

SCRCPY_PATH = os.path.join(
    SCRCPY_FOLDER,
    "scrcpy.exe"
)

# =========================================================
# ANIMATED VOICE UI
# =========================================================

ui_root = None
ui_canvas = None
ui_running = False
ui_state = "READY"


def create_voice_ui():

    global ui_root
    global ui_canvas
    global ui_running

    ui_root = tk.Tk()

    ui_root.title("Voice Control Assistant")
    ui_root.geometry("500x500")
    ui_root.configure(bg="#0b1020")

    ui_root.resizable(False, False)

    title = tk.Label(
        ui_root,
        text="VOICE CONTROL ASSISTANT",
        font=("Segoe UI", 18, "bold"),
        fg="white",
        bg="#0b1020"
    )

    title.pack(pady=25)

    ui_canvas = tk.Canvas(
        ui_root,
        width=440,
        height=300,
        bg="#0b1020",
        highlightthickness=0
    )

    ui_canvas.pack()

    status = tk.Label(
        ui_root,
        text="● READY",
        font=("Segoe UI", 14, "bold"),
        fg="#00ff99",
        bg="#0b1020"
    )

    status.pack(pady=10)

    ui_running = True

    def animate():

        if not ui_running:
            return

        ui_canvas.delete("all")

        center_x = 220
        center_y = 145

        # Avatar circle
        pulse = 10 * math.sin(time.time() * 4)

        radius = 70 + pulse

        ui_canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            outline="#00e5ff",
            width=4
        )

        # Face
        ui_canvas.create_oval(
            center_x - 42,
            center_y - 30,
            center_x - 25,
            center_y - 13,
            fill="#00e5ff",
            outline=""
        )

        ui_canvas.create_oval(
            center_x + 25,
            center_y - 30,
            center_x + 42,
            center_y - 13,
            fill="#00e5ff",
            outline=""
        )

        ui_canvas.create_arc(
            center_x - 35,
            center_y - 5,
            center_x + 35,
            center_y + 40,
            start=200,
            extent=140,
            outline="#00e5ff",
            width=4
        )

        # Waveform
        bars = 25

        for i in range(bars):

            x = 45 + i * 14

            if ui_state == "LISTENING":

                height = (
                    15
                    + abs(
                        math.sin(
                            time.time() * 8 + i
                        )
                    ) * 45
                )

            elif ui_state == "SPEAKING":

                height = (
                    15
                    + abs(
                        math.sin(
                            time.time() * 12 + i
                    )
                    ) * 65
                )

            elif ui_state == "PROCESSING":

                height = (
                    20
                    + abs(
                        math.sin(
                            time.time() * 5 + i
                        )
                    ) * 30
                )

            else:

                height = 10

            ui_canvas.create_rectangle(
                x,
                275 - height,
                x + 7,
                275,
                fill="#00e5ff",
                outline=""
            )

        # Status text
        if ui_state == "LISTENING":

            status.config(
                text="● LISTENING...",
                fg="#00ff99"
            )

        elif ui_state == "PROCESSING":

            status.config(
                text="● PROCESSING...",
                fg="#ffaa00"
            )

        elif ui_state == "SPEAKING":

            status.config(
                text="● SPEAKING...",
                fg="#00e5ff"
            )

        else:

            status.config(
                text="● READY",
                fg="#00ff99"
            )

        ui_root.after(
            40,
            animate
        )

    animate()

    ui_root.mainloop()


def set_ui_state(state):

    global ui_state

    ui_state = state

# =========================================================
# SPEAK
# =========================================================


def speak(text):
    print("Assistant:", text)

    try:
        if not engine:
            print("Voice engine initialize nahi hua.")
            return

        engine.stop()
        engine.say(str(text))
        engine.runAndWait()

    except Exception as e:
        print("Voice Error:", repr(e))





# =========================================================
# NOISE CANCELLATION + SMART LISTEN
# =========================================================

def listen():

    with sr.Microphone() as source:

        print("\n🎤 Listening...")
        set_ui_state("LISTENING")

        # Background noise calibration
        recognizer.dynamic_energy_threshold = True
        recognizer.energy_threshold = 300
        recognizer.pause_threshold = 0.8
        recognizer.non_speaking_duration = 0.5

        print("🔇 Removing background noise...")

        recognizer.adjust_for_ambient_noise(
            source,
            duration=0.5
        )

        print("🎙️ Ready. Speak now...")

        try:

            audio = recognizer.listen(
                source,
                timeout=20,
                phrase_time_limit=25
            )

        except sr.WaitTimeoutError:

            print("No voice detected.")
            return ""

    print("Recognizing...")

    try:

        command = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        command = command.lower().strip()

        print("You:", command)

        return command

    except sr.UnknownValueError:

        print(
            "Sorry, I could not understand. "
            "Background noise may be too high."
        )

        return ""

    except sr.RequestError:

        speak(
            "Internet connection problem."
        )

        return ""

# =========================================================
# WEB
# =========================================================

def open_website(url):
    webbrowser.open_new_tab(url)


def search_google_and_chatgpt(query):

    speak(
        "Opening Google and ChatGPT for "
        + query
    )

    encoded_query = urllib.parse.quote_plus(
        query
    )

    webbrowser.open_new_tab(
        "https://www.google.com/search?q="
        + encoded_query
    )

    time.sleep(1)

    webbrowser.open_new_tab(
        "https://chatgpt.com/?q="
        + encoded_query
    )


# =========================================================
# YOUTUBE DIRECT PLAY
# =========================================================

def youtube_play(song):

    speak(
        "Playing "
        + song
        + " on YouTube."
    )

    try:

        import yt_dlp

        options = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(options) as ydl:

            result = ydl.extract_info(
                "ytsearch1:" + song,
                download=False
            )

        entries = result.get(
            "entries",
            []
        )

        if not entries:

            speak(
                "I could not find that song on YouTube."
            )

            return

        video_url = entries[0].get(
            "webpage_url"
        )

        if not video_url:

            video_id = entries[0].get(
                "id"
            )

            video_url = (
                "https://www.youtube.com/watch?v="
                + video_id
            )

        webbrowser.open_new_tab(
            video_url
        )

    except ImportError:

        speak(
            "YouTube player is not installed. "
            "Please install yt-dlp."
        )

        print(
            "Run: python -m pip install yt-dlp"
        )

    except Exception as e:

        print(
            "YouTube error:",
            e
        )

        speak(
            "Sorry, I could not play the video."
        )


# =========================================================
# APPLICATIONS
# =========================================================

def open_application(app_name):

    try:

        subprocess.Popen(
            [
                "cmd",
                "/c",
                "start",
                "",
                app_name
            ],
            shell=False
        )

        speak(
            "Opening "
            + app_name
        )

    except Exception as e:

        print(
            "Application error:",
            e
        )

        speak(
            "I could not open that application."
        )


def close_application(app_name):

    process_map = {

        "chrome": [
            "chrome.exe"
        ],

        "google chrome": [
            "chrome.exe"
        ],

        "notepad": [
            "notepad.exe"
        ],

        "calculator": [
            "CalculatorApp.exe",
            "calc.exe"
        ],

        "vs code": [
            "Code.exe"
        ],

        "visual studio code": [
            "Code.exe"
        ],

        "explorer": [
            "explorer.exe"
        ],

        "file explorer": [
            "explorer.exe"
        ]
    }

    processes = process_map.get(
        app_name
    )

    if not processes:

        process_name = app_name.strip()

        if (
            " " in process_name
            or not process_name
        ):

            speak(
                "I don't know how to close "
                "that application yet."
            )

            return

        processes = [
            process_name
            if process_name.lower().endswith(".exe")
            else process_name + ".exe"
        ]

    closed = False

    for process in processes:

        result = subprocess.run(
            [
                "taskkill",
                "/IM",
                process,
                "/F"
            ],
            capture_output=True,
            text=True,
            shell=False
        )

        if result.returncode == 0:

            closed = True
            break

    if closed:

        speak(
            "Closed "
            + app_name
        )

    else:

        speak(
            app_name
            + " is not running or could not be closed."
        )


# =========================================================
# MEDIA
# =========================================================

def media_key(action):

    VK_MEDIA_PLAY_PAUSE = 0xB3
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1

    keys = {

        "play":
            VK_MEDIA_PLAY_PAUSE,

        "pause":
            VK_MEDIA_PLAY_PAUSE,

        "next":
            VK_MEDIA_NEXT_TRACK,

        "previous":
            VK_MEDIA_PREV_TRACK
    }

    if action in keys:

        ctypes.windll.user32.keybd_event(
            keys[action],
            0,
            0,
            0
        )

        ctypes.windll.user32.keybd_event(
            keys[action],
            0,
            2,
            0
        )


# =========================================================
# VOLUME / BRIGHTNESS / KEYBOARD
# =========================================================

def volume_up():

    import pyautogui

    pyautogui.press(
        "volumeup",
        presses=5,
        interval=0.05
    )

    speak(
        "Volume increased."
    )


def volume_down():

    import pyautogui

    pyautogui.press(
        "volumedown",
        presses=5,
        interval=0.05
    )

    speak(
        "Volume decreased."
    )


def volume_mute():

    import pyautogui

    pyautogui.press(
        "volumemute"
    )

    speak(
        "Volume muted."
    )


def brightness_up():

    import pyautogui

    for _ in range(5):

        pyautogui.press(
            "brightnessup"
        )

    speak(
        "Brightness increased."
    )


def brightness_down():

    import pyautogui

    for _ in range(5):

        pyautogui.press(
            "brightnessdown"
        )

    speak(
        "Brightness decreased."
    )


def voice_type(text):

    import pyautogui

    speak(
        "Typing."
    )

    pyautogui.write(
        text,
        interval=0.03
    )


def copy_text():

    import pyautogui

    pyautogui.hotkey(
        "ctrl",
        "c"
    )

    speak(
        "Copied."
    )


def paste_text():

    import pyautogui

    pyautogui.hotkey(
        "ctrl",
        "v"
    )

    speak(
        "Pasted."
    )


def cut_text():

    import pyautogui

    pyautogui.hotkey(
        "ctrl",
        "x"
    )

    speak(
        "Cut."
    )


# =========================================================
# SCREENSHOT / FOLDERS
# =========================================================

def take_screenshot():

    try:

        import pyautogui

        folder = (
            Path.home()
            / "Pictures"
            / "VoiceAssistantScreenshots"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        filename = (
            "screenshot_"
            + time.strftime(
                "%Y%m%d_%H%M%S"
            )
            + ".png"
        )

        filepath = folder / filename

        pyautogui.screenshot().save(
            filepath
        )

        speak(
            "Screenshot saved."
        )

        print(
            "Saved:",
            filepath
        )

    except Exception as e:

        print(e)

        speak(
            "Screenshot feature is not available."
        )


def open_folder(folder_name):

    folders = {

        "downloads":
            Path.home() / "Downloads",

        "documents":
            Path.home() / "Documents",

        "desktop":
            Path.home() / "Desktop",

        "pictures":
            Path.home() / "Pictures",

        "videos":
            Path.home() / "Videos",

        "music":
            Path.home() / "Music"
    }

    path = folders.get(
        folder_name
    )

    if path and path.exists():

        speak(
            "Opening "
            + folder_name
        )

        os.startfile(
            path
        )

    else:

        speak(
            folder_name
            + " folder was not found."
        )


# =========================================================
# MATHS
# =========================================================

operators = {

    ast.Add:
        operator.add,

    ast.Sub:
        operator.sub,

    ast.Mult:
        operator.mul,

    ast.Div:
        operator.truediv,

    ast.FloorDiv:
        operator.floordiv,

    ast.Mod:
        operator.mod,

    ast.Pow:
        operator.pow,

    ast.USub:
        operator.neg,

    ast.UAdd:
        operator.pos
}


def safe_calculate(expression):

    try:

        tree = ast.parse(
            expression,
            mode="eval"
        )

        def calc(node):

            if (
                isinstance(
                    node,
                    ast.Constant
                )
                and isinstance(
                    node.value,
                    (int, float)
                )
            ):

                return node.value

            if isinstance(
                node,
                ast.UnaryOp
            ):

                fn = operators.get(
                    type(node.op)
                )

                if fn is None:

                    raise ValueError

                return fn(
                    calc(
                        node.operand
                    )
                )

            if isinstance(
                node,
                ast.BinOp
            ):

                fn = operators.get(
                    type(node.op)
                )

                if fn is None:

                    raise ValueError

                return fn(
                    calc(node.left),
                    calc(node.right)
                )

            raise ValueError

        return calc(
            tree.body
        )

    except Exception:

        return None


def calculate_command(command):

    expression = command.lower()

    remove_words = [

        "calculate",
        "calculator",
        "solve",
        "what is",
        "what's",
        "equals",
        "equal to",
        "please"
    ]

    for word in remove_words:

        expression = expression.replace(
            word,
            ""
        )

    replacements = {

        " to the power of ":
            " ** ",

        " multiplied by ":
            " * ",

        " divided by ":
            " / ",

        " divide by ":
            " / ",

        " times ":
            " * ",

        " plus ":
            " + ",

        " add ":
            " + ",

        " minus ":
            " - ",

        " subtract ":
            " - ",

        " over ":
            " / ",

        " mod ":
            " % ",

        " modulo ":
            " % ",

        " power ":
            " ** "
    }

    expression = (
        " "
        + expression
        + " "
    )

    for word, symbol in replacements.items():

        expression = expression.replace(
            word,
            symbol
        )

    expression = expression.strip()

    allowed = set(
        "0123456789+-*/%.() "
    )

    expression = "".join(
        c
        for c in expression
        if c in allowed
    )

    if not expression:

        return False

    result = safe_calculate(
        expression
    )

    if result is None:

        speak(
            "I could not calculate that."
        )

        return True

    if (
        isinstance(
            result,
            float
        )
        and result.is_integer()
    ):

        result = int(result)

    speak(
        "The answer is "
        + str(result)
    )

    return True



# =========================================================
# SMART VOICE NOTES - READ, SEARCH, LIST, DELETE
# =========================================================

VOICE_NOTES_DIR = Path.home() / "Documents" / "VoiceNotes"


def get_voice_notes():
    VOICE_NOTES_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(
        VOICE_NOTES_DIR.glob("*.txt"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )


def read_latest_note():
    notes = get_voice_notes()

    if not notes:
        speak("You have no saved voice notes.")
        return

    latest = notes[0]

    try:
        content = latest.read_text(encoding="utf-8").strip()

        print("\n===== LATEST VOICE NOTE =====")
        print("File:", latest.name)
        print(content)
        print("=============================\n")

        if content:
            speak("Your latest note says: " + content)
        else:
            speak("Your latest note is empty.")

    except OSError as e:
        print("Read note error:", repr(e))
        speak("Sorry, I could not read your latest note.")


def search_voice_notes(query):
    notes = get_voice_notes()
    query_words = query.lower().split()
    matches = []

    for note in notes:
        try:
            content = note.read_text(encoding="utf-8")
            searchable = (note.stem + " " + content).lower()

            if all(word in searchable for word in query_words):
                matches.append((note, content))

        except OSError as e:
            print("Search note error:", repr(e))

    if not matches:
        speak("No matching notes found.")
        return []

    print("\n===== MATCHING NOTES =====")

    for index, (note, content) in enumerate(matches, start=1):
        print(f"{index}. {note.name}")
        print(content)
        print("--------------------------")

    speak(f"I found {len(matches)} matching notes.")
    return matches


def show_voice_notes():
    notes = get_voice_notes()

    if not notes:
        speak("You have no saved voice notes.")
        return

    print("\n===== YOUR VOICE NOTES =====")

    for index, note in enumerate(notes, start=1):
        print(f"{index}. {note.name}")

    print("============================\n")
    speak(f"You have {len(notes)} saved voice notes.")


def delete_voice_note(query):
    matches = search_voice_notes(query)

    if not matches:
        return

    if len(matches) > 1:
        speak(
            "More than one note matched. "
            "Please use a more specific search phrase. "
            "No note was deleted."
        )
        return

    note, content = matches[0]

    print("Selected note:", note.name)
    speak(
        f"Do you want to permanently delete {note.name}? "
        "Say yes to confirm."
    )

    answer = voice_input("Say yes or no.")

    if not answer or answer.strip().lower() not in (
        "yes", "yes please", "confirm"
    ):
        speak("Deletion cancelled. Your note is safe.")
        return

    try:
        note.unlink()
        print("Deleted:", note)
        speak("The voice note has been deleted.")

    except OSError as e:
        print("Delete note error:", repr(e))
        speak("Sorry, I could not delete that note.")


# =========================================================
# ADVANCED FEATURES: VISION, MEMORY, MACROS, HEALTH, TRACKER
# =========================================================

import json
import os
import time
import subprocess
from pathlib import Path

import psutil

ADVANCED_DATA_DIR = Path.home() / "Documents" / "VoiceAssistantData"
ADVANCED_DATA_DIR.mkdir(parents=True, exist_ok=True)

PROJECT_TASKS_FILE = ADVANCED_DATA_DIR / "project_tasks.json"
MACROS_FILE = ADVANCED_DATA_DIR / "voice_macros.json"


# ---------------------------------------------------------
# 1. SCREEN VISION: SCREENSHOT + OCR TEXT EXTRACTION
# ---------------------------------------------------------

def screen_vision():
    try:
        import pyautogui
        import pytesseract

        # Agar Tesseract PATH mein nahi hai, neeche wali
        # line ko apne installed path ke hisaab se uncomment karo:
        # pytesseract.pytesseract.tesseract_cmd = (
        #     r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        # )

        screenshot = pyautogui.screenshot()

        image_path = ADVANCED_DATA_DIR / (
            "screen_" + time.strftime("%Y%m%d_%H%M%S") + ".png"
        )
        screenshot.save(image_path)

        extracted_text = pytesseract.image_to_string(screenshot).strip()

        print("\n===== SCREEN VISION =====")
        print("Screenshot:", image_path)
        print(extracted_text or "No readable text detected.")
        print("=========================\n")

        if extracted_text:
            speak("I extracted the visible screen text. Check the terminal.")
        else:
            speak("Screenshot saved, but I could not read text on the screen.")

        os.startfile(str(image_path))

    except Exception as e:
        print("Screen Vision error:", repr(e))
        speak("Screen Vision failed. Check the OCR installation.")


# ---------------------------------------------------------
# 2. PERSONAL MEMORY BRAIN: SEARCH NOTES
# ---------------------------------------------------------

def personal_memory_search(query):
    query_words = query.lower().split()
    notes_dir = Path.home() / "Documents" / "VoiceNotes"
    results = []

    if notes_dir.exists():
        for note in notes_dir.glob("*.txt"):
            try:
                content = note.read_text(encoding="utf-8")
                searchable = (note.stem + " " + content).lower()

                if query_words and all(word in searchable for word in query_words):
                    results.append((note.name, content))
            except OSError as e:
                print("Memory search error:", repr(e))

    if not results:
        speak("I could not find that information in your saved notes.")
        return

    print("\n===== PERSONAL MEMORY =====")
    for filename, content in results:
        print("Note:", filename)
        print(content)
        print("---------------------------")

    speak(f"I found {len(results)} matching saved notes. Check the terminal.")


# ---------------------------------------------------------
# 3. VOICE MACROS: SAVE AND RUN CODING SETUP
# ---------------------------------------------------------

def load_macros():
    if not MACROS_FILE.exists():
        return {}

    try:
        return json.loads(MACROS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_coding_macro():
    macros = load_macros()

    macros["coding setup"] = {
        "apps": ["code"],
        "folder": str(Path.home() / "Documents")
    }

    MACROS_FILE.write_text(
        json.dumps(macros, indent=2),
        encoding="utf-8"
    )

    speak("Coding setup macro saved. Edit its folder path for your project.")



def run_coding_macro():
    import shutil
    import subprocess
    import os
    from pathlib import Path

    macros = load_macros()
    macro = macros.get("coding setup", {})

    # Find VS Code
    code_cmd = shutil.which("code")

    if not code_cmd:
        possible_paths = [
            Path(os.environ.get("LOCALAPPDATA", "")) /
            "Programs" / "Microsoft VS Code" / "Code.exe",

            Path(os.environ.get("ProgramFiles", "C:\\Program Files")) /
            "Microsoft VS Code" / "Code.exe",

            Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) /
            "Microsoft VS Code" / "Code.exe",
        ]

        code_cmd = next(
            (str(path) for path in possible_paths if path.is_file()),
            None
        )

    if not code_cmd:
        print("VS Code executable not found.")
        speak("VS Code nahi mila. Pehle VS Code install ya uska path set karo.")
        return

    # Open configured folder if it exists
    folder = Path(macro.get("folder", str(Path.home() / "Documents")))

    try:
        if folder.is_dir():
            subprocess.Popen([code_cmd, str(folder)])
        else:
            print("Configured folder not found:", folder)
            subprocess.Popen([code_cmd])

        speak("Coding setup started.")
    except Exception as e:
        print("Macro error:", repr(e))
        speak("Coding setup start nahi ho paya.")


# ---------------------------------------------------------
# 4. PC HEALTH DETECTIVE
# ---------------------------------------------------------

def pc_health_report():
    try:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(str(Path.home().anchor or "C:\\"))

        print("\n===== PC HEALTH REPORT =====")
        print(f"CPU usage: {cpu}%")
        print(f"RAM usage: {memory.percent}%")
        print(f"RAM available: {memory.available / (1024 ** 3):.2f} GB")
        print(f"Disk usage: {disk.percent}%")
        print("============================\n")

        issues = []

        if cpu >= 85:
            issues.append("CPU usage is high")
        if memory.percent >= 85:
            issues.append("RAM usage is high")
        if disk.percent >= 90:
            issues.append("Disk usage is high")

        if issues:
            speak(". ".join(issues) + ". Details are in the terminal.")
        else:
            speak("No high CPU, RAM, or disk usage detected. Details are in the terminal.")

    except Exception as e:
        print("PC Health error:", repr(e))
        speak("I could not complete the PC health report.")


# ---------------------------------------------------------
# 5. PROJECT PROGRESS TRACKER
# ---------------------------------------------------------

def load_project_tasks():
    if not PROJECT_TASKS_FILE.exists():
        return {}

    try:
        return json.loads(PROJECT_TASKS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_project_tasks(tasks):
    PROJECT_TASKS_FILE.write_text(
        json.dumps(tasks, indent=2),
        encoding="utf-8"
    )


def add_project_task(project, task):
    tasks = load_project_tasks()
    tasks.setdefault(project, [])
    tasks[project].append({"task": task, "done": False})
    save_project_tasks(tasks)
    speak("Task added to " + project)


def show_project_tasks(project):
    tasks = load_project_tasks()
    matching_project = next(
        (name for name in tasks if name.lower() == project.lower()),
        None
    )

    if not matching_project or not tasks[matching_project]:
        speak("No tasks found for that project. Add a task first.")
        return

    print(f"\n===== {matching_project} TASKS =====")
    for index, item in enumerate(tasks[matching_project], start=1):
        status = "DONE" if item["done"] else "PENDING"
        print(f"{index}. [{status}] {item['task']}")

    pending = sum(not item["done"] for item in tasks[matching_project])
    speak(f"{pending} tasks are pending in {matching_project}. Check the terminal.")


def complete_project_task(project, task_query):
    tasks = load_project_tasks()
    matching_project = next(
        (name for name in tasks if name.lower() == project.lower()),
        None
    )

    if not matching_project:
        speak("Project not found.")
        return

    for item in tasks[matching_project]:
        if task_query.lower() in item["task"].lower():
            item["done"] = True
            save_project_tasks(tasks)
            speak("Task marked as completed.")
            return

    speak("I could not find a matching task.")


import webbrowser
from urllib.parse import quote_plus

def smart_launcher(command):
    command = command.lower().strip()

    websites = {
        "github": "https://github.com",
        "linkedin": "https://www.linkedin.com",
        "chatgpt": "https://chatgpt.com",
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "gmail": "https://mail.google.com",
        "stackoverflow": "https://stackoverflow.com",
        "leetcode": "https://leetcode.com",
    }

    if command.startswith("open "):
        name = command[5:].strip()

        if name in websites:
            webbrowser.open(websites[name])
            speak(f"Opening {name}")
            return True

        if name in ("vs code", "visual studio code", "vscode"):
            import shutil
            import subprocess

            code_path = shutil.which("code")
            if code_path:
                subprocess.Popen([code_path])
                speak("Opening Visual Studio Code")
            else:
                speak("VS Code command was not found")
            return True

    if command.startswith("search "):
        query = command[7:].strip()
        if query:
            url = "https://www.google.com/search?q=" + quote_plus(query)
            webbrowser.open(url)
            speak("Searching Google")
        return True

    return False


# =========================================================
# NEW ADVANCED FEATURES: GUARD, STORAGE, NETWORK, PRODUCTIVITY
# =========================================================

import os
import json
import time
import socket
import hashlib
import subprocess
import threading
from pathlib import Path
from getpass import getpass

import psutil

ADVANCED_DIR = Path.home() / "Documents" / "VoiceAssistantData"
ADVANCED_DIR.mkdir(parents=True, exist_ok=True)

GUARD_FILE = ADVANCED_DIR / "app_guard.json"
PRODUCTIVITY_FILE = ADVANCED_DIR / "productivity_usage.json"

# ---------- 1. SMART APP GUARD ----------

PROTECTED_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "vscode": "Code.exe",
}

def load_guard_data():
    try:
        return json.loads(GUARD_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

def setup_app_guard():
    pin = getpass("Create a PIN (input stays hidden): ").strip()
    if len(pin) < 4:
        speak("PIN must contain at least four characters.")
        return

    data = load_guard_data()
    data["pin_hash"] = hashlib.sha256(pin.encode()).hexdigest()
    GUARD_FILE.write_text(json.dumps(data), encoding="utf-8")
    speak("App Guard PIN saved.")

def guarded_open_app(app_name):
    app_name = app_name.lower().strip()
    executable = PROTECTED_APPS.get(app_name)

    if not executable:
        speak("This app is not in the protected app list.")
        return

    data = load_guard_data()
    if not data.get("pin_hash"):
        speak("Set up the App Guard PIN first.")
        return

    entered_pin = getpass("Enter App Guard PIN: ").strip()
    entered_hash = hashlib.sha256(entered_pin.encode()).hexdigest()

    if entered_hash != data["pin_hash"]:
        speak("Incorrect PIN. App not opened.")
        return

    try:
        subprocess.Popen([executable], shell=False)
        speak("PIN accepted. Opening " + app_name)
    except Exception as e:
        print("App Guard error:", repr(e))
        speak("Could not open this app.")

# ---------- 2. SMART STORAGE DETECTIVE ----------

def storage_detective():
    scan_roots = [
        Path.home() / "Downloads",
        Path.home() / "Desktop",
        Path.home() / "Documents",
    ]

    files = []
    for root in scan_roots:
        if not root.exists():
            continue
        try:
            for path in root.rglob("*"):
                try:
                    if path.is_file():
                        files.append((path, path.stat().st_size))
                except (OSError, PermissionError):
                    continue
        except (OSError, PermissionError):
            continue

    largest = sorted(files, key=lambda item: item[1], reverse=True)[:10]

    # Hash files of equal size only, to detect actual duplicates.
    by_size = {}
    for path, size in files:
        if size > 0:
            by_size.setdefault(size, []).append(path)

    duplicates = []
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        hashes = {}
        for path in paths:
            try:
                digest = hashlib.sha256()
                with path.open("rb") as file_obj:
                    for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
                        digest.update(chunk)
                hashes.setdefault(digest.hexdigest(), []).append(path)
            except (OSError, PermissionError):
                continue
        for same_files in hashes.values():
            if len(same_files) > 1:
                duplicates.append(same_files)

    print("\n===== STORAGE DETECTIVE =====")
    print("Files scanned:", len(files))
    print("\nLargest files:")
    for path, size in largest:
        print(f"{size / (1024 ** 2):8.1f} MB  {path}")

    print("\nDuplicate groups:")
    if duplicates:
        for group in duplicates:
            print("Same content:")
            for path in group:
                print("  ", path)
    else:
        print("No duplicates found in scanned folders.")

    print("=============================\n")
    speak("Storage scan finished. Check the terminal for the report.")

# ---------- 3. NETWORK DETECTIVE ----------

def network_detective():
    print("\n===== NETWORK DETECTIVE =====")

    # Internet reachability
    try:
        with socket.create_connection(("1.1.1.1", 443), timeout=3):
            print("Internet connectivity: OK")
    except OSError:
        print("Internet connectivity: FAILED")

    # DNS lookup
    try:
        addresses = socket.getaddrinfo("example.com", 443)
        print("DNS lookup: OK")
        print("Resolved address:", addresses[0][4][0])
    except OSError as e:
        print("DNS lookup: FAILED -", e)

    # Windows ping test
    try:
        result = subprocess.run(
            ["ping", "-n", "3", "-w", "1500", "1.1.1.1"],
            capture_output=True,
            text=True,
            timeout=7
        )
        print("\nPing result:")
        print(result.stdout.strip() or result.stderr.strip())
    except (OSError, subprocess.TimeoutExpired) as e:
        print("Ping test failed:", e)

    print("==============================\n")
    speak("Network diagnostics finished. Check the terminal.")

# ---------- 4. PRODUCTIVITY TRACKER ----------

_productivity_stop = threading.Event()
_productivity_thread = None
_productivity_lock = threading.Lock()

def _productivity_worker():
    try:
        import win32gui
        import win32process
    except ImportError:
        print("Install pywin32 to track the active window.")
        speak("Productivity tracking needs pywin32.")
        _productivity_stop.set()
        return

    usage = {}
    last_app = None
    last_time = time.time()

    while not _productivity_stop.wait(2):
        now = time.time()
        elapsed = max(0, min(now - last_time, 5))
        last_time = now

        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            app_name = psutil.Process(pid).name()
        except Exception:
            app_name = "Unknown"

        if last_app:
            usage[last_app] = usage.get(last_app, 0) + elapsed
        last_app = app_name

        with _productivity_lock:
            try:
                existing = json.loads(
                    PRODUCTIVITY_FILE.read_text(encoding="utf-8")
                ) if PRODUCTIVITY_FILE.exists() else {}
            except (OSError, json.JSONDecodeError):
                existing = {}

            today = time.strftime("%Y-%m-%d")
            daily = existing.setdefault(today, {})
            for app, seconds in usage.items():
                daily[app] = daily.get(app, 0) + seconds
            usage.clear()

            try:
                PRODUCTIVITY_FILE.write_text(
                    json.dumps(existing, indent=2),
                    encoding="utf-8"
                )
            except OSError as e:
                print("Productivity save error:", e)

def start_productivity_tracking():
    global _productivity_thread

    if _productivity_thread and _productivity_thread.is_alive():
        speak("Productivity tracking is already running.")
        return

    _productivity_stop.clear()
    _productivity_thread = threading.Thread(
        target=_productivity_worker,
        daemon=True
    )
    _productivity_thread.start()
    speak("Productivity tracking started.")

def stop_productivity_tracking():
    _productivity_stop.set()
    speak("Productivity tracking stopped.")

def show_productivity_report():
    try:
        data = json.loads(PRODUCTIVITY_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        speak("No productivity report is available yet.")
        return

    today = time.strftime("%Y-%m-%d")
    daily = data.get(today, {})
    if not daily:
        speak("No tracked app usage found for today.")
        return

    print("\n===== TODAY'S APP USAGE =====")
    for app, seconds in sorted(
        daily.items(), key=lambda item: item[1], reverse=True
    ):
        print(f"{app}: {seconds / 60:.1f} minutes")
    print("=============================\n")
    speak("Today's productivity report is ready. Check the terminal.")

# =========================================================
# TIME / DATE
# =========================================================

def tell_time():

    speak(
        "The current time is "
        + time.strftime("%I:%M %p")
    )


def tell_date():

    speak(
        "Today's date is "
        + time.strftime("%A, %d %B %Y")
    )


def create_voice_note():
    try:
        notes_folder = Path.home() / "Documents" / "VoiceNotes"
        notes_folder.mkdir(parents=True, exist_ok=True)

        speak("What should I write in your note?")
        note_text = voice_input("Speak your note now.")

        if not note_text or not note_text.strip():
            speak("No note received. Nothing was saved.")
            return

        filename = time.strftime("Note_%Y%m%d_%H%M%S.txt")
        note_path = notes_folder / filename

        with open(note_path, "w", encoding="utf-8") as file:
            file.write(note_text.strip())

        print("Note saved at:", note_path)
        speak("Your voice note has been saved successfully.")

    except Exception as e:
        print("Voice note error:", repr(e))
        speak("Sorry, I could not save your note.")


# =========================================================
# LEVEL 2 - BATTERY
# =========================================================

def battery_status():

    try:

        import psutil

        battery = (
            psutil.sensors_battery()
        )

        if battery is None:

            speak(
                "Battery information is "
                "not available."
            )

            return

        percent = int(
            battery.percent
        )

        status = (
            "charging"
            if battery.power_plugged
            else "not charging"
        )

        speak(
            f"Battery is {percent} "
            f"percent and {status}."
        )

    except ImportError:

        speak(
            "Please install psutil "
            "for battery information."
        )

        print(
            "Run: python -m pip install psutil"
        )


# =========================================================
# SYSTEM INFORMATION
# =========================================================

def system_information():
    try:
        # Computer name
        computer_name = platform.node()

        # Operating system
        os_name = platform.system()
        os_version = platform.release()
        os_full = platform.platform()

        # CPU
        cpu = platform.processor()

        # Architecture
        architecture = platform.machine()

        if architecture.upper() in ["AMD64", "X86_64"]:
            architecture_text = "64 bit"
        elif architecture.upper() in ["X86", "I386", "I686"]:
            architecture_text = "32 bit"
        elif architecture.upper() == "ARM64":
            architecture_text = "ARM 64 bit"
        else:
            architecture_text = architecture

        # RAM
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)"
                ],
                capture_output=True,
                text=True,
                timeout=5
            )

            ram_gb = result.stdout.strip()

            if not ram_gb:
                ram_gb = "unknown"

        except Exception:
            ram_gb = "unknown"

        # =========================
        # TERMINAL OUTPUT
        # =========================

        print("\n===== SYSTEM INFORMATION =====")
        print("Computer:", computer_name)
        print("OS:", os_full)
        print("CPU:", cpu)
        print("RAM:", ram_gb, "GB")
        print("Architecture:", architecture_text)
        print("==============================")

        # =========================
        # VOICE OUTPUT
        # =========================

        speak(
            f"System is {os_name} {os_version}. "
            f"Processor is {cpu}. "
            f"RAM is {ram_gb} gigabytes. "
            f"Computer name is {computer_name}. "
            f"System architecture is {architecture_text}."
        )

    except Exception as e:

        print("System information error:", e)

        speak(
            "I could not read system information."
        )

# =========================================================
# LEVEL 2 - WIFI
# =========================================================

def wifi_status():

    try:

        result = subprocess.run(
            [
                "netsh",
                "wlan",
                "show",
                "interfaces"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            shell=False
        )

        output = result.stdout

        if (
            "State" in output
            and "connected" in output.lower()
        ):

            ssid = ""

            for line in output.splitlines():

                stripped = line.strip()

                if (
                    stripped.lower().startswith(
                        "ssid"
                    )
                    and "bssid"
                    not in stripped.lower()
                ):

                    if ":" in stripped:

                        ssid = (
                            stripped
                            .split(
                                ":",
                                1
                            )[1]
                            .strip()
                        )

                    break

            if ssid:

                speak(
                    "Wi-Fi is connected to "
                    + ssid
                )

            else:

                speak(
                    "Wi-Fi is connected."
                )

        else:

            speak(
                "Wi-Fi does not appear "
                "to be connected."
            )

    except Exception as e:

        print(e)

        speak(
            "I could not check "
            "Wi-Fi status."
        )


# =========================================================
# LOCK / RESTART / SHUTDOWN
# =========================================================

def lock_computer():

    speak(
        "Locking computer."
    )

    ctypes.windll.user32.LockWorkStation()


def restart_computer():

    speak(
        "Are you sure you want "
        "to restart the computer?"
    )

    answer = listen()

    if (
        "yes" in answer
        or "confirm" in answer
        or "haan" in answer
        or answer == "ha"
    ):

        speak(
            "Restarting computer "
            "in five seconds."
        )

        os.system(
            "shutdown /r /t 5"
        )

    else:

        speak(
            "Restart cancelled."
        )


def shutdown_computer():

    speak(
        "Are you sure you want "
        "to shut down the computer?"
    )

    answer = listen()

    if (
        "yes" in answer
        or "confirm" in answer
        or "haan" in answer
        or answer == "ha"
    ):

        speak(
            "Shutting down computer "
            "in five seconds."
        )

        os.system(
            "shutdown /s /t 5"
        )

    else:

        speak(
            "Shutdown cancelled."
        )
# =========================================================
# LEVEL 2 - VOICE FILE MANAGER
# =========================================================
def get_folder_path(name):
    name = name.strip().lower()

    folders = {
        "desktop": get_real_desktop(),
        "downloads": Path.home() / "Downloads",
        "download": Path.home() / "Downloads",

        "documents": Path.home() / "Documents",
        "document": Path.home() / "Documents",

        "pictures": Path.home() / "Pictures",
        "picture": Path.home() / "Pictures",

        "videos": Path.home() / "Videos",
        "video": Path.home() / "Videos",

        "music": Path.home() / "Music"
    }

    # Normal Windows Desktop/Downloads etc.
    if name in folders:
        path = folders[name]

        if path.exists():
            return path

        # OneDrive fallback
        onedrive = os.environ.get("OneDrive")

        if onedrive:
            onedrive_folders = {
                "desktop": "Desktop",
                "downloads": "Downloads",
                "download": "Downloads",
                "documents": "Documents",
                "document": "Documents",
                "pictures": "Pictures",
                "videos": "Videos",
                "music": "Music"
            }

            folder_name = onedrive_folders.get(name)

            if folder_name:
                path = Path(onedrive) / folder_name

                if path.exists():
                    return path

    return None


def get_real_desktop():
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "[Environment]::GetFolderPath('Desktop')"
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        desktop = result.stdout.strip()

        if desktop:
            return Path(desktop)

    except Exception as e:
        print("Desktop detection error:", e)

    return Path.home() / "Desktop"


def create_folder_voice(name):
    name = name.strip()

    if not name:
        speak("Please tell me the folder name.")
        return

    desktop = get_real_desktop()
    folder_path = desktop / name

    try:
        desktop.mkdir(parents=True, exist_ok=True)

        folder_path.mkdir(
            parents=True,
            exist_ok=False
        )

        print("Created folder:")
        print(folder_path)

        speak(
            f"Folder {name} created successfully."
        )

    except FileExistsError:

        print("Folder already exists:")
        print(folder_path)

        speak(
            f"A folder named {name} already exists."
        )

    except Exception as e:

        print("Create folder error:", e)

        speak(
            "I could not create the folder."
        )

def create_file_voice(name):
    name = name.strip()

    if not name:
        speak("Please tell me the file name.")
        return

    if "." not in Path(name).name:
        name += ".txt"

    desktop = get_real_desktop()
    file_path = desktop / name

    try:
        desktop.mkdir(parents=True, exist_ok=True)

        file_path.touch(exist_ok=False)

        print("Created file:")
        print(file_path)

        speak(f"File {name} created on Desktop.")

    except FileExistsError:
        print("File already exists:")
        print(file_path)

        speak(f"A file named {name} already exists.")

    except Exception as e:
        print("Create file error:", e)
        speak("I could not create the file.")


def search_file_voice(name):
    name = name.strip().lower()

    if not name:
        speak("Please tell me the file or folder name.")
        return

    locations = [
        get_real_desktop(),
        Path.home() / "Downloads",
        Path.home() / "Documents",
        Path.home() / "Pictures",
        Path.home() / "Videos",
        Path.home() / "Music"
    ]

    found = []

    for location in locations:

        if not location.exists():
            continue

        try:
            for item in location.rglob("*"):

                if name in item.name.lower():
                    found.append(item)

                    if len(found) >= 5:
                        break

        except Exception as e:
            print("Search error:", e)

        if len(found) >= 5:
            break

    if not found:
        speak(f"I could not find {name}.")
        return

    print("\nFound:")

    for item in found:
        if item.is_dir():
            print("[FOLDER]", item)
        else:
            print("[FILE]", item)

    # First matching result open
    try:
        os.startfile(str(found[0]))

        if found[0].is_dir():
            speak(f"I found and opened the folder {found[0].name}.")
        else:
            speak(f"I found and opened {found[0].name}.")

    except Exception as e:
        print("Open search result error:", e)
        speak(f"I found {found[0].name}.")

def rename_file_voice(old_name, new_name):
    old_name = old_name.strip()
    new_name = new_name.strip()

    locations = [
        Path.home() / "Desktop",
        Path.home() / "Downloads",
        Path.home() / "Documents"
    ]

    for location in locations:

        if not location.exists():
            continue

        try:
            for item in location.rglob("*"):

                if item.name.lower() == old_name.lower():

                    new_path = item.parent / new_name
                    item.rename(new_path)

                    speak(
                        f"Renamed {old_name} to {new_name}."
                    )

                    return

        except Exception as e:
            print("Rename error:", e)

    speak(f"I could not find {old_name}.")


def delete_file_voice(name):
    name = name.strip()

    locations = [
        Path.home() / "Desktop",
        Path.home() / "Downloads",
        Path.home() / "Documents"
    ]

    found = None

    for location in locations:

        if not location.exists():
            continue

        try:
            for item in location.rglob("*"):

                if item.name.lower() == name.lower():
                    found = item
                    break

        except Exception as e:
            print("Delete search error:", e)

        if found:
            break

    if not found:
        speak(f"I could not find {name}.")
        return

    speak(
        f"I found {found.name}. "
        f"Do you want me to delete it?"
    )

    answer = listen()

    if (
        "yes" in answer
        or "haan" in answer
        or answer == "ha"
        or "confirm" in answer
    ):

        try:
            if found.is_dir():
                found.rmdir()
            else:
                found.unlink()

            speak(f"{name} deleted.")

        except Exception as e:
            print("Delete error:", e)
            speak("I could not delete that file.")

    else:
        speak("Delete cancelled.")
# =========================================================
# LEVEL 2 - FOLDER RENAME & DELETE
# =========================================================

def find_folder_voice(name):
    name = name.strip().lower()

    locations = [
        get_real_desktop(),
        Path.home() / "Downloads",
        Path.home() / "Documents",
        Path.home() / "Pictures",
        Path.home() / "Videos",
        Path.home() / "Music"
    ]

    for location in locations:

        if not location.exists():
            continue

        try:
            for item in location.rglob("*"):

                if item.is_dir() and item.name.lower() == name:
                    return item

        except Exception as e:
            print("Folder search error:", e)

    return None


def rename_folder_voice(old_name, new_name):

    folder = find_folder_voice(old_name)

    if not folder:
        speak(f"I could not find the folder {old_name}.")
        return

    new_path = folder.parent / new_name

    try:
        folder.rename(new_path)

        speak(
            f"Folder {old_name} renamed to {new_name}."
        )

        print("Renamed folder:")
        print(new_path)

    except Exception as e:

        print("Rename folder error:", e)

        speak("I could not rename the folder.")


def delete_folder_voice(name):

    folder = find_folder_voice(name)

    if not folder:
        speak(f"I could not find the folder {name}.")
        return

    speak(
        f"I found the folder {folder.name}. "
        f"Do you want me to delete it?"
    )

    answer = listen()

    if (
        "yes" in answer
        or "haan" in answer
        or answer == "ha"
        or "confirm" in answer
    ):

        try:

            folder.rmdir()

            speak(
                f"Folder {name} deleted."
            )

        except OSError:

            speak(
                "The folder is not empty. "
                "I will not delete it."
            )

        except Exception as e:

            print("Delete folder error:", e)

            speak(
                "I could not delete the folder."
            )

    else:

        speak("Delete cancelled.")

def move_file_voice(name, destination):
    name = name.strip()
    destination = destination.strip().lower()

    destination_path = get_folder_path(destination)

    if not destination_path:
        speak(
            "I only support Desktop, Downloads, "
            "Documents, Pictures, Videos and Music."
        )
        return

    if not destination_path.exists():
        speak("The destination folder does not exist.")
        return

    locations = [
        Path.home() / "Desktop",
        Path.home() / "Downloads",
        Path.home() / "Documents",
        Path.home() / "Pictures",
        Path.home() / "Videos",
        Path.home() / "Music"
    ]

    for location in locations:

        if not location.exists():
            continue

        try:
            for item in location.rglob("*"):

                if item.name.lower() == name.lower():

                    new_path = destination_path / item.name
                    item.rename(new_path)

                    speak(
                        f"Moved {item.name} to {destination}."
                    )

                    return

        except Exception as e:
            print("Move error:", e)

    speak(f"I could not find {name}.")


# =========================================================
# LEVEL 2 - COPY / MOVE FOLDER / FILE LOCATION
# =========================================================

import shutil


def ask_overwrite(destination):
    if not destination.exists():
        return True

    speak(
        f"{destination.name} already exists. "
        "Do you want to replace it?"
    )

    answer = listen().lower()

    return (
        "yes" in answer
        or "haan" in answer
        or answer == "ha"
        or "confirm" in answer
    )


def find_item_voice(name):
    name = name.strip().lower()

    
    locations = [
        get_real_desktop(),
        Path.home() / "Downloads",
        Path.home() / "Documents",
        Path.home() / "Pictures",
        Path.home() / "Videos",
        Path.home() / "Music",
        Path("C:/"),
        Path("D:/")
    ]


    for location in locations:

        if not location.exists():
            continue

        try:
            for item in location.rglob("*"):

                
                normalize = lambda text: "".join(
                    ch for ch in text.lower() if ch.isalnum()
                )

                if normalize(item.name) == normalize(name):
                    return item

                    return item

        except Exception as e:
            print("Find item error:", e)

    return None


def open_project_by_name(project_name):
    project_name = project_name.strip()

    item = find_item_voice(project_name)

    if not item:
        speak(f"I could not find the project {project_name}.")
        return False

    if not item.is_dir():
        speak(f"{project_name} is not a folder.")
        return False

    try:
        os.startfile(str(item))
        speak(f"Opening project {item.name}.")
        return True
    except OSError as e:
        print("Project open error:", repr(e))
        speak("Sorry, I could not open the project.")
        return False


def copy_file_voice(name, destination):
    source = find_item_voice(name)

    if not source:
        speak(f"I could not find {name}.")
        return

    if source.is_dir():
        speak(f"{name} is a folder. Use copy folder instead.")
        return

    destination_path = get_folder_path(destination)

    if not destination_path:
        speak("I could not find that destination folder.")
        return

    destination_file = destination_path / source.name

    if not ask_overwrite(destination_file):
        speak("Copy cancelled.")
        return

    try:
        shutil.copy2(source, destination_file)

        speak(
            f"{source.name} copied to {destination}."
        )

    except Exception as e:
        print("Copy file error:", e)
        speak("I could not copy the file.")


def move_folder_voice(name, destination):
    source = find_item_voice(name)

    if not source:
        speak(f"I could not find the folder {name}.")
        return

    if not source.is_dir():
        speak(f"{name} is not a folder.")
        return

    destination_path = get_folder_path(destination)

    if not destination_path:
        speak("I could not find that destination folder.")
        return

    destination_folder = destination_path / source.name

    if not ask_overwrite(destination_folder):
        speak("Move cancelled.")
        return

    try:

        if destination_folder.exists():
            shutil.rmtree(destination_folder)

        shutil.move(
            str(source),
            str(destination_folder)
        )

        speak(
            f"Folder {source.name} moved to {destination}."
        )

    except Exception as e:
        print("Move folder error:", e)
        speak("I could not move the folder.")


def copy_folder_voice(name, destination):
    source = find_item_voice(name)

    if not source:
        speak(f"I could not find the folder {name}.")
        return

    if not source.is_dir():
        speak(f"{name} is not a folder.")
        return

    destination_path = get_folder_path(destination)

    if not destination_path:
        speak("I could not find that destination folder.")
        return

    destination_folder = destination_path / source.name

    if destination_folder.exists():

        if not ask_overwrite(destination_folder):
            speak("Copy cancelled.")
            return

        try:
            shutil.rmtree(destination_folder)

        except Exception as e:
            print("Remove old folder error:", e)
            speak("I could not replace the existing folder.")
            return

    try:

        shutil.copytree(
            source,
            destination_folder
        )

        speak(
            f"Folder {source.name} copied to {destination}."
        )

    except Exception as e:
        print("Copy folder error:", e)
        speak("I could not copy the folder.")


def where_is_file_voice(name):
    item = find_item_voice(name)

    if not item:
        speak(f"I could not find {name}.")
        return

    print("Exact location:")
    print(item.resolve())

    speak(
        f"I found {item.name}. "
        f"It is located in {item.parent}."
    )


def open_file_location_voice(name):
    item = find_item_voice(name)

    if not item:
        speak(f"I could not find {name}.")
        return

    try:

        os.startfile(str(item.parent))

        speak(
            f"Opening the location of {item.name}."
        )

    except Exception as e:
        print("Open location error:", e)
        speak("I could not open the file location.")
            

# =========================================================
# QUESTION / WRITING
# =========================================================

def is_question(command):

    keywords = [

        "who",
        "what",
        "when",
        "where",
        "why",
        "how",
        "which",
        "whose",

        "is",
        "are",
        "can",
        "could",
        "should",

        "tell me",
        "tell",
        "explain",
        "define",
        "meaning",
        "what is",
        "who is",
        "how to",

        "kaun",
        "kya",
        "kab",
        "kahan",
        "kyun",
        "kyu",
        "kaise",
        "kis",
        "kitna",
        "kitni",
        "batao",
        "bata",
        "samjhao",
        "kya hai",
        "kaun hai",

        "write",
        "writing",
        "essay",
        "paragraph",
        "article",
        "letter",
        "application",
        "email",
        "story",
        "poem",
        "shayari",
        "speech",
        "report",
        "resume",
        "cover letter",

        "solve",
        "solution",
        "answer",
        "notes",
        "definition",
        "difference",
        "advantages",
        "disadvantages",
        "example",
        "formula",
        "program",
        "code",
        "algorithm",

        "likho",
        "likh do",
        "likh",
        "nibandh",
        "patra",
        "kahani",
        "kavita",
        "bhashan",
        "jawab"
    ]

    return any(
        word in command
        for word in keywords
    )
# =========================================================
# LEVEL 2 - STORAGE / DISK STATUS
# =========================================================

def get_storage_info(drive="C:"):
    try:
        total, used, free = shutil.disk_usage(drive)

        total_gb = total / (1024 ** 3)
        used_gb = used / (1024 ** 3)
        free_gb = free / (1024 ** 3)

        usage_percent = (used / total) * 100

        print("\n===== STORAGE STATUS =====")
        print(f"Drive: {drive}")
        print(f"Total: {total_gb:.2f} GB")
        print(f"Used : {used_gb:.2f} GB")
        print(f"Free : {free_gb:.2f} GB")
        print(f"Usage: {usage_percent:.1f}%")
        print("==========================\n")

        speak(
            f"{drive} drive has "
            f"{free_gb:.1f} gigabytes free "
            f"out of {total_gb:.1f} gigabytes."
        )

    except Exception as e:
        print("Storage error:", e)
        speak("I could not check the storage.")


def storage_status_voice():
    get_storage_info("C:")

def get_all_drives_storage():

    try:

        drives = []

        # Windows logical drives
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-PSDrive -PSProvider FileSystem).Name"
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        for drive in result.stdout.split():

            drive = drive.strip().upper()

            if drive:
                drives.append(drive + ":")

        if not drives:
            speak("I could not detect the drives.")
            return

        print("\n===== ALL DRIVE STORAGE =====")

        for drive in drives:

            try:

                total, used, free = shutil.disk_usage(drive)

                total_gb = total / (1024 ** 3)
                used_gb = used / (1024 ** 3)
                free_gb = free / (1024 ** 3)

                usage = (used / total) * 100

                print(
                    f"{drive} | "
                    f"Total: {total_gb:.1f} GB | "
                    f"Used: {used_gb:.1f} GB | "
                    f"Free: {free_gb:.1f} GB | "
                    f"Usage: {usage:.1f}%"
                )

            except Exception as e:

                print(
                    f"{drive} | Unable to read"
                )

        print("==============================\n")

        speak(
            f"I found {len(drives)} drives. "
            "I have displayed their storage information."
        )

    except Exception as e:

        print("All drives error:", e)

        speak(
            "I could not check all drives."
        )
# =========================================================
# LEVEL 2 - SYSTEM INFORMATION
# =========================================================

import platform

def get_system_info():
    try:
        computer_name = platform.node()
        windows_version = platform.platform()
        cpu = platform.processor()

        # Get system architecture
        architecture = platform.machine()

        if architecture.upper() in ["AMD64", "X86_64"]:
            architecture_voice = "64 bit"
        elif architecture.upper() in ["X86", "I386", "I686"]:
            architecture_voice = "32 bit"
        elif architecture.upper() == "ARM64":
            architecture_voice = "ARM 64 bit"
        else:
            architecture_voice = architecture

        # RAM
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)"
                ],
                capture_output=True,
                text=True,
                timeout=5
            )

            ram_gb = result.stdout.strip()

        except Exception:
            ram_gb = "unknown"

        # Terminal output
        print("\n===== SYSTEM INFORMATION =====")
        print(f"Computer Name : {computer_name}")
        print(f"Windows       : {windows_version}")
        print(f"CPU           : {cpu}")
        print(f"RAM           : {ram_gb} GB")
        print(f"Architecture  : {architecture_voice}")
        print("===============================\n")

        # Voice output
        speak(
            f"System is {windows_version}. "
            f"Processor is {cpu}. "
            f"RAM is {ram_gb} gigabytes. "
            f"System architecture is {architecture_voice}."
        )

    except Exception as e:
        print("System information error:", e)
        speak("I could not get the system information.")

# =========================================================
# LEVEL 2 - BATTERY INFORMATION
# =========================================================

def battery_information():
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                """
                Get-CimInstance Win32_Battery |
                Select-Object EstimatedChargeRemaining, BatteryStatus |
                ConvertTo-Json -Compress
                """
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        output = result.stdout.strip()

        if not output:
            speak("I could not detect a battery on this computer.")
            return

        import json

        data = json.loads(output)

        # PowerShell single object
        if isinstance(data, dict):
            batteries = [data]
        else:
            batteries = data

        charge = batteries[0].get(
            "EstimatedChargeRemaining"
        )

        status = batteries[0].get(
            "BatteryStatus"
        )

        # Battery status codes
        status_text = {
            1: "discharging",
            2: "charging",
            3: "fully charged",
            4: "charging",
            5: "charging",
            6: "charging",
            7: "charging",
            8: "charging",
            9: "charging",
            10: "charging",
            11: "charging"
        }

        current_status = status_text.get(
            status,
            "status unknown"
        )

        print("\n===== BATTERY INFORMATION =====")
        print(f"Battery : {charge}%")
        print(f"Status  : {current_status}")
        print("===============================\n")

        speak(
            f"Battery is at {charge} percent "
            f"and it is {current_status}."
        )

    except Exception as e:

        print("Battery information error:", e)

        speak(
            "I could not read the battery information."
        )
# =========================================================
# LEVEL 3 - CLIPBOARD CONTROL
# =========================================================

def clipboard_read():
    try:
        text = pyperclip.paste()

        if not text:
            speak("The clipboard is empty.")
            return

        print("\n===== CLIPBOARD =====")
        print(text)
        print("=====================\n")

        # बहुत लंबा text voice में नहीं पढ़ेंगे
        if len(text) > 200:
            speak(
                "The clipboard contains text. "
                "I have displayed it on the screen."
            )
        else:
            speak("The clipboard contains " + text)

    except Exception as e:
        print("Clipboard read error:", e)
        speak("I could not read the clipboard.")


def clipboard_clear():
    try:
        pyperclip.copy("")

        speak("Clipboard cleared.")

    except Exception as e:
        print("Clipboard clear error:", e)
        speak("I could not clear the clipboard.")


def clipboard_paste():
    try:
        text = pyperclip.paste()

        if not text:
            speak("The clipboard is empty.")
            return

        import pyautogui
        import time

        # Current active window ko focus rehne do
        time.sleep(0.5)

        pyautogui.hotkey("ctrl", "v")

        time.sleep(0.5)

        speak("Pasted successfully.")

    except Exception as e:
        print("Clipboard paste error:", e)
        speak("I could not paste the clipboard content.")

# =========================================================
# LEVEL 3 - RUNNING APPS / CPU / RAM MONITOR
# =========================================================

def running_apps():
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-Process | "
                "Sort-Object CPU -Descending | "
                "Select-Object -First 10 ProcessName, Id | "
                "Format-Table -AutoSize"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stdout.strip()

        if not output:
            speak("I could not find running applications.")
            return

        print("\n===== RUNNING APPS =====")
        print(output)
        print("========================\n")

        speak(
            "I found the running applications. "
            "I have displayed the top processes on the screen."
        )

    except Exception as e:
        print("Running apps error:", e)
        speak("I could not read the running applications.")


def top_cpu_processes():
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-Process | "
                "Where-Object {$_.CPU -ne $null} | "
                "Sort-Object CPU -Descending | "
                "Select-Object -First 5 ProcessName, CPU | "
                "Format-Table -AutoSize"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stdout.strip()

        if not output:
            speak("I could not read CPU usage.")
            return

        print("\n===== TOP CPU PROCESSES =====")
        print(output)
        print("=============================\n")

        speak(
            "I have displayed the top processes using the CPU."
        )

    except Exception as e:
        print("CPU monitor error:", e)
        speak("I could not read CPU usage.")


def top_ram_processes():
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-Process | "
                "Sort-Object WorkingSet64 -Descending | "
                "Select-Object -First 5 ProcessName, "
                "@{Name='RAM_MB';Expression={[math]::Round($_.WorkingSet64 / 1MB, 1)}} | "
                "Format-Table -AutoSize"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stdout.strip()

        if not output:
            speak("I could not read RAM usage.")
            return

        print("\n===== TOP RAM PROCESSES =====")
        print(output)
        print("=============================\n")

        speak(
            "I have displayed the top processes using RAM."
        )

    except Exception as e:
        print("RAM monitor error:", e)
        speak("I could not read RAM usage.")      
# =========================================================
# LEVEL 3 - ADVANCED FILE SEARCH
# =========================================================

def find_pdf_files():
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-ChildItem -Path $env:USERPROFILE -Filter *.pdf -File -Recurse -ErrorAction SilentlyContinue | Select-Object -First 20 FullName"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout.strip()

        if not output:
            speak("I could not find any PDF files.")
            return

        print("\n===== PDF FILES =====")
        print(output)
        print("====================\n")

        speak("I found PDF files. I have displayed their locations.")

    except Exception as e:
        print("PDF search error:", e)
        speak("I could not search for PDF files.")


def find_large_files():
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-ChildItem -Path $env:USERPROFILE -File -Recurse -ErrorAction SilentlyContinue | Where-Object {$_.Length -gt 100MB} | Sort-Object Length -Descending | Select-Object -First 20 FullName,@{Name='Size_MB';Expression={[math]::Round($_.Length/1MB,2)}}"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout.strip()

        if not output:
            speak("I could not find files larger than 100 megabytes.")
            return

        print("\n===== LARGE FILES =====")
        print(output)
        print("=======================\n")

        speak("I found files larger than 100 megabytes.")

    except Exception as e:
        print("Large file search error:", e)
        speak("I could not search for large files.")


def find_files_today():
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-ChildItem -Path $env:USERPROFILE -File -Recurse -ErrorAction SilentlyContinue | Where-Object {$_.LastWriteTime.Date -eq (Get-Date).Date} | Select-Object -First 20 FullName,LastWriteTime"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout.strip()

        if not output:
            speak("I could not find files modified today.")
            return

        print("\n===== FILES MODIFIED TODAY =====")
        print(output)
        print("================================\n")

        speak("I found files modified today.")

    except Exception as e:
        print("Today's file search error:", e)
        speak("I could not search for today's files.")

# =========================================================
# LEVEL 3 - STUDY SETUP AUTOMATION
# =========================================================

def study_setup():
    try:
        speak("Starting your study setup.")

        # Chrome
        subprocess.Popen(
            ["cmd", "/c", "start", "", "chrome"],
            shell=False
        )

        time.sleep(2)

        # Brave
        subprocess.Popen(
            ["cmd", "/c", "start", "", "brave"],
            shell=False
        )

        time.sleep(2)

        # VS Code
        subprocess.Popen(
            ["cmd", "/c", "start", "", "code"],
            shell=False
        )

        time.sleep(2)

        # File Explorer
        subprocess.Popen(
            "explorer.exe"
        )

        time.sleep(2)

        speak("Study setup started successfully.")

    except Exception as e:
        print("Study setup error:", e)
        speak("I could not start the study setup.")

# =========================================================
# LEVEL 3 - SYSTEM HEALTH REPORT
# =========================================================

def system_health_report():
    try:
        import psutil

        # CPU
        cpu_usage = psutil.cpu_percent(interval=1)

        # RAM
        memory = psutil.virtual_memory()
        ram_usage = memory.percent
        ram_used = round(memory.used / (1024 ** 3), 2)
        ram_total = round(memory.total / (1024 ** 3), 2)

        # Disk
        disk = psutil.disk_usage("C:\\")
        disk_usage = disk.percent
        disk_free = round(disk.free / (1024 ** 3), 2)

        # Battery
        battery = psutil.sensors_battery()

        if battery:
            battery_percent = battery.percent

            if battery.power_plugged:
                battery_status = "charging"
            else:
                battery_status = "not charging"
        else:
            battery_percent = "unknown"
            battery_status = "unknown"

        # Network
        network = psutil.net_io_counters()

        print("\n================================")
        print("       SYSTEM HEALTH REPORT")
        print("================================")
        print(f"CPU Usage       : {cpu_usage}%")
        print(f"RAM Usage       : {ram_usage}%")
        print(f"RAM             : {ram_used} GB / {ram_total} GB")
        print(f"C Drive Usage   : {disk_usage}%")
        print(f"C Drive Free    : {disk_free} GB")
        print(f"Battery         : {battery_percent}%")
        print(f"Battery Status  : {battery_status}")
        print("Network         : Connected / Available")
        print("================================\n")

        speak(
            f"System health report. "
            f"CPU usage is {cpu_usage} percent. "
            f"RAM usage is {ram_usage} percent. "
            f"C drive usage is {disk_usage} percent. "
            f"Battery is {battery_percent} percent."
        )

    except Exception as e:
        print("System health error:", e)
        speak("I could not generate the system health report.")
# =========================================================
# LEVEL 3 - PERFORMANCE MONITOR
# =========================================================

def performance_monitor():
    try:
        import psutil
        import time

        print("\n================================")
        print("       PERFORMANCE MONITOR")
        print("================================")

        print("Monitoring system for 5 seconds...\n")

        for i in range(5):
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent

            print(f"CPU: {cpu}%   |   RAM: {ram}%")

        # Top CPU processes
        processes = []

        for process in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent"]
        ):
            try:
                processes.append(process.info)
            except:
                pass

        processes.sort(
            key=lambda x: x["cpu_percent"] or 0,
            reverse=True
        )

        print("\nTop CPU Processes:")
        print("--------------------------")

        for p in processes[:5]:
            print(
                f"{p['name']} "
                f"(PID: {p['pid']}) - "
                f"CPU: {p['cpu_percent']}%"
            )

        print("================================\n")

        speak("Performance monitoring completed.")

    except Exception as e:
        print("Performance monitor error:", e)
        speak("I could not monitor system performance.")

# =========================================================
# LEVEL 3 - SMART SYSTEM ALERT
# =========================================================

def check_system_alerts():
    try:
        import psutil

        cpu = psutil.cpu_percent(interval=1)

        memory = psutil.virtual_memory()
        ram = memory.percent

        disk = psutil.disk_usage("C:\\")
        disk_percent = disk.percent

        battery = psutil.sensors_battery()

        alerts = []

        # CPU Alert
        if cpu > 80:
            alerts.append(f"CPU usage is high at {cpu}%")

        # RAM Alert
        if ram > 80:
            alerts.append(f"RAM usage is high at {ram}%")

        # Disk Alert
        if disk_percent > 90:
            alerts.append(f"C drive usage is critical at {disk_percent}%")

        # Battery Alert
        if battery and battery.percent < 20 and not battery.power_plugged:
            alerts.append(f"Battery is low at {battery.percent}%")

        print("\n================================")
        print("       SMART SYSTEM ALERT")
        print("================================")

        if alerts:
            print("⚠️ ALERTS FOUND:\n")

            for alert in alerts:
                print("⚠️", alert)

            print("================================\n")

            speak("System alerts detected. Please check the terminal.")

        else:
            print("✅ No critical system alerts.")
            print("CPU:", cpu, "%")
            print("RAM:", ram, "%")
            print("Disk:", disk_percent, "%")

            if battery:
                print("Battery:", battery.percent, "%")

            print("================================\n")

            speak("No critical system alerts detected.")

    except Exception as e:
        print("System alert error:", e)
        speak("I could not check system alerts.")

# =========================================================
# LEVEL 3 - SMART RESOURCE ADVISOR
# =========================================================

def smart_resource_advisor():
    try:
        import psutil

        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("C:\\")
        disk_percent = disk.percent

        battery = psutil.sensors_battery()

        print("\n================================")
        print("      SMART RESOURCE ADVISOR")
        print("================================")

        recommendations = []

        # CPU
        if cpu >= 80:
            recommendations.append(
                "CPU usage is high. Close unnecessary applications."
            )
        else:
            print(f"✅ CPU usage is normal: {cpu}%")

        # RAM
        if ram >= 80:
            recommendations.append(
                "RAM usage is high. Close unused applications and browser tabs."
            )
        else:
            print(f"✅ RAM usage is normal: {ram}%")

        # Disk
        if disk_percent >= 90:
            recommendations.append(
                "C drive is almost full. Delete unnecessary files."
            )
        else:
            print(f"✅ C drive usage is normal: {disk_percent}%")

        # Battery
        if battery:
            battery_percent = battery.percent

            if battery_percent < 20 and not battery.power_plugged:
                recommendations.append(
                    "Battery is low. Connect the charger."
                )
            else:
                print(f"✅ Battery: {battery_percent}%")

        # Recommendations
        if recommendations:
            print("\n💡 RECOMMENDATIONS:\n")

            for recommendation in recommendations:
                print("👉", recommendation)

            speak(
                "I found some system resource issues. "
                "Please check the recommendations in the terminal."
            )

        else:
            print("\n🚀 Your system resources look healthy.")
            speak("Your system resources look healthy.")

        print("================================\n")

    except Exception as e:
        print("Smart advisor error:", e)
        speak("I could not analyze your system resources.")

# =========================================================
# LEVEL 3 - SECURITY CHECK
# =========================================================

def security_check():
    try:
        import subprocess

        print("\n================================")
        print("       SECURITY CHECK")
        print("================================")

        # Windows Firewall
        firewall = subprocess.run(
            ["powershell", "-Command",
             "Get-NetFirewallProfile | Select-Object Name, Enabled"],
            capture_output=True,
            text=True
        )

        print("\n🔥 Windows Firewall:")
        print(firewall.stdout.strip())

        # Microsoft Defender
        defender = subprocess.run(
            ["powershell", "-Command",
             "Get-MpComputerStatus | Select-Object "
             "AntivirusEnabled, RealTimeProtectionEnabled"],
            capture_output=True,
            text=True
        )

        print("\n🛡️ Microsoft Defender:")
        print(defender.stdout.strip())

        # Windows Update service
        update = subprocess.run(
            ["powershell", "-Command",
             "(Get-Service wuauserv).Status"],
            capture_output=True,
            text=True
        )

        print("\n🔄 Windows Update Service:")
        print(update.stdout.strip())

        print("\n================================\n")

        speak("Security check completed. Please check the terminal.")

    except Exception as e:
        print("Security check error:", e)
        speak("I could not complete the security check.")

# =========================================================
# LEVEL 3 - SECURITY STATUS
# =========================================================

def security_status():
    try:
        import subprocess

        # Firewall
        firewall = subprocess.run(
            ["powershell", "-Command",
             "(Get-NetFirewallProfile | Where-Object {$_.Enabled -eq $false}).Count"],
            capture_output=True,
            text=True
        )

        firewall_off = int(firewall.stdout.strip() or 0)
        firewall_status = "ON" if firewall_off == 0 else "CHECK"

        # Defender
        defender = subprocess.run(
            ["powershell", "-Command",
             "(Get-MpComputerStatus).AntivirusEnabled"],
            capture_output=True,
            text=True
        )

        defender_status = (
            "ON" if defender.stdout.strip().lower() == "true"
            else "OFF"
        )

        # Real-time protection
        realtime = subprocess.run(
            ["powershell", "-Command",
             "(Get-MpComputerStatus).RealTimeProtectionEnabled"],
            capture_output=True,
            text=True
        )

        realtime_status = (
            "ON" if realtime.stdout.strip().lower() == "true"
            else "OFF"
        )

        # Windows Update
        update = subprocess.run(
            ["powershell", "-Command",
             "(Get-Service wuauserv).Status"],
            capture_output=True,
            text=True
        )

        update_status = update.stdout.strip()

        print("\n================================")
        print("        SECURITY STATUS")
        print("================================")

        print(f"Firewall       : {firewall_status}")
        print(f"Defender       : {defender_status}")
        print(f"Real-time      : {realtime_status}")
        print(f"Windows Update : {update_status}")

        print("================================\n")

        speak("Security status check completed.")

    except Exception as e:
        print("Security status error:", e)
        speak("I could not check the security status.")
# =========================================================
# LEVEL 3 - START WINDOWS UPDATE
# =========================================================

def start_windows_update():
    try:
        import subprocess

        print("\nStarting Windows Update service...")

        result = subprocess.run(
            [
                "powershell",
                "-Command",
                "Start-Service wuauserv"
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ Windows Update service started successfully.")
            speak("Windows Update service has been started.")
        else:
            print("⚠️ Could not start Windows Update service.")
            print(result.stderr.strip())
            speak("I could not start the Windows Update service.")

    except Exception as e:
        print("Windows Update error:", e)
        speak("There was a problem starting Windows Update.")

# =========================================================
# LEVEL 3 - NETWORK MONITOR
# =========================================================

def network_monitor():
    try:
        import psutil
        import socket

        print("\n================================")
        print("        NETWORK MONITOR")
        print("================================")

        # Internet connectivity
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            internet = "Connected"
        except:
            internet = "Not Connected"

        # Active network interfaces
        stats = psutil.net_if_stats()

        active_adapters = []

        for name, info in stats.items():
            if info.isup:
                active_adapters.append(name)

        # Network traffic
        io = psutil.net_io_counters()

        download_mb = round(io.bytes_recv / (1024 ** 2), 2)
        upload_mb = round(io.bytes_sent / (1024 ** 2), 2)

        print(f"\nInternet       : {internet}")

        print("\nActive Adapters:")
        if active_adapters:
            for adapter in active_adapters:
                print(f"  - {adapter}")
        else:
            print("  None")

        print(f"\nData Received  : {download_mb} MB")
        print(f"Data Sent      : {upload_mb} MB")

        print("================================\n")

        if internet == "Connected":
            speak("Internet is connected.")
        else:
            speak("Internet is not connected.")

    except Exception as e:
        print("Network monitor error:", e)
        speak("I could not check the network.")

# =========================================================
# LEVEL 3 - DOWNLOADS ORGANIZER
# =========================================================

def organize_downloads():
    try:
        import os
        import shutil

        downloads = os.path.join(os.path.expanduser("~"), "Downloads")

        if not os.path.exists(downloads):
            print("❌ Downloads folder not found.")
            speak("Downloads folder was not found.")
            return

        categories = {
            "PDF": [".pdf"],
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"],
            "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
            "Audio": [".mp3", ".wav", ".aac", ".flac", ".m4a"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Code": [".py", ".java", ".cpp", ".c", ".js", ".html", ".css"],
            "Documents": [".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"],
        }

        moved = 0

        print("\n================================")
        print("       DOWNLOADS ORGANIZER")
        print("================================")

        for filename in os.listdir(downloads):

            source = os.path.join(downloads, filename)

            # Skip folders
            if not os.path.isfile(source):
                continue

            extension = os.path.splitext(filename)[1].lower()

            category = "Others"

            for folder, extensions in categories.items():
                if extension in extensions:
                    category = folder
                    break

            destination_folder = os.path.join(downloads, category)

            os.makedirs(destination_folder, exist_ok=True)

            destination = os.path.join(destination_folder, filename)

            # Avoid overwriting existing files
            if os.path.exists(destination):
                name, ext = os.path.splitext(filename)
                counter = 1

                while os.path.exists(destination):
                    new_name = f"{name}_{counter}{ext}"
                    destination = os.path.join(
                        destination_folder,
                        new_name
                    )
                    counter += 1

            shutil.move(source, destination)

            print(f"Moved: {filename} -> {category}")
            moved += 1

        print("\n================================")
        print(f"✅ Total files organized: {moved}")
        print("================================\n")

        speak(f"Downloads organized. {moved} files were moved.")

    except Exception as e:
        print("Downloads organizer error:", e)
        speak("I could not organize the Downloads folder.")

# =========================================================
# LEVEL 3 - DUPLICATE FILE FINDER
# =========================================================

def find_duplicate_files():
    try:
        import os
        import hashlib
        from collections import defaultdict

        search_locations = [
            os.path.join(os.path.expanduser("~"), "Downloads"),
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Documents")
        ]

        file_groups = defaultdict(list)

        print("\n================================")
        print("       DUPLICATE FILE FINDER")
        print("================================")
        print("Scanning files...\n")

        # Scan files
        for location in search_locations:

            if not os.path.exists(location):
                continue

            for root, dirs, files in os.walk(location):

                for filename in files:
                    filepath = os.path.join(root, filename)

                    try:
                        size = os.path.getsize(filepath)

                        # First group by size
                        file_groups[size].append(filepath)

                    except (PermissionError, OSError):
                        continue

        duplicates = []

        # Compare content only for same-size files
        for size, files in file_groups.items():

            if len(files) < 2:
                continue

            hashes = defaultdict(list)

            for filepath in files:

                try:
                    sha256 = hashlib.sha256()

                    with open(filepath, "rb") as f:
                        while True:
                            chunk = f.read(1024 * 1024)

                            if not chunk:
                                break

                            sha256.update(chunk)

                    file_hash = sha256.hexdigest()
                    hashes[file_hash].append(filepath)

                except (PermissionError, OSError):
                    continue

            for file_hash, matching_files in hashes.items():

                if len(matching_files) > 1:
                    duplicates.append(matching_files)

        # Display results
        if not duplicates:

            print("✅ No duplicate files found.")
            print("================================\n")

            speak("No duplicate files were found.")
            return

        print("⚠️ DUPLICATE FILES FOUND:\n")

        total_duplicates = 0

        for group_number, group in enumerate(duplicates, 1):

            print(f"Group {group_number}:")

            for filepath in group:
                print(f"  📄 {filepath}")

            print()

            total_duplicates += len(group) - 1

        print("================================")
        print(f"Duplicate copies: {total_duplicates}")
        print(f"Duplicate groups : {len(duplicates)}")
        print("================================\n")

        speak(
            f"I found {total_duplicates} duplicate file copies."
        )

    except Exception as e:
        print("Duplicate finder error:", e)
        speak("I could not find duplicate files.")

# =========================================================
# LEVEL 3 - SAFE CLEANUP WITH RECYCLE BIN
# =========================================================

def safe_cleanup():
    try:
        import os
        import subprocess

        temp_folder = os.environ.get("TEMP")

        # -----------------------------
        # TEMP FILES SCAN
        # -----------------------------

        temp_files = []
        temp_size = 0

        if temp_folder and os.path.exists(temp_folder):

            for root, dirs, filenames in os.walk(temp_folder):

                for filename in filenames:

                    filepath = os.path.join(root, filename)

                    try:
                        if os.path.isfile(filepath):
                            temp_files.append(filepath)
                            temp_size += os.path.getsize(filepath)
                    except:
                        continue

        temp_size_mb = round(temp_size / (1024 ** 2), 2)

        # -----------------------------
        # RECYCLE BIN SIZE
        # -----------------------------

        recycle_size = 0

        try:
            recycle_command = (
                "(Get-ChildItem 'C:\\$Recycle.Bin' "
                "-Recurse -Force -ErrorAction SilentlyContinue "
                "| Measure-Object Length -Sum).Sum"
            )

            result = subprocess.run(
                ["powershell", "-Command", recycle_command],
                capture_output=True,
                text=True
            )

            value = result.stdout.strip()

            if value and value.replace(".", "", 1).isdigit():
                recycle_size = int(float(value))

        except:
            recycle_size = 0

        recycle_size_mb = round(
            recycle_size / (1024 ** 2), 2
        )

        total_size_mb = round(
            temp_size_mb + recycle_size_mb,
            2
        )

        # -----------------------------
        # SHOW CLEANUP REPORT
        # -----------------------------

        print("\n================================")
        print("       SAFE CLEANUP")
        print("================================")

        print(f"Temporary files : {len(temp_files)}")
        print(f"Temporary size  : {temp_size_mb} MB")
        print(f"Recycle Bin     : {recycle_size_mb} MB")
        print(f"Total cleanup   : {total_size_mb} MB")

        if not temp_files and recycle_size == 0:

            print("\n✅ Nothing to clean.")
            print("================================\n")

            speak("There is nothing to clean.")
            return

        print("\n⚠️ CLEANUP WILL REMOVE:")
        print("• Temporary files")
        print("• Recycle Bin contents")

        print("\n⚠️ Recycle Bin files cannot be restored")
        print("after the cleanup.")

        # -----------------------------
        # CONFIRMATION
        # -----------------------------

        speak(
            f"I found {total_size_mb} megabytes "
            "of cleanup data. "
            "This includes the Recycle Bin. "
            "Do you want to continue?"
        )

        confirmation = input(
            "\nType YES to confirm cleanup: "
        ).strip().lower()

        if confirmation != "yes":

            print("\n❌ Cleanup cancelled.")
            speak("Cleanup cancelled.")
            return

        # -----------------------------
        # DELETE TEMP FILES
        # -----------------------------

        deleted = 0
        failed = 0

        print("\nCleaning temporary files...\n")

        for filepath in temp_files:

            try:
                os.remove(filepath)
                deleted += 1

            except:
                failed += 1

        # -----------------------------
        # EMPTY RECYCLE BIN
        # -----------------------------

        recycle_cleared = False

        try:

            recycle_result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Clear-RecycleBin -Force -ErrorAction Stop"
                ],
                capture_output=True,
                text=True
            )

            if recycle_result.returncode == 0:
                recycle_cleared = True

        except:
            recycle_cleared = False

        # -----------------------------
        # FINAL REPORT
        # -----------------------------

        print("\n================================")
        print("       CLEANUP COMPLETE")
        print("================================")

        print(f"Temporary files deleted : {deleted}")
        print(f"Temporary files skipped : {failed}")

        if recycle_cleared:
            print("Recycle Bin             : Emptied ✅")
        else:
            print("Recycle Bin             : Could not empty ⚠️")

        print("================================\n")

        if recycle_cleared:

            speak(
                f"Cleanup completed. "
                f"{deleted} temporary files were removed "
                "and the Recycle Bin was emptied."
            )

        else:

            speak(
                f"Cleanup completed. "
                f"{deleted} temporary files were removed, "
                "but the Recycle Bin could not be emptied."
            )

    except Exception as e:

        print("Cleanup error:", e)
        speak("I could not complete the cleanup.")

# =========================================================
# LEVEL 3 - SYSTEM ACTIVITY LOG
# =========================================================

import os
from datetime import datetime

ACTIVITY_LOG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "assistant_activity_log.txt"
)


def log_activity(command, action, status="SUCCESS"):
    try:
        time_now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        with open(
            ACTIVITY_LOG_FILE,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                f"[{time_now}] "
                f"Command: {command} | "
                f"Action: {action} | "
                f"Status: {status}\n"
            )

    except Exception as e:
        print("Activity log error:", e)


def show_activity_log():
    try:
        print("\n================================")
        print("       SYSTEM ACTIVITY LOG")
        print("================================")

        if not os.path.exists(ACTIVITY_LOG_FILE):

            print("No activity has been logged yet.")
            print("================================\n")

            speak(
                "There is no activity log yet."
            )

            return

        with open(
            ACTIVITY_LOG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            logs = file.readlines()

        if not logs:

            print("Activity log is empty.")
            print("================================\n")

            speak(
                "The activity log is empty."
            )

            return

        print("\nRecent Activity:\n")

        # Last 20 activities
        for entry in logs[-20:]:

            print(entry.strip())

        print("\n================================\n")

        speak(
            "Here is your recent activity log."
        )

    except Exception as e:

        print(
            "Activity log error:",
            e
        )

        speak(
            "I could not read the activity log."
        )


# =========================================================
# AUTOMATIC COMMAND LOGGER
# =========================================================

def logged_action(command, action):

    log_activity(
        command,
        action,
        "SUCCESS"
    )

# =========================================================
# JOKE FEATURE
# =========================================================

def tell_joke():

    jokes = [
        "Why did the computer go to the doctor? Because it had a virus!",
        
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        
        "Why was the math book sad? Because it had too many problems!",
        
        "What do you call a computer that sings? A Dell!",
        
        "Why did the developer go broke? Because he used up all his cache!",
        
        "Why don't programmers like nature? Because it has too many bugs!"
    ]

    joke = random.choice(jokes)

    print("\n😂 Joke:")
    print(joke)

    speak(joke)


# =========================================================
# CURRENT NEWS HEADLINES
# =========================================================

def get_news_headlines():

    try:

        speak("Fetching the latest news headlines.")

        url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        import xml.etree.ElementTree as ET

        root = ET.fromstring(
            response.content
        )

        items = root.findall(".//item")

        if not items:

            speak("Sorry, I could not find any news headlines.")

            return

        print("\n" + "=" * 60)
        print("📰 LATEST NEWS HEADLINES")
        print("=" * 60)

        headlines = []

        for item in items[:5]:

            title_element = item.find("title")

            if title_element is not None:

                title = title_element.text.strip()

                headlines.append(title)

                print(
                    f"{len(headlines)}. {title}"
                )

        print("=" * 60)

        speak(
            f"I found {len(headlines)} latest news headlines."
        )

        # Read first 3 headlines
        for i, headline in enumerate(
            headlines[:3],
            start=1
        ):

            speak(
                f"Headline {i}. {headline}"
            )

    except requests.exceptions.RequestException:

        print("❌ Internet connection problem.")

        speak(
            "Sorry, I could not connect to the internet."
        )

    except Exception as e:

        print(
            "❌ News error:",
            e
        )

        speak(
            "Sorry, I could not fetch the news."
        )


# =========================================================
# LEVEL 4 - OFFLINE AI MEMORY (JSON)
# =========================================================

MEMORY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "assistant_memory.json"
)


def load_memory():
    default_memory = {
        "paths": {},
        "preferences": {},
        "custom_commands": {}
    }

    try:
        if not os.path.exists(MEMORY_FILE):
            return default_memory

        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return default_memory

        for key in default_memory:
            if not isinstance(data.get(key), dict):
                data[key] = {}

        return data

    except (OSError, json.JSONDecodeError):
        speak("Memory file could not be read.")
        return default_memory


def save_memory(memory):
    try:
        temp_file = MEMORY_FILE + ".tmp"

        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(
                memory,
                file,
                indent=4,
                ensure_ascii=False
            )

        os.replace(temp_file, MEMORY_FILE)
        return True

    except (OSError, TypeError, ValueError):
        speak("Memory could not be saved.")
        return False


def memory_key(value):
    return " ".join(value.lower().strip().split())


def remember_path(name, path):
    name = memory_key(name)
    path = os.path.expandvars(os.path.expanduser(path.strip()))

    if not name or not path:
        speak("Path name and location are required.")
        return False

    memory = load_memory()
    memory["paths"][name] = path

    if save_memory(memory):
        speak("Path remembered for " + name)
        return True

    return False


def open_saved_path(name):
    memory = load_memory()
    name = memory_key(name)

    path = memory["paths"].get(name)

    if not path:
        speak(f"No saved path found for {name}.")
        return False

    if not os.path.exists(path):
        speak("The saved path does not exist.")
        print("Path:", path)
        return False

    try:
        os.startfile(path)
        speak(f"Opening {name}.")
        return True
    except OSError as e:
        print("Open path error:", repr(e))
        speak("Sorry, I could not open the path.")
        return False


def remember_preference(name, value):
    name = memory_key(name)
    value = value.strip()

    if not name or not value:
        speak("Preference name and value are required.")
        return False

    memory = load_memory()
    memory["preferences"][name] = value

    if save_memory(memory):
        speak("Preference saved.")
        return True

    return False


def remember_custom_command(alias, target):
    alias = memory_key(alias)
    target = target.strip().lower()

    if not alias or not target:
        speak("Command name and action are required.")
        return False

    if alias == target:
        speak("Custom command cannot point to itself.")
        return False

    if alias.startswith(("remember ", "forget ", "delete memory")):
        speak("That shortcut name is reserved.")
        return False

    memory = load_memory()
    memory["custom_commands"][alias] = target

    if save_memory(memory):
        speak("Custom command saved.")
        return True

    return False


def show_memory():
    memory = load_memory()

    for section in ("paths", "preferences", "custom_commands"):
        print("\n" + section.upper())

        if not memory[section]:
            print("No saved items.")
            continue

        for name, value in memory[section].items():
            print(f"{name}: {value}")

    speak("Saved memory displayed.")


def forget_memory(section, name):
    sections = {
        "path": "paths",
        "preference": "preferences",
        "command": "custom_commands"
    }

    section = sections.get(memory_key(section))
    name = memory_key(name)

    if not section or not name:
        speak("Please specify what memory to forget.")
        return False

    memory = load_memory()

    if name not in memory[section]:
        speak("That memory was not found.")
        return False

    del memory[section][name]

    if save_memory(memory):
        speak("Memory forgotten.")
        return True

    return False


def resolve_custom_command(command):
    memory = load_memory()
    alias = memory_key(command)

    # Only one-level expansion; avoids command loops.
    target = memory["custom_commands"].get(alias)

    if target and memory_key(target) != alias:
        return target

    return command


def forget_all_memory():
    speak("Are you sure you want to delete all saved memory? Say yes to confirm.")

    answer = voice_input("Please say yes or no.")

    if not answer or answer.strip().lower() not in ("yes", "yes please", "confirm"):
        speak("Memory deletion cancelled.")
        return False

    memory = {
        "paths": {},
        "preferences": {},
        "custom_commands": {}
    }

    if save_memory(memory):
        speak("All saved memory has been deleted.")
        return True

    return False

# =========================================================
# COMMAND PROCESSOR
# =========================================================

def process_command(command):

    if not command:
        return True


    # ===== MULTI-STEP COMMANDS =====
    if " then " in command:
        steps = [
            part.strip()
            for part in command.split(" then ")
            if part.strip()
        ]

        if len(steps) < 2 or len(steps) > 4:
            speak("Please give between two and four steps.")
            return True

        print("Planned steps:")
        for index, step in enumerate(steps, start=1):
            print(f"{index}. {step}")

        speak(
            f"I found {len(steps)} steps. "
            "Say yes to run them in this order."
        )
        confirmation = listen().strip().lower()

        if confirmation not in ("yes", "haan", "ha", "confirm"):
            speak("Multi-step command cancelled.")
            return True

        for step in steps:
            # Prevent a sequence from stopping the assistant.
            if step in ("exit", "bye", "stop assistant", "close assistant"):
                speak("Exit commands are not allowed inside a sequence.")
                break

            speak("Running step: " + step)
            process_command(step)

        speak("Multi-step sequence finished.")
        return True

    # Save every recognized command
    log_activity(
        command,
        "Command received",
        "RECEIVED"
    )


    # Resolve saved custom shortcuts
    command = resolve_custom_command(command)


    # OPEN A SAVED PATH
    if command.startswith("open my ") and command.endswith(" folder"):
        name = command[len("open my "):-len(" folder")].strip()
        open_saved_path(name)
        return True

    if command.startswith("open saved path "):
        name = command[len("open saved path "):].strip()
        open_saved_path(name)
        return True

    # SHOW SAVED MEMORY
    if command in ("show memory", "show saved memory", "my memory"):
        show_memory()
        return True


    # READ LATEST NOTE
    if command in (
        "read my latest note",
        "read latest note",
        "read my last note",
        "read latest voice note"
    ):
        read_latest_note()
        return True

    # SHOW ALL NOTES
    if command in (
        "show my notes",
        "show notes",
        "list my notes",
        "show voice notes"
    ):
        show_voice_notes()
        return True

    # SEARCH NOTES
    if command.startswith("search note "):
        query = command[len("search note "):].strip()

        if query:
            search_voice_notes(query)
        else:
            speak("Please tell me what to search for.")

        return True

    # DELETE A NOTE - CONFIRMATION REQUIRED
    if command.startswith("delete note "):
        query = command[len("delete note "):].strip()

        if query:
            delete_voice_note(query)
        else:
            speak("Please tell me which note to delete.")

        return True

    # OPEN PROJECT BY NAME
    if command.startswith("open project "):
        project_name = command[len("open project "):].strip()
        open_project_by_name(project_name)
        return True

    # REMEMBER PATH: "remember path projects folder"
    if command.startswith("remember path "):
        name = command[len("remember path "):].strip()
        path = voice_input("Tell me the full folder or file path.")

        if path:
            remember_path(name, path)

        return True

    # REMEMBER PREFERENCE: "remember preference language"
    if command.startswith("remember preference "):
        name = command[len("remember preference "):].strip()
        value = voice_input("Tell me the preference value.")

        if value:
            remember_preference(name, value)

        return True

    # REMEMBER CUSTOM COMMAND
    if command.startswith("remember command "):
        alias = command[len("remember command "):].strip()
        target = voice_input(
            "Tell me the existing voice command this shortcut should run."
        )

        if target:
            remember_custom_command(alias, target)

        return True

    # FORGET SAVED MEMORY
    if command.startswith("forget path "):
        forget_memory(
            "path",
            command[len("forget path "):].strip()
        )
        return True

    if command.startswith("forget preference "):
        forget_memory(
            "preference",
            command[len("forget preference "):].strip()
        )
        return True

    if command.startswith("forget command "):
        forget_memory(
            "command",
            command[len("forget command "):].strip()
        )
        return True


    if command in ("forget memory", "delete all memory", "clear all memory"):
        forget_all_memory()
        return True


    # =====================================================
    # WHO IS SHIVAM - PERSONAL PROFILE
    # =====================================================


    if command.strip().lower() in (
        "who is shivam",
        "who is shivam kumar",
        "tell me about shivam",
        "tell me about myself",
        "who am i",
        "tell me shivam"
    ):
        profile = (
            "Shivam is a B.Tech Computer Science and Engineering "
            "student specializing in Artificial Intelligence "
            "and Machine Learning. He is interested in Python, "
            "AI, software development and building practical projects. "
            "His projects include LinguaFlash, AI Resume Builder, "
            "Personal Finance Dashboard, Voice Control Assistant, "
            "YouTube Summarizer, and LifeMoment memory book."
        )

       
        print("\n===== ABOUT SHIVAM =====")
        print(profile)

        import sys

        tts_code = (
            "import pyttsx3, sys; "
            "e = pyttsx3.init('sapi5'); "
            "e.setProperty('volume', 1.0); "
            "e.say(sys.argv[1]); "
            "e.runAndWait()"
        )

        result = subprocess.run(
            [sys.executable, "-c", tts_code, profile],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("Profile voice error:", result.stderr)

        return True




    # =====================================================
    # EXIT
    # =====================================================

    if (
        command in [
            "bye",
            "goodbye"
        ]
        or "bye bye" in command
        or "exit assistant" in command
        or "stop assistant" in command
        or "close assistant" in command
    ):

        speak(
            "Goodbye! Have a nice day."
        )

        return False


    # =====================================================
    # TIME
    # =====================================================

    if (
        command in [
            "time",
            "current time"
        ]
        or "what is the time" in command
        or "what's the time" in command
        or "what is time" in command
        or "tell me the time" in command
    ):

        tell_time()

        return True


    # =====================================================
    # DATE
    # =====================================================

    if (
        command in [
            "date",
            "current date"
        ]
        or "what is the date" in command
        or "what's the date" in command
        or "what is today's date" in command
        or "what is todays date" in command
        or "today's date" in command
        or "todays date" in command
        or "tell me the date" in command
    ):

        tell_date()

        return True


    # =====================================================
    # MATH
    # =====================================================

    if (
        command.startswith(
            "calculate "
        )
        or command.startswith(
            "calculator "
        )
        or command.startswith(
            "solve "
        )
    ):

        calculate_command(
            command
        )

        return True


    if (
        any(
            x in command
            for x in [
                "+",
                "*",
                "/",
                "%"
            ]
        )
        and any(
            c.isdigit()
            for c in command
        )
    ):

        calculate_command(
            command
        )

        return True


    # =====================================================
    # BATTERY
    # =====================================================

    if (
        command in [
            "battery",
            "battery status"
        ]
        or "what is my battery" in command
        or "battery percentage" in command
        or "battery level" in command
        or "how much battery" in command
    ):

        battery_status()

        return True


    # =====================================================
    # SYSTEM INFO
    # =====================================================

    if (
        command in [
            "system information",
            "system info",
            "computer information",
            "pc information"
        ]
        or "system information" in command
        or "system info" in command
    ):

        system_information()

        return True


    # =====================================================
    # WIFI
    # =====================================================

    if any(phrase in command for phrase in [
        "wi-fi",
        "wifi",
        "wi-fi status",
        "wi fi status",
        "check wi-fi",
        "check wi fi",
        "wi-fi check",
        "wi-fi ka status",
        "internet status",
        "internet connection",
        "network status",
        "network connection",
        "check my wi-fi"
    ]):

        wifi_status()

        return True


    # =====================================================
    # VOLUME
    # =====================================================

    if (
        "volume up" in command
        or "increase volume" in command
        or "volume increase" in command
    ):

        volume_up()

        return True


    if (
        "volume down" in command
        or "decrease volume" in command
        or "volume decrease" in command
    ):

        volume_down()

        return True


    if (
        command == "mute"
        or "mute volume" in command
    ):

        volume_mute()

        return True


    # =====================================================
    # BRIGHTNESS
    # =====================================================

    if (
        "brightness up" in command
        or "increase brightness" in command
        or "brightness increase" in command
    ):

        brightness_up()

        return True


    if (
        "brightness down" in command
        or "decrease brightness" in command
        or "brightness decrease" in command
    ):

        brightness_down()

        return True


    # =====================================================
    # MEDIA
    # =====================================================

    if (
        command == "pause"
        or "pause music" in command
        or "pause song" in command
        or "pause video" in command
    ):

        media_key("pause")

        speak("Paused.")

        return True


    if command in [
        "resume",
        "resume music",
        "resume song",
        "play music"
    ]:

        media_key("play")

        speak("Playing.")

        return True


    if (
        command == "next"
        or "next song" in command
        or "next track" in command
        or "next video" in command
    ):

        media_key("next")

        speak("Next.")

        return True


    if (
        command == "previous"
        or "previous song" in command
        or "previous track" in command
        or "previous video" in command
    ):

        media_key("previous")

        speak("Previous.")

        return True


    # =====================================================
    # VOICE TYPING
    # =====================================================

    if command.startswith("type "):

        text = command[
            5:
        ].strip()

        if text:

            voice_type(
                text
            )

        return True


    # =====================================================
    # COPY / PASTE / CUT
    # =====================================================

    if (
        command == "copy"
        or "copy this" in command
        or "copy text" in command
    ):

        copy_text()

        return True


    if (
        command == "paste"
        or "paste this" in command
        or "paste text" in command
    ):

        paste_text()

        return True


    if (
        command == "cut"
        or "cut this" in command
        or "cut text" in command
    ):

        cut_text()

        return True


    # =====================================================
    # SCREENSHOT
    # =====================================================

    if (
        command == "screenshot"
        or "take screenshot" in command
        or "take a screenshot" in command
        or "screenshot le lo" in command
    ):

        take_screenshot()

        return True


    # =====================================================
    # LOCK
    # =====================================================

    if (
        command == "lock"
        or "lock computer" in command
        or "lock pc" in command
        or "lock laptop" in command
    ):

        lock_computer()

        return True


    # =====================================================
    # RESTART
    # =====================================================

    if (
        command == "restart"
        or "restart computer" in command
        or "restart pc" in command
        or "restart laptop" in command
    ):

        restart_computer()

        return True


    # =====================================================
    # SHUTDOWN
    # =====================================================

    if (
        command == "shutdown"
        or "shut down" in command
        or "shutdown computer" in command
        or "shutdown pc" in command
        or "shutdown laptop" in command
    ):

        shutdown_computer()

        return True


    # =====================================================
    # FOLDERS
    # =====================================================

    folder_commands = {

        "downloads":
            "downloads",

        "open downloads":
            "downloads",

        "documents":
            "documents",

        "open documents":
            "documents",

        "desktop":
            "desktop",

        "open desktop":
            "desktop",

        "pictures":
            "pictures",

        "open pictures":
            "pictures",

        "videos":
            "videos",

        "open videos":
            "videos",

        "music":
            "music",

        "open music":
            "music"
    }

    if command in folder_commands:

        open_folder(
            folder_commands[command]
        )

        return True


    # =====================================================
    # CLOSE APP - LEVEL 2
    # =====================================================

    if command.startswith(
        "close "
    ):

        app = command[
            6:
        ].strip()

        if app:

            close_application(
                app
            )

        return True


    if command.startswith(
        "exit "
    ):

        app = command[
            5:
        ].strip()

        if (
            app
            and app not in [
                "assistant",
                "program"
            ]
        ):

            close_application(
                app
            )

            return True


    # =====================================================
    # PLAY SONG
    # =====================================================

    if command.startswith(
        "play "
    ):

        song = command[
            5:
        ].strip()

        if song:

            youtube_play(
                song
            )

            return True


    # =====================================================
    # YOUTUBE
    # =====================================================

    if (
        command == "youtube"
        or "open youtube" in command
    ):

        speak(
            "Opening YouTube."
        )

        open_website(
            "https://www.youtube.com"
        )

        return True


    # =====================================================
    # GOOGLE
    # =====================================================

    if (
        command == "google"
        or "open google" in command
    ):

        speak(
            "Opening Google."
        )

        open_website(
            "https://www.google.com"
        )

        return True


    # =====================================================
    # CHATGPT
    # =====================================================

    if (
        command == "chatgpt"
        or "open chatgpt" in command
        or "open chat gpt" in command
    ):

        speak(
            "Opening ChatGPT."
        )

        open_website(
            "https://chatgpt.com"
        )

        return True


    # =====================================================
    # CHROME
    # =====================================================

    if (
        command == "chrome"
        or "open chrome" in command
    ):

        speak(
            "Opening Chrome."
        )

        open_application(
            "chrome"
        )

        return True


    # =====================================================
    # CALCULATOR APP
    # =====================================================

    if (
        command == "calculator"
        or "open calculator" in command
        or "calculator kholo" in command
    ):

        speak(
            "Opening calculator."
        )

        subprocess.Popen(
            "calc.exe"
        )

        return True


    # =====================================================
    # NOTEPAD
    # =====================================================

    if (
        command == "notepad"
        or "open notepad" in command
        or "notepad kholo" in command
    ):

        speak(
            "Opening Notepad."
        )

        subprocess.Popen(
            "notepad.exe"
        )

        return True


    # =====================================================
    # FILE EXPLORER
    # =====================================================

    if (
        command == "explorer"
        or "open explorer" in command
        or "open file explorer" in command
    ):

        speak(
            "Opening File Explorer."
        )

        subprocess.Popen(
            "explorer.exe"
        )

        return True


    # =====================================================
    # SETTINGS
    # =====================================================

    if (
        command == "settings"
        or "open settings" in command
    ):

        speak(
            "Opening settings."
        )

        os.system(
            "start ms-settings:"
        )

        return True


    # =====================================================
    # VS CODE
    # =====================================================

    if (
        command == "vs code"
        or "open vs code" in command
        or "open visual studio code" in command
    ):

        speak(
            "Opening Visual Studio Code."
        )

        open_application(
            "code"
        )

        return True


    # =====================================================
    # THIS PC
    # =====================================================

    if (
        command in [
            "computer",
            "open computer",
            "this pc"
        ]
        or "open this pc" in command
    ):

        speak(
            "Opening This PC."
        )

        subprocess.Popen(
            "explorer.exe "
            "shell:MyComputerFolder"
        )

        return True

    # =====================================================
    # LEVEL 2 - FILE MANAGER COMMANDS
    # =====================================================

    if command.startswith("create folder "):

        name = command[
            len("create folder "):
        ].strip()

        create_folder_voice(name)
        return True


    if command.startswith("make folder "):

        name = command[
            len("make folder "):
        ].strip()

        create_folder_voice(name)
        return True


    if command.startswith("create file "):

        name = command[
            len("create file "):
        ].strip()

        create_file_voice(name)
        return True


    if command.startswith("make file "):

        name = command[
            len("make file "):
        ].strip()

        create_file_voice(name)
        return True


    if command.startswith("search file "):

        name = command[
            len("search file "):
        ].strip()

        search_file_voice(name)
        return True


    if command.startswith("find file "):

        name = command[
            len("find file "):
        ].strip()

        search_file_voice(name)
        return True


    if command.startswith("delete file "):

        name = command[
            len("delete file "):
        ].strip()

        delete_file_voice(name)
        return True


    if command.startswith("remove file "):

        name = command[
            len("remove file "):
        ].strip()

        delete_file_voice(name)
        return True


    if command.startswith("rename file "):

        data = command[
            len("rename file "):
        ].strip()

        if " to " in data:

            old_name, new_name = data.split(
                " to ",
                1
            )

            rename_file_voice(
                old_name.strip(),
                new_name.strip()
            )

        else:

            speak(
                "Say rename file old name to new name."
            )

        return True


    if command.startswith("move file "):

        data = command[
            len("move file "):
        ].strip()

        if " to " in data:

            file_name, destination = data.split(
                " to ",
                1
            )

            move_file_voice(
                file_name.strip(),
                destination.strip()
            )

        else:

            speak(
                "Say move file file name to Downloads."
            )

        return True

    # =====================================================
    # LEVEL 3 - CLIPBOARD
    # =====================================================

    if (
        command == "what is in clipboard"
        or command == "read clipboard"
        or command == "check clipboard"
        or command == "clipboard"
    ):
     clipboard_read()
     return True


    if (
        command == "clear clipboard"
        or command == "empty clipboard"
    ):
     clipboard_clear()
     return True


    if (
        command == "paste"
        or command == "paste clipboard"
    ):
     clipboard_paste()
     return True
    # =====================================================
    # LEVEL 3 - PROCESS MONITOR
    # =====================================================

    if (
        command == "show running apps"
        or command == "running apps"
        or command == "show running processes"
    ):
     running_apps()
     return True


    if (
        "what is using cpu" in command
        or "cpu usage" in command
        or "show cpu usage" in command
    ):
     top_cpu_processes()
     return True


    if (
       "what is using ram" in command
        or "ram usage" in command
        or "show ram usage" in command
    ):
     top_ram_processes()
     return True
    # =====================================================
    # LEVEL 3 - ADVANCED FILE SEARCH
    # =====================================================

    if (
        command == "find all pdf files"
        or command == "find pdf files"
        or command == "search pdf files"
    ):
     find_pdf_files()
     return True


    if (
       command == "find files larger than 100 mb"
       or command == "find large files"
       or command == "find files over 100 mb"
    ):
     find_large_files()
     return True


    if (
        command == "find files modified today"
        or command == "find files changed today"
        or command == "find today's files"
    ):
     find_files_today()
     return True

    # =====================================================
    # LEVEL 3 - STUDY SETUP COMMAND
    # =====================================================

    if (
        command == "open my study setup"
        or command == "start my study setup"
        or command == "study setup"
    ):
      study_setup()
      return True

    # =====================================================
    # LEVEL 3 - SYSTEM HEALTH COMMAND
    # =====================================================

    if (
        command == "system health"
        or command == "system health report"
        or command == "give me system health"
        or command == "check system health"
    ):
     system_health_report()
     return True

    # =====================================================
    # LEVEL 3 - PERFORMANCE MONITOR COMMAND
    # =====================================================

    if (
        command == "performance monitor"
        or command == "monitor performance"
        or command == "check performance"
        or command == "check system performance"
    ):
     performance_monitor()
     return True

    # =====================================================
    # LEVEL 3 - SMART SYSTEM ALERT COMMAND
    # =====================================================

    if (
        command == "check system alerts"
        or command == "system alerts"
        or command == "check alerts"
        or command == "check system alert"
    ):
     check_system_alerts()
     return True

    # =====================================================
    # LEVEL 3 - SMART RESOURCE ADVISOR COMMAND
    # =====================================================

    if (
         command == "smart resource advisor"
         or command == "resource advisor"
         or command == "analyze system"
         or command == "analyze my system"
         or command == "analyse my system"
    ):
     smart_resource_advisor()
     return True

    # =====================================================
    # LEVEL 3 - SECURITY CHECK COMMAND
    # =====================================================

    if (
    command == "check security"
    or command == "security check"
    or command == "check system security"
    ):
     security_check()
     return True

    # =====================================================
    # LEVEL 3 - SECURITY STATUS COMMAND
    # =====================================================

    if (
    command == "security status"
    or command == "show security status"
    or command == "check security status"
):
     security_status()
     return True


    # =====================================================
    # LEVEL 3 - START WINDOWS UPDATE COMMAND
    # =====================================================

    if (
        command == "start windows update"
        or command == "start windows update service"
        or command == "turn on windows update"
    ):
     start_windows_update()
     return True

    # =====================================================
    # LEVEL 3 - NETWORK MONITOR COMMAND
    # =====================================================

    if (
        command == "check network"
        or command == "network monitor"
        or command == "check my network"
        or command == "show network"
    ):
     network_monitor()
     return True

    # =====================================================
    # LEVEL 3 - DOWNLOADS ORGANIZER COMMAND
    # =====================================================

    if (
        command == "organize my downloads"
        or command == "organize downloads"
        or command == "clean my downloads"
        or command == "sort my downloads"
        or command == "organise my download"
    ):
     organize_downloads()
     return True

    # =====================================================
    # LEVEL 3 - DUPLICATE FILE FINDER COMMAND
    # =====================================================

    if (
        command == "find duplicate files"
        or command == "search duplicate files"
        or command == "find duplicates"
        or command == "check duplicate files"
    ):
     find_duplicate_files()
     return True

    # =====================================================
    # LEVEL 3 - SAFE CLEANUP COMMAND
    # =====================================================

    if (
        command == "clean temporary files"
        or command == "clean temp files"
        or command == "start cleanup"
        or command == "clean my system"
    ):
     safe_cleanup()
     return True

    # =====================================================
    # LEVEL 3 - ACTIVITY LOG COMMAND
    # =====================================================

    if (
        command == "show activity log"
        or command == "show my activity log"
        or command == "activity log"
        or command == "show activity"
    ):

     show_activity_log()

     log_activity(
        command,
        "Activity log displayed"
    )

     return True

    # =====================================================
    # JOKE COMMANDS
    # =====================================================

    if (
        command == "joke"
        or command == "tell me a joke"
        or command == "tell me a funny joke"
        or command == "make me laugh"
    ):

        tell_joke()

        return True


    # =====================================================
    # NEWS HEADLINES
    # =====================================================

    if (
        command == "news"
        or command == "latest news"
        or command == "news headlines"
        or command == "latest news headlines"
        or command == "today's news"
        or command == "todays news"
        or command == "today's headlines"
        or command == "todays headlines"
        or "tell me the latest news" in command
        or "tell me today's news" in command
    ):

        get_news_headlines()

        return True

    return process_command_extra(command)
    # =====================================================
# LEVEL 4 - MESSAGING ASSISTANT
# =====================================================

def voice_input(prompt):
    speak(prompt)
    return listen()


def confirm_message(platform, recipient, message):

    print("\n===== MESSAGE CONFIRMATION =====")
    print("Platform:", platform)
    print("Recipient:", recipient)
    print("Message:", message)

    speak(
        "You are about to send a message on "
        + platform
        + " to "
        + recipient
        + ". Say yes to continue."
    )

    answer = listen()

    if (
        "yes" in answer
        or "confirm" in answer
        or "haan" in answer
        or answer == "ha"
    ):
        return True

    speak("Message cancelled.")
    return False

def send_email():

    speak("Email assistant started.")

    recipient = voice_input(
        "Tell me the email address."
    )

    if not recipient:
        return True

    subject = voice_input(
        "Tell me the email subject."
    )

    if not subject:
        subject = "Message"

    message = voice_input(
        "Tell me the email message."
    )

    if not message:
        speak("Message is empty.")
        return True

    if not confirm_message(
        "Email",
        recipient,
        message
    ):
        return True

    url = (
        "mailto:"
        + urllib.parse.quote(recipient)
        + "?subject="
        + urllib.parse.quote(subject)
        + "&body="
        + urllib.parse.quote(message)
    )

    speak("Opening your email application.")

    webbrowser.open(url)

    return True
def send_whatsapp():

    speak("WhatsApp assistant started.")

    contact = voice_input(
        "Tell me the WhatsApp contact name."
    )

    if not contact:
        return True

    message = voice_input(
        "Tell me the WhatsApp message."
    )

    if not message:
        speak("Message is empty.")
        return True

    if not confirm_message(
        "WhatsApp",
        contact,
        message
    ):
        return True

    import pyautogui
    import pyperclip
    import time

    # Copy message
    pyperclip.copy(message)

    speak("Opening WhatsApp Web.")

    webbrowser.open_new_tab(
        "https://web.whatsapp.com/"
    )

    time.sleep(10)

    speak(
        "Searching for " + contact
    )

    # WhatsApp Web search shortcut
    pyautogui.hotkey(
        "ctrl",
        "alt",
        "/"
    )

    time.sleep(2)

    pyautogui.write(
        contact,
        interval=0.05
    )

    time.sleep(3)

    # Select contact
    pyautogui.press("down")
    time.sleep(1)
    pyautogui.press("enter")

    time.sleep(3)

    # Click message area near bottom
    screen_width, screen_height = pyautogui.size()

    pyautogui.click(
        screen_width // 2,
        screen_height - 100
    )

    time.sleep(1)

    # Paste message
    pyautogui.hotkey(
        "ctrl",
        "v"
    )

    time.sleep(2)

    speak(
        "Message is ready in WhatsApp. "
        "Say send to confirm."
    )

    answer = listen()

    if (
        "send" in answer
        or "yes" in answer
        or "haan" in answer
        or "confirm" in answer
    ):

        pyautogui.press("enter")

        speak(
            "Message sent."
        )

    else:

        speak(
            "Message sending cancelled."
        )

    return True

def send_telegram():

    speak(
        "Telegram assistant started."
    )

    username = voice_input(
        "Tell me the Telegram username."
    )

    if not username:
        return True

    username = (
        username.replace(" ", "")
        .replace("@", "")
    )

    message = voice_input(
        "Tell me the Telegram message."
    )

    if not message:
        speak("Message is empty.")
        return True

    if not confirm_message(
        "Telegram",
        "@" + username,
        message
    ):
        return True

    encoded_message = urllib.parse.quote(
        message
    )

    url = (
        "https://t.me/"
        + username
        + "?text="
        + encoded_message
    )

    speak(
        "Opening Telegram with your message."
    )

    webbrowser.open(url)

    speak(
        "Message is ready. "
        "Check the recipient and press send."
    )

    return True
def send_instagram():

    speak("Instagram assistant started.")

    import pyautogui
    import pyperclip
    import time
    import webbrowser
   
    # =========================================
    # GET INSTAGRAM USERNAME
    # =========================================

    username = voice_input(
        "Tell me the Instagram username."
    )

    if not username:
        return True

    username = (
        username
        .replace(" ", "")
        .replace("@", "")
        .strip()
    )

    # =========================================
    # GET MESSAGE
    # =========================================

    message = voice_input(
        "Tell me the Instagram message."
    )

    if not message:
        speak("Message is empty.")
        return True

    # =========================================
    # CONFIRMATION
    # =========================================

    if not confirm_message(
        "Instagram",
        "@" + username,
        message
    ):
        return True

    pyperclip.copy(message)

    # =========================================
    # OPEN INSTAGRAM MESSAGES
    # =========================================

    speak("Opening Instagram messages.")

    webbrowser.open_new_tab(
        "https://www.instagram.com/direct/inbox/"
    )

    time.sleep(8)

    screen_width, screen_height = pyautogui.size()

    # =========================================
    # NEW MESSAGE BUTTON
    # =========================================

    speak("Opening new message.")

    pyautogui.click(
        int(screen_width * 0.281),
        int(screen_height * 0.149)
    )

    time.sleep(3)

    # =========================================
    # TO FIELD
    # =========================================

    speak("Searching for " + username)

    # Click the To field
    pyautogui.click(
        int(screen_width * 0.50),
        int(screen_height * 0.338)
    )

    time.sleep(1)

    pyautogui.write(
        username,
        interval=0.08
    )

    time.sleep(5)

    # =========================================
    # SELECT FIRST MATCH
    # =========================================

    # Click first result below To field
    pyautogui.click(
        int(screen_width * 0.50),
        int(screen_height * 0.415)
    )

    time.sleep(2)

    # =========================================
    # CHAT BUTTON
    # =========================================

    speak("Opening chat.")

    pyautogui.click(
        int(screen_width * 0.50),
        int(screen_height * 0.79)
    )

    time.sleep(5)

    # =========================================
    # MESSAGE BOX
    # =========================================

    speak("Opening message box.")

    pyautogui.click(
        screen_width // 2,
        int(screen_height * 0.88)
    )

    time.sleep(1)

    # =========================================
    # PASTE MESSAGE
    # =========================================

    pyautogui.hotkey(
        "ctrl",
        "v"
    )

    time.sleep(2)

    speak(
        "Message is ready. Press Enter to send."
    )

    # Enter automatically nahi dabega.

    return True


# =========================================================
# NEW FEATURES: VOICE READER, CODING, SUMMARY, TRANSLATION
# =========================================================

from pathlib import Path
import ast
import re
import textwrap
import webbrowser

DESKTOP_DIR = Path.home() / "Desktop"
DESKTOP_DIR.mkdir(parents=True, exist_ok=True)


# 1. VOICE SCREEN READER
def read_screen_aloud():
    try:
        import pyautogui
        import pytesseract

        screenshot = pyautogui.screenshot()
        text = pytesseract.image_to_string(screenshot).strip()

        if not text:
            speak("I could not detect readable text on the screen.")
            return

        print("\n===== SCREEN READER =====\n", text)

        # Speak in smaller chunks to avoid very long TTS calls.
        chunks = re.split(r"(?<=[.!?])\s+", text)
        speak("Reading the visible screen text.")

        for chunk in chunks:
            chunk = chunk.strip()
            if chunk:
                speak(chunk)

    except Exception as e:
        print("Voice screen reader error:", repr(e))
        speak("Screen reader failed. Check Tesseract OCR installation.")


# 2. VOICE CODING: SAFE STARTER TEMPLATES, SAVE TO DESKTOP
def create_voice_code():
    speak("Say the type of Python code you want.")
    request = listen().lower().strip()

    if not request:
        speak("I did not hear a coding request.")
        return

    code = None

    if "prime" in request:
        code = textwrap.dedent("""\
            def is_prime(number):
                if number < 2:
                    return False
                for divisor in range(2, int(number ** 0.5) + 1):
                    if number % divisor == 0:
                        return False
                return True


            if __name__ == "__main__":
                value = int(input("Enter a number: "))
                print(is_prime(value))
        """)

    elif "factorial" in request:
        code = textwrap.dedent("""\
            def factorial(number):
                if number < 0:
                    raise ValueError("Number must be non-negative")
                result = 1
                for value in range(2, number + 1):
                    result *= value
                return result


            if __name__ == "__main__":
                value = int(input("Enter a number: "))
                print(factorial(value))
        """)

    elif "palindrome" in request:
        code = textwrap.dedent("""\
            def is_palindrome(text):
                cleaned = ''.join(
                    character.lower()
                    for character in text
                    if character.isalnum()
                )
                return cleaned == cleaned[::-1]


            if __name__ == "__main__":
                value = input("Enter text: ")
                print(is_palindrome(value))
        """)

    else:
        speak(
            "Offline coding currently supports prime checker, "
            "factorial and palindrome templates. No file was created."
        )
        return

    # Validate syntax before saving; never execute generated code.
    try:
        ast.parse(code)
    except SyntaxError:
        speak("The generated code did not pass syntax validation.")
        return

    filename = "voice_generated_code.py"
    destination = DESKTOP_DIR / filename

    if destination.exists():
        speak("That file already exists. Say yes to overwrite it.")
        answer = listen().lower().strip()
        if answer not in ("yes", "haan", "ha", "confirm"):
            speak("Save cancelled. Existing file was not changed.")
            return

    try:
        destination.write_text(code, encoding="utf-8")
        print("Code saved:", destination)
        speak("Python code saved on your Desktop.")
    except OSError as e:
        print("Code save error:", repr(e))
        speak("I could not save the code file.")


# 3. OFFLINE EXTRACTIVE SUMMARY
def summarize_text(text, max_sentences=5):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if not sentences:
        return text[:1000].strip()

    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    stop_words = {
        "the", "and", "for", "that", "with", "this", "from",
        "are", "was", "were", "have", "has", "into", "their",
        "you", "your", "but", "not", "can", "will", "they"
    }

    frequencies = {}
    for word in words:
        if word not in stop_words:
            frequencies[word] = frequencies.get(word, 0) + 1

    scored = []
    for index, sentence in enumerate(sentences):
        sentence_words = re.findall(r"\b[a-zA-Z]{3,}\b", sentence.lower())
        score = sum(frequencies.get(w, 0) for w in sentence_words)
        scored.append((score / max(len(sentence_words), 1), index, sentence))

    best = sorted(scored, reverse=True)[:max_sentences]
    best = sorted(best, key=lambda item: item[1])
    return " ".join(item[2] for item in best)


def summarize_document_or_article():
    speak("Say PDF to summarize a PDF, or article to summarize a web article.")
    mode = listen().lower().strip()

    text = ""

    try:
        if "pdf" in mode:
            speak("Say the full PDF file path.")
            file_path = listen().strip().strip('"')

            if not file_path:
                speak("No file path received.")
                return

            from pypdf import PdfReader
            pdf_path = Path(file_path).expanduser()

            if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
                speak("That PDF file could not be found.")
                return

            reader = PdfReader(str(pdf_path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)

        elif "article" in mode:
            speak("Say or type the article URL in the terminal.")
            url = input("Article URL: ").strip()

            if not url.startswith(("https://", "http://")):
                speak("Please provide a valid HTTP or HTTPS URL.")
                return

            from bs4 import BeautifulSoup
            response = requests.get(
                url,
                timeout=15,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            text = soup.get_text(" ", strip=True)

        else:
            speak("Please say PDF or article.")
            return

        if not text.strip():
            speak("No extractable text was found.")
            return

        summary = summarize_text(text)
        print("\n===== SUMMARY =====\n", summary)

        speak("Here is the summary.")
        for sentence in re.split(r"(?<=[.!?])\s+", summary):
            if sentence.strip():
                speak(sentence.strip())

    except Exception as e:
        print("Summary error:", repr(e))
        speak("Summary failed. Check the file, URL or internet connection.")


# 4. HINDI <-> ENGLISH SPEECH TRANSLATOR
def translate_speech():
    try:
        from deep_translator import GoogleTranslator

        speak("Say Hindi to English, or English to Hindi.")
        direction = listen().lower()

        if "hindi" in direction and "english" in direction:
            if direction.index("hindi") < direction.index("english"):
                source_lang, target_lang = "hi-IN", "en"
            else:
                source_lang, target_lang = "en-IN", "hi"
        else:
            speak("Please specify Hindi to English or English to Hindi.")
            return

        speak("Speak the sentence to translate.")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=15)

        spoken_text = recognizer.recognize_google(
            audio, language=source_lang
        )

        translated = GoogleTranslator(
            source="hi" if source_lang == "hi-IN" else "en",
            target="en" if target_lang == "en" else "hi"
        ).translate(spoken_text)

        print("Original:", spoken_text)
        print("Translation:", translated)
        speak("Translation: " + translated)

    except Exception as e:
        print("Translator error:", repr(e))
        speak("Translation failed. Check microphone and internet access.")


def process_command_extra(command):


    # ===== NEW FEATURE COMMANDS =====

    if command in (
        "read screen aloud",
        "read my screen",
        "screen reader",
        "read screen text"
    ):
        read_screen_aloud()
        return True

    if command in (
        "voice coding",
        "create code",
        "generate python code",
        "write python code"
    ):
        create_voice_code()
        return True

    if command in (
        "summarize pdf",
        "summarise pdf",
        "summarize article",
        "document summary",
        "read summary aloud"
    ):
        summarize_document_or_article()
        return True

    if command in (
        "translate speech",
        "start translator",
        "voice translator",
        "translate hindi english"
    ):
        translate_speech()
        return True


    # STEP 3 CODE YAHAN
    if (
        command == "send email"
        or command == "send an email"
        or command == "email"
        or "send email" in command
    ):
        send_email()
        return True

    if (
        command == "send whatsapp"
        or command == "send a whatsapp message"
        or command == "whatsapp message"
        or "send whatsapp" in command
    ):
        send_whatsapp()
        return True

    if (
        command == "send telegram"
        or command == "send a telegram message"
        or command == "telegram message"
        or "send telegram" in command
    ):
        send_telegram()
        return True
    if command.strip() in ["instagram", "open instagram"]:
        import webbrowser
        webbrowser.open("https://www.instagram.com/")
        return True
    if (
        command == "send instagram message"
        or command == "send instagram"
        or command == "instagram message"
        or command == "send an instagram message"
        or "send instagram" in command
    ):
        send_instagram()
        return True


    # SMART VOICE NOTES - BEFORE GOOGLE/CHATGPT SEARCH

    if command in (
        "read latest note",
        "read my latest note",
        "read my last note",
        "read latest voice note"
    ):
        read_latest_note()
        return True

    if command in (
        "show all notes",
        "show my notes",
        "show notes",
        "show voice notes",
        "list my notes"
    ):
        show_voice_notes()
        return True

    if command.startswith("search note "):
        query = command[len("search note "):].strip()
        if query:
            search_voice_notes(query)
        else:
            speak("Please tell me what to search for.")
        return True

    if command.startswith("search notes "):
        query = command[len("search notes "):].strip()
        if query:
            search_voice_notes(query)
        else:
            speak("Please tell me what to search for.")
        return True

    if command.startswith("delete note "):
        query = command[len("delete note "):].strip()
        if query:
            delete_voice_note(query)
        else:
            speak("Please tell me which note to delete.")
        return True


    # =====================================================
    # ADVANCED FEATURE COMMANDS
    # =====================================================

    if command in ("check my screen", "screen vision", "read my screen"):
        screen_vision()
        return True

    if command.startswith("remember search "):
        query = command[len("remember search "):].strip()
        if query:
            personal_memory_search(query)
        else:
            speak("Tell me what to search in your saved notes.")
        return True

    if command in ("save coding setup", "create coding macro"):
        save_coding_macro()
        return True

    if command in ("start coding setup", "run coding macro"):
        run_coding_macro()
        return True

    if command in ("check pc health", "why is my laptop slow", "pc health report"):
        pc_health_report()
        return True

    if command.startswith("add project task "):
        data = command[len("add project task "):].strip()
        if " to " in data:
            task, project = data.rsplit(" to ", 1)
            add_project_task(project.strip(), task.strip())
        else:
            speak("Say add project task task name to project name.")
        return True

    if command.startswith("show project tasks "):
        project = command[len("show project tasks "):].strip()
        if project:
            show_project_tasks(project)
        else:
            speak("Tell me the project name.")
        return True

    if command.startswith("complete project task "):
        data = command[len("complete project task "):].strip()
        if " in " in data:
            task, project = data.rsplit(" in ", 1)
            complete_project_task(project.strip(), task.strip())
        else:
            speak("Say complete project task task name in project name.")
        return True


    # PRODUCTIVITY TRACKER COMMANDS
    if command in (
        "start productivity tracking",
        "start app tracking"
    ):
        start_productivity_tracking()
        return True

    if command in (
        "stop productivity tracking",
        "stop app tracking"
    ):
        stop_productivity_tracking()
        return True

    if command in (
        "show productivity report",
        "show app usage",
        "today's productivity report",
        "show productivity tracking"
    ):
        show_productivity_report()
        return True


    # SMART APP & WEBSITE LAUNCHER
    if smart_launcher(command):
        return True



    # SMART APP GUARD COMMANDS
    if command in (
        "setup app guard",
        "set up app guard",
        "smart app guard",
        "smart app guide",
        "setup app guide",
        "set up app guide"
    ):
        setup_app_guard()
        return True


    if command.startswith("guarded open "):
        app_name = command[len("guarded open "):].strip()
        if app_name:
            guarded_open_app(app_name)
        else:
            speak("Tell me which protected app to open.")
        return True

    # ===== SMART STORAGE DETECTIVE =====
    if command in (
        "scan large files",
        "find duplicate files",
        "storage detective",
        "scan my storage"
    ):
        storage_detective()
        return True

    # ===== NETWORK DETECTIVE =====
    if command in (
        "network detective",
        "diagnose my network",
        "check internet diagnostics",
        "run network test"
    ):
        network_detective()
        return True

    # ===== PRODUCTIVITY TRACKER =====
    if command in ("start productivity tracking", "start app tracking"):
        start_productivity_tracking()
        return True

    if command in ("stop productivity tracking", "stop app tracking"):
        stop_productivity_tracking()
        return True

    if command in (
        "show productivity report",
        "show app usage",
        "today's productivity report"
    ):
        show_productivity_report()
        return True

    # =====================================================
    # QUESTIONS / WRITING / STUDY
    # =====================================================

    if is_question(
        command
    ):

        search_google_and_chatgpt(
            command
        )

        return True

    # =====================================================
    # FOLDER RENAME / DELETE
    # =====================================================

    if command.startswith("rename folder "):

        data = command[len("rename folder "):].strip()

        if " to " in data:

            old_name, new_name = data.split(
                " to ",
                1
            )

            rename_folder_voice(
                old_name.strip(),
                new_name.strip()
            )

        else:

            speak(
                "Say rename folder old name to new name."
            )

        return True


    if command.startswith("delete folder "):

        name = command[len("delete folder "):].strip()

        if name:
            delete_folder_voice(name)

        else:
            speak("Please tell me the folder name.")

        return True


    if command.startswith("remove folder "):

        name = command[len("remove folder "):].strip()

        if name:
            delete_folder_voice(name)

        else:
            speak("Please tell me the folder name.")

        return True

    
    # =====================================================
    # LEVEL 2 - COPY / MOVE FOLDER / FILE LOCATION COMMANDS
    # =====================================================

    if command.startswith("copy file "):

        data = command[len("copy file "):].strip()

        if " to " in data:

            file_name, destination = data.split(
                " to ",
                1
            )

            copy_file_voice(
                file_name.strip(),
                destination.strip()
            )

        else:

            speak(
                "Say copy file file name to Downloads."
            )

        return True


    if command.startswith("move folder "):

        data = command[len("move folder "):].strip()

        if " to " in data:

            folder_name, destination = data.split(
                " to ",
                1
            )

            move_folder_voice(
                folder_name.strip(),
                destination.strip()
            )

        else:

            speak(
                "Say move folder folder name to Documents."
            )

        return True

    if command.startswith("copy folder "):

        data = command[len("copy folder "):].strip()

        # "to" ya "download" / "downloads" dono support
        if " to " in data:

            folder_name, destination = data.split(
                " to ",
                1
            )

        elif data.endswith(" download"):

            folder_name = data[:-len(" download")].strip()
            destination = "downloads"

        elif data.endswith(" downloads"):

            folder_name = data[:-len(" downloads")].strip()
            destination = "downloads"

        else:

            speak(
                "Say copy folder folder name to Downloads."
            )

            return True

        copy_folder_voice(
            folder_name.strip(),
            destination.strip()
        )

        return True


        

    if (
        command.startswith("where is my file ")
        or command.startswith("where is file ")
    ):

        if command.startswith("where is my file "):

            name = command[
                len("where is my file "):
            ].strip()

        else:

            name = command[
                len("where is file "):
            ].strip()

        where_is_file_voice(name)

        return True


    if command.startswith("open location of "):

        name = command[
            len("open location of "):
        ].strip()

        open_file_location_voice(name)

        return True
    
    # =====================================================
    # ALL DRIVE STORAGE STATUS
    # =====================================================

    if (
        command == "check storage"
        or command == "check disk space"
        or command == "storage status"
        or command == "how much storage is left"
        or command == "disk space"
    ):

        get_all_drives_storage()

        return True


    # Specific drive: C, D, E, F...
    if command.startswith("check drive "):

        drive = command[len("check drive "):].strip().upper()

        if not drive.endswith(":"):
            drive += ":"

        get_storage_info(drive)

        return True


    if command.startswith("show drive "):

        drive = command[len("show drive "):].strip().upper()

        if not drive.endswith(":"):
            drive += ":"

        get_storage_info(drive)

        return True

    # =====================================================
    # SEARCH FILE / FOLDER
    # =====================================================
    
    if command.startswith("search folder "):
    
            name = command[len("search folder "):].strip()
    
            if name:
                search_file_voice(name)
            else:
                speak("Please tell me the folder name.")
    
            return True
    
    
    if command.startswith("find folder "):
    
            name = command[len("find folder "):].strip()
    
            if name:
                search_file_voice(name)
            else:
                speak("Please tell me the folder name.")
    
            return True

    # =====================================================
    # SYSTEM INFORMATION COMMANDS
    # =====================================================

    if (
        command == "system information"
        or command == "system info"
        or command == "computer information"
        or command == "computer info"
        or command == "laptop information"
        or command == "laptop info"
        or command == "my computer information"
    ):

        get_system_info()

        return True
    # =====================================================
    # BATTERY COMMANDS
    # =====================================================

    if (
        command == "battery status"
        or command == "battery information"
        or command == "check battery"
        or command == "battery"
        or command == "how much battery is left"
    ):

     battery_information()

     return True 


    # VOICE NOTES
    if command in (
        "create note",
        "make a note",
        "save a note",
        "take a note",
        "create voice note"
    ):
        create_voice_note()
        return True

    # =====================================================
    # LEVEL 3 - STUDY REMINDER
    # =====================================================

    if (
    "remind me at 9 pm to study" in command
    or "remind me at 9:00 pm to study" in command
    or "remind me at 9 p.m. to study" in command
    or "remind me at 9:00 p.m. to study" in command
    ):
     speak("Study reminder set for 9 PM.")

     subprocess.Popen([
        "powershell",
        "-NoProfile",
        "-Command",
        'schtasks /create /sc DAILY /tn "VoiceAssistant Study Reminder" /tr "msg * \'Time to study!\'" /st 21:00 /f'
    ])

     return True
    # =====================================================
    # GOOGLE SEARCH
    # =====================================================

    if command.startswith(
        "search "
    ):

        query = command[
            7:
        ].strip()

        if query:

            encoded_query = (
                urllib.parse.quote_plus(
                    query
                )
            )

            speak(
                "Searching Google."
            )

            open_website(
                "https://www.google.com/search?q="
                + encoded_query
            )

        return True


    # =====================================================
    # GENERIC OPEN
    # =====================================================

    if command.startswith(
        "open "
    ):

        app = command[
            5:
        ].strip()

        if app:

            open_application(
                app
            )

        return True


    # =====================================================
    # UNKNOWN
    # =====================================================

    speak(
        "Sorry, I don't know "
        "that command yet."
    )

    return True


# =========================================================
# MAIN
# =========================================================

def main():

    speak(
        "Voice Control Assistant started."
    )

    speak(
        "I am ready for your command."
    )

    while True:

        command = listen()


        if not process_command(
            command
        ):

            break


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    

    main()