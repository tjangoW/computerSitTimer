"""
Convert mp3 to wav format for the AudioPlayer
"""
# from https://realpython.com/playing-and-recording-sound-python/#pydub_1


import pydub
sound = pydub.AudioSegment.from_mp3("River_birds-1m.mp3")
sound.export("River_birds-1m.mp3.wav", format="wav")
