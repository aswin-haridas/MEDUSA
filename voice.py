import speech_recognition as sr
import pyttsx3
import time


def initialize_tts_engine():
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
    return engine


def recognize_speech_from_mic(recognizer, microphone):
    with microphone as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand the audio"
    except sr.RequestError as e:
        return f"Error with speech recognition service: {e}"


def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    tts_engine = initialize_tts_engine()

    print("Speak into your microphone. Say 'exit' to stop.")

    while True:
        text = recognize_speech_from_mic(recognizer, microphone)
        print(f"You said: {text}")

        # Convert recognized text back to speech
        if text.strip() and text != "Could not understand the audio":
            tts_engine.say(text)
            tts_engine.runAndWait()

        # Exit condition
        if text.lower() == "exit":
            print("Exiting...")
            tts_engine.say("Goodbye")
            tts_engine.runAndWait()
            break


if __name__ == "__main__":
    main()