import speech_recognition as sr
import queue



class SpeechRecog():
    def __init__(self, state_queue=None):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.state = "Idle"
        self.state_queue = state_queue

    def set_state(self, state: str):
        self.state = state
        self.state_queue.put(self.state)

    def listen_for_speech(self):
        text = ""
        # Use the default microphone as the audio source
        with self.microphone as source:
            self.set_state("Listening...")
            # Listen for the first phrase and extract it into audio data
            audio_data = self.recognizer.listen(source)
            self.set_state("Recognizing...")
            
            try:
                # Recognize speech using Google Web Speech API
                text = self.recognizer.recognize_google(audio_data)
                #print(f"You said: {text}")
            except sr.UnknownValueError:
                print("Google Web Speech API could not understand the audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Web Speech API; {e}")
        self.set_state("Idle")
        return text