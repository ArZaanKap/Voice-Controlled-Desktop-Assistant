import os
import pyttsx3
import speech_recognition as sr
import pyautogui
import subprocess
import webbrowser
from send2trash import send2trash

engine = pyttsx3.init()
last_opened_folder = None  # stores last opened folder


def speak(text):
    print(f"🤖 {text}")
    engine.say(text)
    engine.runAndWait()


def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        print(f"📄 You said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
    except sr.RequestError:
        speak("API error. Check internet.")
    return None


def get_response(prompt):
    # Ask a sub-question twice, if still no answer, cancel
    speak(prompt)
    response = listen()
    if not response:
        speak("I didn't catch that. Please repeat.")
        response = listen()
    if not response:
        speak("Okay, let's try something else.")
        return None
    return response


def change_volume(action):
    if action == "up":
        pyautogui.press("volumeup")
    elif action == "down":
        pyautogui.press("volumedown")
    elif action == "mute":
        pyautogui.press("volumemute")
    elif action == "unmute":
        pyautogui.press("volumeunmute")
    speak(f"Volume {action}")



def take_screenshot():
    global last_opened_folder
    screenshot = pyautogui.screenshot()
    if last_opened_folder:
        os.makedirs(last_opened_folder, exist_ok=True)  # Ensure folder exists
        path = os.path.join(last_opened_folder, "screenshot.png")
    else:
        desktop_path = os.path.expanduser("~/Desktop")
        os.makedirs(desktop_path, exist_ok=True)
        path = os.path.join(desktop_path, "screenshot.png")
    screenshot.save(path)

    if last_opened_folder:
        folder_name = os.path.basename(os.path.normpath(last_opened_folder))
        speak(f"Screenshot saved to {folder_name}")
    else: 
        speak(f"Screenshot saved to Desktop")



def create_folder():
    folder_name = get_response("What should I name the folder?")
    if not folder_name:
        return
    path = os.path.join(os.getcwd(), folder_name)
    try:
        os.makedirs(path)
        speak(f"Folder '{folder_name}' created.")
    except FileExistsError:
        speak("That folder already exists.")


def delete_folder():
    folder_name = get_response("Which folder do you want to delete?")
    if not folder_name:
        return
    path = os.path.join(os.getcwd(), folder_name)
    if os.path.isdir(path):
        confirmation = get_response(f"Are you sure you want to delete the folder {folder_name}? Say yes to confirm.")
        if confirmation and "yes" in confirmation:
            try:
                send2trash(path)
                speak(f"Folder {folder_name} sent to trash.")
            except Exception as e:
                speak(f"Error: {e}")
        else:
            speak("Folder deletion cancelled.")
    else:
        speak("That folder doesn't exist.")


def open_folder():
    global last_opened_folder
    folder_name = get_response("Which folder do you want to open?")
    if not folder_name:
        return
    path = os.path.join(os.getcwd(), folder_name)
    if os.path.isdir(path):
        os.startfile(path)
        last_opened_folder = path
        speak(f"Folder {folder_name} opened.")
    else:
        speak("That folder doesn't exist.")


def close_folder():
    try:
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], check=True)
        subprocess.run(["start", "explorer"], shell=True)
        speak("Closed folder windows.")
    except Exception as e:
        speak(f"Could not close folders: {e}")


def rename_folder():
    old_name = get_response("What is the current name of the folder?")
    if not old_name:
        return
    new_name = get_response("What should be the new name?")
    if not new_name:
        return
    old_path = os.path.join(os.getcwd(), old_name)
    new_path = os.path.join(os.getcwd(), new_name)
    if os.path.isdir(old_path):
        try:
            os.rename(old_path, new_path)
            speak(f"Renamed folder from {old_name} to {new_name}.")
        except Exception as e:
            speak(f"Could not rename folder: {e}")
    else:
        speak("That folder doesn't exist.")


def open_application():
    app_name = get_response("Which application do you want to open?")
    if not app_name:
        return
    # Lookup common Windows apps by name
    app_lookup = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "command prompt": "cmd.exe",
        "explorer": "explorer.exe",
        "wordpad": "write.exe",
        "task manager": "taskmgr.exe"
    }
    for key, exe in app_lookup.items():
        if key in app_name:
            try:
                subprocess.Popen(exe)
                speak(f"Opening {key}.")
            except Exception as e:
                speak(f"Failed to open {key}: {e}")
            return
    # Fallback to direct execution
    try:
        subprocess.Popen(app_name)
        speak(f"Opening {app_name}.")
    except Exception:
        speak("Couldn't open that application. Try a built-in app or check the name.")


def search_google():
    query = get_response("What would you like to search?")
    if not query:
        return
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    speak("Searching Google.")


def main():
    speak("Voice Assistant ready. Awaiting your command.")
    while True:
        command = listen() or ""
        cmd = command.lower()

        if "volume up" in cmd:
            change_volume("up")
        elif "volume down" in cmd:
            change_volume("down")
        elif "mute" in cmd:
            change_volume("mute")
        elif "unmute" in cmd:
            change_volume("unmute")
        elif "screenshot" in cmd:
            take_screenshot()
        elif "create folder" in cmd:
            create_folder()
        elif "delete folder" in cmd:
            delete_folder()
        elif "open folder" in cmd:
            open_folder()
        elif "close folder" in cmd:
            close_folder()
        elif "rename folder" in cmd:
            rename_folder()
        elif "open app" in cmd or "open application" in cmd:
            open_application()
        elif "search" in cmd:
            search_google()
        elif "exit" in cmd or "quit" in cmd:
            speak("Goodbye!")
            break
        else:
            speak("Command not recognized. Try again.")


if __name__ == "__main__":
    main()
