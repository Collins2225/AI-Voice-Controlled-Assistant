"""
Voice-Controlled Media Player - Phase 1 Enhanced
Optimized for built-in microphones (no headset required)
Includes: play, pause, next, previous, volume control, and mute
"""

import speech_recognition as sr
from pynput.keyboard import Key, Controller
import time

# Initialize
keyboard = Controller()
recognizer = sr.Recognizer()

# Adjusted settings for built-in microphones
recognizer.energy_threshold = 300  # Lower threshold for quieter mics
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_adjustment_damping = 0.15
recognizer.dynamic_energy_ratio = 1.5
recognizer.pause_threshold = 1.0  # Slightly longer pause detection


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


def listen():
    """Listen and convert speech to text"""
    with sr.Microphone() as source:
        print("\nListening...")

        try:
            # Longer ambient noise adjustment for built-in mics
            print("Calibrating microphone...")
            recognizer.adjust_for_ambient_noise(source, duration=1.0)

            # Listen with longer timeout and phrase limit
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)

            print("Processing...")
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text

        except sr.WaitTimeoutError:
            print("Timeout - no speech detected")
        except sr.UnknownValueError:
            print("Could not understand")
        except sr.RequestError:
            print("Network error - check internet connection")

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


def display_commands():
    """Display all available commands"""
    print("\nAVAILABLE COMMANDS:")
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
    print("Voice Media Control - Enhanced Version")
    print("=" * 60)

    # Test microphones
    test_microphone()

    print("\n" + "=" * 60)

    # Display all commands
    display_commands()

    print("\nPress Ctrl+C to exit")
    print("\nTIP: Speak clearly and wait for 'Listening...' prompt")
    print("=" * 60)

    try:
        while True:
            text = listen()
            if text:
                control_media(text)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\nExiting program. Goodbye!")


if __name__ == "__main__":
    main()