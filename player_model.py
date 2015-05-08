__author__ = 'Brycon'

import datetime
import os
import pickle
import subprocess as sp
from functools import partial
from random import shuffle

import spotipy
import spotipy.util

import winplayer
from util.threads import DownloaderThread, ConverterThread
from util.observable import Observable


RECENT_PICKLE_FILE = "util/recent_playlists.p"
RECENT_LIMIT = 5

CLIENT_ID = "1e9958fdd24746aea8959ccf6f724441"
CLIENT_SECRET = "a5bcdc07002c463f87a7d827c1638b91"
REDIRECT_URI = "http://student.cs.appstate.edu/carpenterba/SpotifySampler/callback.html"


class Model(Observable):
    """
        Model object in the MVC pattern. Processes all the logic for the playlist sampling.
    """
    def __init__(self):
        """
            Constructor the Model object.
        """
        super(Model, self).__init__()

        self.recent_playlists = self.__load_recent_playlists()

        self.master_track_list = []
        self.playlist_list = []
        self.favorites_list = []
        self.current_track_number = 0
        self.playlist_amount = 0

        self.sp = None
        self.current_track = None
        self.player = None
        self.analyzer = None
        self.downloader = None

    def setup(self):
        """
            Handles setting up the Model to sample a playlist. Spotify Playlist has already been set.
        """
        if not self.spotify_playlist:
            raise InvalidInputException("You must set the spotify playlist, before you can start the player.")

        if self.player:
            call_play = True
        else:
            call_play = False

        print("\nSampling playlist: %s" % self.spotify_playlist["name"])
        self.__load_tracks()
        self.playlist_amount = self.get_playlist_track_number()
        print("With a total of %d preview-able tracks" % self.playlist_amount)
        self.current_track_number = 0

        self.player = winplayer.WinPlayer(self.notify_observers)
        self.analyzer = ConverterThread(self.player, self.playlist_amount)
        self.analyzer.start()
        self.downloader = DownloaderThread(self.analyzer, self.playlist_amount)
        self.downloader.start()

        if call_play:
            self.on()

        self.__grab_tracks()

    def on(self):
        """
            Sets the Model to start playing tracks.
        """
        self.player.play()

    def off(self):
        """
            Paused the Model from playing any more tracks.
        """
        self.player.pause()

    def set_spotify_playlist(self, username, playlist):
        """
            Sets the Spotify Playlist with the information specified.
            Information can be found in the URL for the Spotify Playlist.
            https://play.spotify.com/user/<username>/playlist/<playlist>

        :param username: User ID that owns the Spotify Playlist
        :param playlist: Playlist ID for that playlist
        """
        self.__set_spotipy_info(username, playlist)
        self.__authenticate_login()
        self.__retrieve_playlist()
        self.setup()

    def get_user_playlists(self):
        """
            Gets the Spotify Playlists owned by the User that has already been authenticated.

        :return: A list of Spotify Playlist Objects owned by the user currently authenticated.
        """
        if not self.sp:
            return None

        return self.sp.user_playlists(self.sp.current_user()['id'])

    def get_current_username(self):
        """
            Gets the username of the currently authenticated user.

        :return: A String of the currently authenticated user's username.
        """
        if not self.sp:
            return "(Not Logged In)"

        return self.sp.current_user()['id']

    def get_current_track(self):
        """
            Gets the current track.

        :return: A SpotifyTrack object of the current playing track.
        """
        return self.current_track

    def get_current_track_number(self):
        """
            Gets the current track number.

        :return: An integer value representing the track number of the currently playing track.
        """
        return self.current_track_number

    def get_playlist_amount(self):
        """
            Gets the number of tracks sampled in the playlist.

        :return: The number of total tracks sampled in this playlist.
        """
        return self.playlist_amount

    def get_favorites_list(self):
        """
            Gets the list of favorited songs.

        :return: A list containing SpotifyTrack objects of each favorited song.
        """
        return self.favorites_list

    def get_master_track_list(self):
        """
            Gets the master track list for the current sampling playlist.

        :return: A list containing SpotifyTrack objects of all tracks in the current playlist.
        """
        return self.master_track_list

    def get_recent_playlists(self):
        """
            Gets the dictionary representing the recent playlists sampled.

        :return: A dictionary containing playlist id, playlist owner, playlist name, and date sampled for each of the
            five most recent playlists sampled.
        """
        return self.recent_playlists

    def get_playlist_list(self):
        """
            Gets the list of played songs.

        :return: A list containing SpotifyTrack objects of each played song.
        """
        return self.playlist_list

    def get_playlist(self):
        """
            Gets the Spotify Playlist Object of the current Spotify Playlist.

        :return: A Spotify Playlist Object of the currently sampling playlist
        """
        return self.spotify_playlist

    def get_playlist_track_number(self):
        """
            Gets the number of tracks sampled in the playlist.

        :return: The number of total tracks sampled in this playlist.
        """
        return len(self.master_track_list)

    def shuffle_playlist(self):
        """
            Shuffles the ordering of the current playlist. Master track list should be set.
        """
        shuffle(self.master_track_list)

    def notify_observers(self, *args, **kwargs):
        """
            Observer notification method of the Observer pattern.
        """
        if 'track' in kwargs:
            self.current_track = kwargs['track']
            self.current_track_number += 1

        super(Model, self).notify_observers(*args, **kwargs)

    def unload_player(self, callback, wait=True):
        """
            Handles the logic for unloading the player once it has been terminated.

        :param callback: The method to be called once unloading has finished.
        :param wait: Boolean value for deciding if we should waiting until the current track has finished
            playing. Default value is true.
        """
        if self.player:
            self.player.stop()
            if self.player.paused():
                wait = False
            if self.player.get_time() > 30:
                wait = False

        if self.analyzer:
            self.analyzer.stop()
            self.analyzer.unload()

        if self.downloader:
            self.downloader.stop()
            DownloaderThread.unload()

        if self.player and wait:
            self.player.wait_until_finished(callback)

    def new_playlist(self, user_id, playlist_id):
        """
            Handles the logic of sampling a new playlist, with the information specified.

        :param user_id: User ID of the playlist being sampled
        :param playlist_id: Playlist ID of the playlist being sampled.
        """
        if self.player:
            self.unload_player(partial(self.set_spotify_playlist, user_id, playlist_id))
        else:
            self.set_spotify_playlist(user_id, playlist_id)

    def export_favorites(self, export_type, **kwargs):
        """
            Method for exporting favorites. Method determined by export_type.

            If export_type is 'csv' will export to CSV file.
            If export_type is 'existing' will export to an existing Spotify Playlist
            If export_type is 'new' will export to a new Spotify Playlist

        :param export_type: The type of export being performed.
        :param kwargs: Needed by the various forms of exporting. See individual export methods for more information.
        """
        try:
            print("Exporting favorites type %s" % export_type)
            if export_type == 'csv':
                self.export_csv(**kwargs)
            elif export_type == 'existing':
                self.export_existing_playlist(kwargs["user"], kwargs["playlist"])
            elif export_type == 'new':
                self.export_new_playlist(kwargs["playlist"])
        except spotipy.SpotifyException as e:
            print("Checking exception: %s" % e.message)
            if "The access token expired" in e.message:
                print("Token expired: attempting to re-authenticate login.")
                self.__authenticate_login()
                self.export_favorites(export_type, **kwargs)
            else:
                raise

    def export_csv(self, **kwargs):
        """
            Method for handling exporting to a CSV file.

            :param file_name: The name of the file to be exported to
            :param information: A list of the information to be exported.
                Handles 'name', 'artists', 'album',  and 'preview_url'
        """
        file_name = kwargs['file_name']
        information = kwargs['information']

        with open(file_name + ".csv", 'w') as csv_file:
            for track in self.favorites_list:
                information_list = []

                if 'name' in information:
                    information_list.append(track['track']['name'])

                if 'artists' in information:
                    artists = [x['name'] for x in track['track']['artists']]
                    information_list.append("-".join(artists))

                if 'album' in information:
                    information_list.append(track['track']['album']['name'])

                if 'preview_url' in information:
                    information_list.append(track['track']['preview_url'])

                csv_file.write(",".join(information_list) + "\n")

        sp.call(["notepad.exe ", file_name + ".csv"])

    def export_existing_playlist(self, user, playlist):
        """
            Method for exporting favorited tracks to an existing Spotify Playlist.

        :param user: the User ID of the existing playlist
        :param playlist: the Playlist ID of the existing playlist
        """
        self.__append_to_playlist(user, playlist)

    def export_new_playlist(self, playlist):
        """
            Method for exporting favorited tracks to a new Spotify Playlist

        :param playlist: the name of the new Spotify Playlist
        """

        user = self.sp.current_user()['id']
        playlist = self.sp.user_playlist_create(user, playlist, public=False)
        self.__append_to_playlist(user, playlist['id'])

    ###################################
    # #
    # BEGIN PRIVATE UTILITY METHODS  #
    # #
    ###################################

    def __set_spotipy_info(self, username, playlist_id):
        """
            Sets the information for playlist sampling

        :param username: the User ID of the sampled playlist
        :param playlist_id: the Playlist ID of the sampled playlist
        """
        self.spotipy_username = username
        self.spotipy_playlist_id = playlist_id

    def __authenticate_login(self):
        """
            Method for authenticating login with Spotify. Spotify Information should be set first.
        """
        token = self.__request_spotipy_token()
        if token:
            self.__request_spotipy_object(token)

    def __request_spotipy_token(self):
        """
            Method for requesting the Spotify access token.

        :return: A valid Spotify access token
        """
        if not self.spotipy_username or not self.spotipy_playlist_id:
            raise InvalidInputException("You must set the spotipy information first.")

        scopes = 'playlist-modify-public playlist-modify-private playlist-read-private'

        return spotipy.util.prompt_for_user_token(self.spotipy_username, scope=scopes, client_id=CLIENT_ID,
                                                  client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)

    def __request_spotipy_object(self, token):
        """
            Method for creating the Spotipy Object for making calls to Spotify

        :param token: The valid access token
        """
        if not token:
            raise InvalidInputException("You must request a valid authentication token first")
        self.sp = spotipy.Spotify(auth=token)

    def __retrieve_playlist(self):
        """
            Method for retrieving the playlist desired for sampling.
        """
        if not self.spotipy_username or not self.spotipy_playlist_id:
            raise InvalidInputException("You must set the spotipy information first.")

        if not self.sp:
            raise InvalidInputException("You must request a Spotipy object first.")
        self.spotify_playlist = self.sp.user_playlist(self.spotipy_username, self.spotipy_playlist_id)
        self.__add_recent_playlist(self.spotify_playlist)

    def __load_tracks(self):
        """
            Method for loading the tracks of a sampled playlist.
        """
        tracks = self.spotify_playlist["tracks"]

        self.__add_tracks(tracks)

        while tracks['next']:
            tracks = self.sp.next(tracks)
            self.__add_tracks(tracks)

        self.shuffle_playlist()
        self.notify_observers(load=True)

    def __add_tracks(self, track_list):
        """
            Method for adding the SpotifyTrack objects in a Spotify Playlist object to the master track list.

        :param track_list: Spotify Playlist Object
        """
        for track in track_list["items"]:
            if track['track']['preview_url']:
                self.master_track_list.append(SpotifyTrack(track))

    def __grab_tracks(self):
        """
            Initiates the SpotifyTrack Objects into the pipeline for download, conversion, and play.
        """
        for i in range(self.get_playlist_track_number()):
            track = self.master_track_list[0]
            self.master_track_list.remove(track)
            self.downloader.queue_download(track)

    def __append_to_playlist(self, user, playlist):
        """
            Method for appending favorites tracks to an existing Spotify Playlist.

        :param user: User ID of the existing playlist.
        :param playlist: Playlist ID of the existing playlist.
        """
        current_playlist = self.sp.user_playlist(user, playlist)["tracks"]
        current_playlist = self.__playlist_to_track_list(current_playlist)
        current_playlist = set(Model.__get_track_ids(current_playlist))

        track_ids = set(Model.__get_track_ids(self.favorites_list))
        track_ids = list(track_ids.difference(current_playlist))
        if track_ids:
            self.sp.user_playlist_add_tracks(user, playlist, track_ids)

    def __playlist_to_track_list(self, playlist):
        """
            Converts a SpotifyPlaylist object to a list of SpotifyTrack objects

        :param playlist: A Spotify Playlist object
        :return: A list of SpotifyTrack objects
        """
        track_list = []
        for track in playlist["items"]:
            track_list.append(SpotifyTrack(track))

        while playlist["next"]:
            playlist = self.sp.next(playlist)
            for track in playlist["items"]:
                track_list.append(SpotifyTrack(track))

        return track_list

    def __save_recent_playlists(self):
        """
            Dumps the recent playlist dictionary to a pickle file.
        """
        pickle.dump(self.recent_playlists, open(RECENT_PICKLE_FILE, 'wb'))

    def __add_recent_playlist(self, playlist):
        """
            Adds a Spotify Playlist object to the dictionary of recently sampled playlists.

        :param playlist:
        """
        key = str(playlist['owner']['id']) + "-" + str(playlist['id'])
        if key not in self.recent_playlists:
            self.recent_playlists[key] = {'id': playlist['id'], 'owner': playlist['owner']['id'],
                                          'name': playlist['name'], 'added': datetime.datetime.now()}
            if len(self.recent_playlists) > RECENT_LIMIT:
                self.__remove_oldest_recent_playlist()
        else:
            self.recent_playlists[key]['added'] = datetime.datetime.now()

        self.__save_recent_playlists()

    def __remove_oldest_recent_playlist(self):
        """
            Once the capacity of the recent playlist dictionary has been reached, removes the oldest entry.
        """
        min_key = None
        oldest_time = datetime.timedelta.min
        for key, playlist in self.recent_playlists.items():
            time = datetime.datetime.now() - playlist['added']
            if time > oldest_time:
                oldest_time = time
                min_key = key
        del self.recent_playlists[min_key]


    @staticmethod
    def __load_recent_playlists():
        """
            Loads the recently sampled playlist dictionary from pickle file.

        :return: Dictionary of recently sampled playlist.
        """
        if os.path.isfile(RECENT_PICKLE_FILE):
            return pickle.load(open(RECENT_PICKLE_FILE, 'rb'))
        return {}

    @staticmethod
    def __get_track_ids(track_list):
        """
            Converts a list of SpotifyTrack objects to a list of Track IDs

        :param track_list: A list of SpotifyTrack objects.
        :return: A list of Track IDs
        """
        result = []
        for track in track_list:
            result.append(track['track']['id'])
        return result


class InvalidInputException(Exception):
    """
        Exception for the type of error in the Spotify Playlist Sampler Application
    """
    def __init__(self, message):
        """
            Constructor for the InvalidInputException

        :param message: Description of the error produced.
        """
        super(InvalidInputException, self).__init__(message)


class SpotifyTrack(dict):
    """
        Subclass of the python Dictionary object.
        Spotify Track objects returned from Spotipy are just native dictionaries.
        By subclassing the wrapper class, I can override the __str__  method.
    """
    def __init__(self, *args, **kwargs):
        """
            Constructor for SpotifyTrack
        """
        super(SpotifyTrack, self).__init__(*args, **kwargs)

    def __str__(self):
        """
            Generates a String description based on the track name.
        :return: A String of the track's name.
        """
        if 'track' in self:
            try:
                return self.get('track').get('name')
            except UnicodeEncodeError:
                return self.get('track').get('name').encode('utf-8')

        return super(SpotifyTrack, self).__str__()





