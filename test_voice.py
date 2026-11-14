
import pyttsx3

engine = pyttsx3.init("sapi5")
print("Available voices:")

for voice in engine.getProperty("voices"):
    print(voice.name, voice.id)

engine.setProperty("rate", 170)
engine.say("Hello Shivam, can you hear me?")
engine.runAndWait()

print("Test finished.")
