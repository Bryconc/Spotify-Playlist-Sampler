__author__ = 'Brycon'

import Queue as q
import threading
import os
import winsound


class WinPlayer(object):
    """
        Player object for a Windows machine. Created to circumvent the issues with
        PyAudio on a Windows machine. The player, once created, can be queued up with songs and
        will play once the 'play' method is called.
    """
    def __init__(self, callback=None):
        """
            Constructor for WinPlayer. Initializes the internal song queue and
            play thread.

        :param callback: An optional function that will be called at the start
            of every new track played during the play thread.
        """
        self.song_queue = q.Queue()
        self.play_thread = PlayThread(self, threading.Event(), callback)
        self.playing = False
        self.play_thread.pause()
        self.play_thread.start()

    def add_audio(self, audio, track):
        """
            Queues audio to be played through the player.
        :param audio: The WAV file to be queued for play. Should be the location of the file.
        :param track: A dictionary in the Spotify Track notation, corresponding
            to the audio track being played.
        :raises: TypeError: audio argument was not a WAV file
        """
        if not WinPlayer.__is_wav_file(audio):
            raise TypeError("File must be of type .WAV")

        self.song_queue.put((audio, track))

    def play(self):
        """
            Starts the Player if not already playing.
        """
        if not self.playing:
            self.playing = True
            self.play_thread.play()

    def pause(self):
        """
            Pauses the Player if not already paused.
            Player will be paused at the END of the current playing file
        """
        if self.playing:
            self.playing = False
            self.play_thread.pause()
            print("Player will pause at the end of the current audio.")

    def paused(self):
        """
            Checks to see if the player is paused.
            :return: True if the player is paused. False otherwise.
        """
        return self.play_thread.is_paused()

    def stop(self, count=True):
        """
            Stops the Player permanently.
        :param count: Optional boolean to determine if the count thread should continue.
        """
        self.play_thread.stop(count)

    def get_next_audio(self):
        """
            Gets the next audio file on the Player queue. Used by the underlying thread to get the next
            audio to play.
        :return: A set object containing the WAV file URL and Track information.
        """
        return self.song_queue.get()

    def wait_until_finished(self, callback):
        """
            When called, the calling thread will initiate a call
            to the parameter function once the Player has finished
            running. Can be combined with the stop function.
        :param callback: Function that will be called once execution of the Player
        has finished.
        """
        self.play_thread.call_when_finished(callback)

    def get_time(self):
        """
            Gets the time of the currently playing track.
        :return: Time of the currently playing track.
        """
        return self.play_thread.get_time()


    @staticmethod
    def __is_wav_file(audio):
        """
            Checks if the file URL passed is a WAV file.
        :param audio: File URL
        :return: True if the URL is for a WAV file other wise returns False
        """
        file_name, file_extension = os.path.splitext(audio)
        return file_extension == '.wav'


class PlayThread(threading.Thread):
    """
        Inner play thread for the Player Object
        While executes, plays tracks from the Player's Queue in continuous
        succession if not paused.
    """
    def __init__(self, player, event, callback):
        """
            Constructor for the PlayThread
        :param player: a reference to the overarching Player Object
        :param event: a reference to the event which will keep track of pauses of the Player
        :param callback: the function that will be called at the start of every new track.
        """
        super(PlayThread, self).__init__()
        self.player = player
        self.play_event = event
        self.current_audio = None
        self.callback = callback
        self.finish_callback = None
        self.running = False
        self.paused = True
        self.timer = TimerThread(callback)
        self.timer.start()

    def run(self):
        """
            Thread's run function. Will be called once start() is called on the Thread.
            While the Player is running, will continuously pull tracks from the parent Player's
            queue and play them through WinSound, calling the callback function at the start of each one.
        """
        self.running = True
        while self.running:
            if self.play_event.is_set():
                self.paused = False
                next_audio, track = self.player.get_next_audio()
                self.current_audio = track
                if self.callback:
                    self.callback(track=track)
                self.timer.reset_count()
                winsound.PlaySound(next_audio, winsound.SND_FILENAME | winsound.SND_NOSTOP)
            else:
                self.paused = True
                self.play_event.wait()
        if self.finish_callback:
            self.timer.stop()
            self.finish_callback()

    def stop(self, count):
        """
            Stops the player permanently.
        :param count: Determines if the timer should continue to count. True if it should continue
        false otherwise.
        """
        self.running = False
        if not count:
            self.timer.stop()

    def pause(self):
        """
            Pauses the PlayThread.
        """
        self.play_event.clear()

    def is_paused(self):
        """
            Determines if the PlayThread is currently paused.
        :return: True if currently paused, False otherwise.
        """
        return self.paused

    def play(self):
        """
            Resumes the PlayThread after it has been paused.
        """
        self.play_event.set()

    def get_time(self):
        """
            Gets the time of the current track being played.
        :return: The time of the current track being played.
        """
        return self.timer.get_count()

    def call_when_finished(self, callback):
        """
            Sets the callback function of the PlayThread to the function specified.
            PlayThread can only call one function when finished.
        :param callback: Function to be called once the PlayThread finishes.
        """
        self.finish_callback = callback


class TimerThread(threading.Thread):
    """
        Thread to keep track of the time of each track that is played.
    """

    def __init__(self, callback=None):
        """
            Constructor for the TimerThread.
        :param callback: Callback function for every increment of the time.
        """
        super(TimerThread, self).__init__()
        self.time_event = threading.Event()
        self.count = 0
        self.callback = callback
        self.running = False

    def run(self):
        """
            Thread's run function. Will be called once start() is called on the Thread.
            While running, will increment the count by 1 and then wait a full second before repeating
            the process.
        """
        self.running = True
        while not self.time_event.wait(1) and self.running:
            self.count += 1
            if self.callback:
                self.callback(count=self.count)

    def stop(self):
        """
            Stops the TimerThread.
        """
        self.running = False

    def get_count(self):
        """
            Gets the count of the current TimerThread.
        :return: The count of the current TimerThread.
        """
        return self.count

    def reset_count(self):
        """
            Resets the count of the Timer back to 0.
            Updates the callback.
        """
        self.count = 0
        self.callback(count=self.count)

