"""
Voice-Controlled Media Player - Phase 2
Wake Word Detection: "Computer"
Multi-Command Mode: Stays active for 1 minute
"""

import speech_recognition as sr
from pynput.keyboard import Key, Controller
import time
import threading

# Initialize
keyboard = Controller()
recognizer = sr.Recognizer()

# Adjusted settings for built-in microphones
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_adjustment_damping = 0.15
recognizer.dynamic_energy_ratio = 1.5
recognizer.pause_threshold = 1.0

# Wake word and session settings
WAKE_WORD = "computer"
ACTIVE_SESSION_DURATION = 60  # seconds (1 minute)
last_command_time = 0
session_active = False


def control_media(command):
    """Send media control command based on voice input"""
    command = command.lower()

    # Volume up commands
    if any(word in command for word in ['volume up', 'increase volume', 'louder', 'turn up']):
        keyboard.press(Key.media_volume_up)
        keyboard.release(Key.media_volume_up)
        print("Executed: volume up")
        return True

    # Volume down commands
    elif any(word in command for word in ['volume down', 'decrease volume', 'quieter', 'turn down', 'lower volume']):
        keyboard.press(Key.media_volume_down)
        keyboard.release(Key.media_volume_down)
        print("Executed: volume down")
        return True

    # Mute/unmute commands
    elif any(word in command for word in ['mute', 'unmute', 'silence']):
        keyboard.press(Key.media_volume_mute)
        keyboard.release(Key.media_volume_mute)
        print("Executed: mute/unmute")
        return True

    # Basic media control commands
    commands = {
        'pause': Key.media_play_pause,
        'stop': Key.media_play_pause,
        'play': Key.media_play_pause,
        'resume': Key.media_play_pause,
        'next': Key.media_next,
        'skip': Key.media_next,
        'previous': Key.media_previous,
        'back': Key.media_previous,
    }

    for keyword, key in commands.items():
        if keyword in command:
            keyboard.press(key)
            keyboard.release(key)
            print(f"Executed: {keyword}")
            return True

    print("Unknown command")
    return False


def get_remaining_time():
    """Calculate remaining time in active session"""
    global last_command_time
    elapsed = time.time() - last_command_time
    remaining = max(0, ACTIVE_SESSION_DURATION - elapsed)
    return remaining


def is_session_active():
    """Check if session is still active"""
    global session_active, last_command_time

    if not session_active:
        return False

    elapsed = time.time() - last_command_time

    if elapsed >= ACTIVE_SESSION_DURATION:
        session_active = False
        return False

    return True


def activate_session():
    """Activate the command session"""
    global session_active, last_command_time
    session_active = True
    last_command_time = time.time()
    print("\nSession activated! You have 1 minute to give commands.")


def refresh_session():
    """Refresh the session timer after each command"""
    global last_command_time
    last_command_time = time.time()


def listen_for_wake_word():
    """Listen for the wake word 'Computer'"""
    with sr.Microphone() as source:
        print("\nWaiting for wake word...")

        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)

            text = recognizer.recognize_google(audio)
            text_lower = text.lower()

            # Check if wake word is detected
            if WAKE_WORD in text_lower:
                print(f"Wake word detected: {text}")
                return True
            else:
                # Only show if something other than wake word was said
                if len(text.strip()) > 0:
                    print(f"Heard: {text} (not wake word)")
                return False

        except sr.WaitTimeoutError:
            return False
        except sr.UnknownValueError:
            return False
        except sr.RequestError:
            print("Network error - check internet connection")
            return False
        except Exception as e:
            return False

    return False


def listen_for_command():
    """Listen for voice command during active session"""
    with sr.Microphone() as source:
        remaining = get_remaining_time()
        print(f"\nListening for command... ({int(remaining)}s remaining)")

        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)

            # Use remaining time as timeout
            timeout = min(remaining + 1, 6)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=5)

            print("Processing...")
            text = recognizer.recognize_google(audio)
            print(f"Command: {text}")
            return text

        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("Could not understand")
            return None
        except sr.RequestError:
            print("Network error")
            return None
        except Exception as e:
            return None

    return None


def test_microphone():
    """Test and display available microphones"""
    print("\nDetecting available microphones...")

    try:
        mic_list = sr.Microphone.list_microphone_names()
        print(f"\nFound {len(mic_list)} microphone(s):")
        for i, name in enumerate(mic_list):
            print(f"  [{i}] {name}")

        return True
    except Exception as e:
        print(f"Error detecting microphones: {e}")
        return False


def display_info():
    """Display program information and commands"""
    print("\n" + "=" * 60)
    print("WAKE WORD: 'Computer'")
    print("MODE: Multi-Command (1 minute active window)")
    print("=" * 60)
    print("\nHow to use:")
    print("  1. Say 'Computer'")
    print("  2. System stays active for 1 minute")
    print("  3. Give multiple commands within that time")
    print("  4. Each command resets the 1 minute timer")
    print("  5. After 1 minute of no commands, returns to wake word")
    print("\n" + "=" * 60)
    print("AVAILABLE COMMANDS:")
    print("-" * 60)
    print("Playback Control:")
    print("  - pause, stop       : Pause media")
    print("  - play, resume      : Play/resume media")
    print("  - next, skip        : Next track")
    print("  - previous, back    : Previous track")
    print("\nVolume Control:")
    print("  - volume up, louder      : Increase volume")
    print("  - volume down, quieter   : Decrease volume")
    print("  - mute, unmute           : Toggle mute")
    print("-" * 60)


def main():
    """Main program"""
    print("=" * 60)
    print("Voice Media Control - Phase 2: Multi-Command Mode")
    print("=" * 60)

    # Test microphones
    test_microphone()

    # Display info
    display_info()

    print("\nPress Ctrl+C to exit")
    print("=" * 60)

    try:
        while True:
            # Check if session is active
            if is_session_active():
                # Session is active, listen for commands
                command = listen_for_command()

                if command:
                    # Execute command and refresh session timer
                    control_media(command)
                    refresh_session()
                else:
                    # Check if session expired during listening
                    if not is_session_active():
                        print("\nSession expired. Waiting for wake word...")

            else:
                # No active session, wait for wake word
                wake_word_detected = listen_for_wake_word()

                if wake_word_detected:
                    activate_session()

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nExiting program. Goodbye!")


if __name__ == "__main__":
    main()