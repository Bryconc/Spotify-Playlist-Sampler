__author__ = 'Brycon'

import os
import Queue
import ssl
import tempfile
import threading
import urllib

import echonest.remix.support.ffmpeg as ffmpeg


DEBUG_ANALYZER = False

DOWNLOAD_DIRECTORY = "util/Temp_Directory/"


class DownloaderThread(threading.Thread):
    """
        The DownloaderThread object.
        Maintains a queue of tracks to download.
        Downloads and places in temporary directory
        Passes downloaded file unto the Converter
    """
    def __init__(self, analyzer_thread, amount=0):
        """
            The Constructor for the DownloaderThread.

        :param analyzer_thread: A reference to the Converter to pass the downloaded file to.
        :param amount: The amount of downloads expected.
        """
        super(DownloaderThread, self).__init__()
        self.download_queue = Queue.Queue()
        self.analyzer_thread = analyzer_thread
        self.amount = amount
        self.downloaded = 0
        self.running = False

    def queue_download(self, track):
        """
            Appends the SpotifyTrack object to the download queue.
        :param track:
        """
        self.download_queue.put(track)

    def stop(self):
        """
            Stops the DownloaderThread.
        """
        self.running = False

    def run(self):
        """
            Run method for the Thread object. Call Thread.start() instead.
        """
        self.running = True
        while self.downloaded < self.amount and self.running:
            try:
                track = self.download_queue.get()
                # print("Downloading new track... %d of %d" % (self.downloaded, self.amount))
                if not os.path.isfile(DOWNLOAD_DIRECTORY + track['track']['id'] + ".mp3"):
                    mp3file, headers = urllib.urlretrieve(track['track']['preview_url'],
                                                          DOWNLOAD_DIRECTORY + track['track']['id'] + ".mp3")
                    self.analyzer_thread.queue_analysis(mp3file, track)
                else:
                    self.analyzer_thread.queue_analysis(DOWNLOAD_DIRECTORY + track['track']['id'] + ".mp3", track)
                self.downloaded += 1
            except ssl.SSLError:
                print("***** Error downloading " + track['track']['name'] + " *****")
                self.queue_download(track)

    @staticmethod
    def unload():
        """
            Unloading mechanic for the DownloadThread. Deletes the downloaded MP3 files.
        """
        for dl_file in os.listdir(DOWNLOAD_DIRECTORY):
            if dl_file.endswith(".mp3"):
                try:
                    os.remove(DOWNLOAD_DIRECTORY + dl_file)
                except WindowsError:
                    print("Error with " + dl_file)


class ConverterThread(threading.Thread):
    """
        Converter thread for converting MP3 files to WAV
        Maintains a queue of tracks to convert.
        Converts and places in the %temp% directory
        Passes converted file unto the Player
    """
    def __init__(self, player, amount=0):
        """
            Constructor for the ConverterThread.

        :param player: a reference to the player to pass on the WAV file to
        :param amount: The expected amount of conversions
        """
        super(ConverterThread, self).__init__()
        self.analyze_queue = Queue.Queue()
        self.player = player
        self.amount = amount
        self.analyzed = 0
        self.running = False
        self.af_list = []

    def stop(self):
        """
            Stops the ConverterThread
        """
        self.running = False

    def queue_analysis(self, mp3_file, track):
        """
            Queues the conversion of track object to WAV
        :param mp3_file: Mp3 File of track
        :param track: Spotify track object
        """
        self.analyze_queue.put((mp3_file, track))

    def run(self):
        """
            Run method for the Thread object. Use Thread.start() instead.
        """
        self.running = True
        while self.analyzed < self.amount and self.running:
            try:
                # print("Checking for new analysis... %d of %d with queue size %d" % (
                # self.analyzed, self.amount, self.analyze_queue.qsize()))
                mp3file, track = self.analyze_queue.get()
                af = ConverterThread.convert_to_wav(mp3file)
                self.af_list.append(af)
                self.player.add_audio(af, track)
                self.analyzed += 1
            except RuntimeError as e:
                print("***** Error processing " + track['track']['name'] + " *****")
                print(e)
                self.amount -= 1

    def unload(self):
        """
            Unload mechanism for the ConverterThread. Deleted the temporary WAV files
        """
        print("Deleting temp wav files")
        for af in self.af_list:
            try:
                os.remove(af)
            except WindowsError as e:
                print("Error with " + str(af))


    @staticmethod
    def convert_to_wav(mp3file):
        """
            Method for converting an MP3 file to a WAV file.
        :param mp3file: MP3 File to convert
        :return : Returns a reference to WAV file
        """
        temp_file_handle, converted_file = tempfile.mkstemp(".wav")
        ffmpeg.ffmpeg(mp3file, converted_file, overwrite=True, numChannels=2, sampleRate=44100, verbose=DEBUG_ANALYZER)
        os.close(temp_file_handle)
        return converted_file