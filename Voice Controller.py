"""
Secure Voice Media Controller
Two-layer security: Startup password + Wake word
"""

import speech_recognition as sr
from pynput.keyboard import Key, Controller
import time
import json
import os
import hashlib

keyboard = Controller()
recognizer = sr.Recognizer()
recognizer.energy_threshold = 400

WAKE_WORD = "computer"
ACTIVE_SESSION_DURATION = 60
PASSWORD_FILE = "voice_password.json"
MAX_PASSWORD_ATTEMPTS = 3

session_active = False
last_command_time = 0
program_unlocked = False


def setup_password():
    """Set up the startup voice password"""
    print("=" * 60)
    print("STARTUP PASSWORD SETUP")
    print("=" * 60)
    print("Choose a secret password phrase.")
    print("Example: 'open sesame', 'alpha gamma', 'my secret code'")
    print("Use 2-3 words that are easy to remember.")
    print("=" * 60)

    while True:
        with sr.Microphone() as source:
            print("\nSay your new password...")
            recognizer.adjust_for_ambient_noise(source, duration=1)

            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                password_text = recognizer.recognize_google(audio).lower()

                print(f"You said: '{password_text}'")
                print("\nSay it again to confirm...")

                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                confirm_audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                confirm_text = recognizer.recognize_google(confirm_audio).lower()

                if password_text == confirm_text:
                    password_hash = hashlib.sha256(password_text.encode()).hexdigest()

                    with open(PASSWORD_FILE, 'w') as f:
                        json.dump({
                            'password_hash': password_hash,
                            'password_hint': password_text[:3] + "..."
                        }, f)

                    print("\n" + "=" * 60)
                    print("PASSWORD SET SUCCESSFULLY")
                    print("=" * 60)
                    print(f"Hint: {password_text[:3]}...")
                    print("Remember this password.")
                    print("=" * 60)

                    return password_text
                else:
                    print("Passwords do not match. Try again.")
                    print(f"First: '{password_text}'")
                    print(f"Second: '{confirm_text}'")

            except sr.UnknownValueError:
                print("Could not understand. Please try again.")
            except sr.RequestError:
                print("Network error. Check internet connection.")
            except Exception as e:
                print(f"Error: {e}")


def load_password():
    """Load the saved password configuration"""
    global program_unlocked

    if not os.path.exists(PASSWORD_FILE):
        print("No password found. First-time setup.")
        setup_password()
        return True

    try:
        with open(PASSWORD_FILE, 'r') as f:
            data = json.load(f)

        password_hint = data.get('password_hint', 'No hint')
        print(f"Password hint: {password_hint}")
        return True

    except:
        print("Error loading password file. Recreating...")
        setup_password()
        return True


def verify_password(spoken_text):
    """Verify the spoken password against stored hash"""
    try:
        with open(PASSWORD_FILE, 'r') as f:
            data = json.load(f)

        stored_hash = data.get('password_hash', '')
        current_hash = hashlib.sha256(spoken_text.lower().encode()).hexdigest()

        return current_hash == stored_hash

    except:
        return False


def unlock_program():
    """Unlock the program with voice password"""
    global program_unlocked

    if program_unlocked:
        return True

    print("\n" + "=" * 60)
    print("PROGRAM LOCKED")
    print("=" * 60)
    print("Say the startup password to unlock.")

    attempts = MAX_PASSWORD_ATTEMPTS

    while attempts > 0:
        with sr.Microphone() as source:
            print(f"\nAttempts remaining: {attempts}")
            print("Say password...")

            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                spoken_text = recognizer.recognize_google(audio)

                print(f"You said: '{spoken_text}'")

                if verify_password(spoken_text):
                    program_unlocked = True
                    print("\n" + "=" * 60)
                    print("ACCESS GRANTED")
                    print("=" * 60)
                    print("Program unlocked.")
                    print(f"Wake word: '{WAKE_WORD}'")
                    print("=" * 60)
                    return True
                else:
                    attempts -= 1
                    if attempts > 0:
                        print("Incorrect password. Try again.")
                    else:
                        print("Too many failed attempts.")
                        return False

            except sr.UnknownValueError:
                attempts -= 1
                print("Could not understand. Try again.")
            except sr.RequestError:
                print("Network error.")
            except Exception as e:
                attempts -= 1
                print(f"Error: {e}")

    return False


