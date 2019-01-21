# Import the necessary modules.
import pyaudio
import wave
import os
import click
import numpy as np
import matplotlib.pyplot as plt


class RecAUD:

    def __init__(self, chunk=3024, frmat=pyaudio.paInt16, channels=1, rate=22000, py=pyaudio.PyAudio()):

        # Start Tkinter and set Title
        self.collections = []
        self.CHUNK = chunk
        self.FORMAT = frmat
        self.CHANNELS = channels
        self.RATE = rate
        self.p = py
        self.frames = []
        self.st = 1
        self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        self.filename = 'test_recording.wav'

        # Call the main method to initate the loop:
        self.main()

    def main(self,):
        # Start the mainloop, which will be indefinite until 'q' is pressed.
        mainloop = True
        while mainloop:
            key = click.getchar()
            print(key)

            if key == 'q' or key == 'Q':
                mainloop = False

            if key == 'r':
                print('* starting recording, press ctrl+c to stop...')
                self.start_record()

            if key == 'p':
                print('* replaying clip')
                self.replay()

            if key =='d':
                print('* displaying..\n\n')
                self.display()


    def start_record(self):
        self.st = 1
        self.frames = []
        stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)

        # somewhat kludgy way to interrupt an active stream, but it works:
        try:
            while self.st == 1:
                data = stream.read(self.CHUNK)
                self.frames.append(data)
                print("* recording")
        except KeyboardInterrupt:
            print('* recording stopped, saved to {}'.format(self.filename))

        stream.close()

        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def stop(self):
        self.st = 0

    def replay(self):
        play=pyaudio.PyAudio()
        stream_play=play.open(format=self.FORMAT,
                              channels=self.CHANNELS,
                              rate=self.RATE,
                              output=True)
        for data in self.frames:
            stream_play.write(data)
        stream_play.stop_stream()
        stream_play.close()
        play.terminate()

    def display(self):
        wf = wave.open(self.filename, 'rb')
        frames = wf.getnframes()
        #rate = wf.getframerate()
        duration = frames / float(self.RATE)
        bytes_per_sample = wf.getsampwidth()
        bits_per_sample  = bytes_per_sample * 8
        dtype = 'int{0}'.format(bits_per_sample)
        audio = np.fromstring(wf.readframes(int(duration*self.RATE*bytes_per_sample/self.CHANNELS)), dtype=dtype)
        #print(audio)
        plt.plot(audio)
        plt.show()




# Create an object of the ProgramGUI class to begin the program.
guiAUD = RecAUD()
