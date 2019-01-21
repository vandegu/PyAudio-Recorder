# Import the necessary modules.
import pyaudio
import wave
import os
import click
import numpy as np
import matplotlib.pyplot as plt

# I'm much obliged to user6038351 on stackoverflow for providing framework for much of this code
# (see post here: https://stackoverflow.com/questions/43521804/recording-audio-with-pyaudio-on-a-button-click-and-stop-recording-on-another-but/51229082#51229082)
#
# I'm also much obliged to Dr. Eric Bruning for his insights and code on how to use fft, display audio,
# and answering my general geeky Python questions. See his code here:
# https://gist.github.com/deeplycloudy/2152643


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

    def dB(self,a,base=1.0):
        return 10.0*np.log10(a/base)


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
        #plt.plot(np.arange(frames)/self.RATE,audio)
        fs = self.RATE
        audio_fft = np.fft.fft(audio)
        freqs = np.fft.fftfreq(audio.shape[0], 1.0/fs) / 1000.0
        max_freq_kHz = freqs.max()
        times = np.arange(audio.shape[0]) / float(fs)
        fftshift = np.fft.fftshift

        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(8.5,11))
        ax_spec_gram = fig.add_subplot(312)
        ax_fft  = fig.add_subplot(313)
        ax_time = fig.add_subplot(311)
        plt.gcf().subplots_adjust(bottom=0.15)

        ax_spec_gram.specgram(audio, Fs=fs, cmap = 'jet')#cmap='gist_heat')
        ax_spec_gram.set_xlim(0,duration)
        ax_spec_gram.set_ylim(0,max_freq_kHz*1000.0)
        ax_spec_gram.set_ylabel('Frequency (Hz)')
        ax_spec_gram.set_xlabel('Time (s)')

        ax_fft.plot(fftshift(freqs), fftshift(self.dB(audio_fft)))
        ax_fft.set_xlim(0,max_freq_kHz)
        ax_fft.set_xlabel('Frequency (kHz)')
        ax_fft.set_ylabel('dB')

        ax_time.plot(np.arange(frames)/self.RATE,audio/audio.max())
        ax_time.set_xlabel('Time (s)')
        ax_time.set_ylabel('Relative amplitude')
        ax_time.set_xlim(0,duration)

        plt.tight_layout()
        plt.show()




# Create an object of the ProgramGUI class to begin the program.
guiAUD = RecAUD()