def lock_program():
    """Lock the program"""
    global program_unlocked, session_active
    program_unlocked = False
    session_active = False
    print("\n" + "=" * 60)
    print("PROGRAM LOCKED")
    print("=" * 60)


def control_media(command):
    """Execute media control commands"""
    command = command.lower()

    if any(word in command for word in ['play', 'pause', 'stop', 'resume']):
        keyboard.press(Key.media_play_pause)
        keyboard.release(Key.media_play_pause)
        print("Command: Play/Pause")
        return True

    elif any(word in command for word in ['next', 'skip']):
        keyboard.press(Key.media_next)
        keyboard.release(Key.media_next)
        print("Command: Next")
        return True

    elif any(word in command for word in ['previous', 'back']):
        keyboard.press(Key.media_previous)
        keyboard.release(Key.media_previous)
        print("Command: Previous")
        return True

    elif any(word in command for word in ['volume up', 'louder']):
        for _ in range(2):
            keyboard.press(Key.media_volume_up)
            keyboard.release(Key.media_volume_up)
            time.sleep(0.05)
        print("Command: Volume up")
        return True

    elif any(word in command for word in ['volume down', 'quieter']):
        for _ in range(2):
            keyboard.press(Key.media_volume_down)
            keyboard.release(Key.media_volume_down)
            time.sleep(0.05)
        print("Command: Volume down")
        return True

    elif 'mute' in command:
        keyboard.press(Key.media_volume_mute)
        keyboard.release(Key.media_volume_mute)
        print("Command: Mute")
        return True

    elif 'lock program' in command or 'lock system' in command:
        lock_program()
        print("Command: Lock program")
        return True

    print(f"Unknown command: {command}")
    return False


def display_status():
    """Display current program status"""
    print("\n" + "=" * 60)
    print("VOICE MEDIA CONTROLLER")
    print("=" * 60)

    if program_unlocked:
        print("Status: UNLOCKED")
        if session_active:
            remaining = ACTIVE_SESSION_DURATION - (time.time() - last_command_time)
            print(f"Session: ACTIVE ({int(remaining)} seconds remaining)")
        else:
            print(f"Session: INACTIVE (say '{WAKE_WORD}' to activate)")
    else:
        print("Status: LOCKED")
        print("Say startup password to unlock")

    print("\nAvailable Commands:")
    print("-" * 60)
    print("Media: play, pause, next, previous, volume up/down, mute")
    print("System: lock program")
    print("-" * 60)
    print("Press Ctrl+C to exit")
    print("=" * 60)


def main():
    """Main program loop"""
    global session_active, last_command_time, program_unlocked

    print("=" * 60)
    print("SECURE VOICE MEDIA CONTROLLER")
    print("=" * 60)
    print("Security layers:")
    print("1. Startup password (voice)")
    print(f"2. Wake word: '{WAKE_WORD}'")
    print("=" * 60)

    if not load_password():
        print("Failed to setup password system.")
        return

    try:
        while True:
            if not program_unlocked:
                if not unlock_program():
                    print("Failed to unlock. Exiting.")
                    break
                display_status()

            if session_active:
                elapsed = time.time() - last_command_time
                if elapsed > ACTIVE_SESSION_DURATION:
                    session_active = False
                    print("\nSession expired")
                    display_status()
                    continue

                with sr.Microphone() as source:
                    remaining = ACTIVE_SESSION_DURATION - elapsed
                    print(f"\nListening for command... ({int(remaining)} seconds)")

                    try:
                        recognizer.adjust_for_ambient_noise(source, duration=0.2)
                        audio = recognizer.listen(source, timeout=3, phrase_time_limit=2)

                        command = recognizer.recognize_google(audio)
                        print(f"Command: {command}")

                        if control_media(command):
                            last_command_time = time.time()

                    except sr.UnknownValueError:
                        pass
                    except Exception as e:
                        print(f"Error: {e}")

            else:
                with sr.Microphone() as source:
                    try:
                        recognizer.adjust_for_ambient_noise(source, duration=0.3)
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=1)

                        text = recognizer.recognize_google(audio).lower()

                        if WAKE_WORD in text:
                            print(f"\nWake word detected: '{text}'")
                            session_active = True
                            last_command_time = time.time()
                            print(f"Session activated for {ACTIVE_SESSION_DURATION} seconds")

                        elif 'lock' in text:
                            lock_program()

                    except sr.UnknownValueError:
                        pass
                    except Exception:
                        pass

                time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nProgram terminated.")
        lock_program()


if __name__ == "__main__":
    main()