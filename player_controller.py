__author__ = 'Brycon'

import player_view


class Controller(object):
    """
        Controller Object in MVC pattern. Mediates between model and view.
    """
    def __init__(self, model):
        """
            Constructor for Controller
        :param model: Reference to the Model component of the MVC
        """
        self.model = model
        self.view = player_view.View(self, model)

    def show(self):
        """
            Displays the View component of the MVC
        """
        self.view.show()

    def start(self):
        """
            Starts the application. Equivalent of 'play'
        """
        self.model.on()
        self.view.enable_pause_button()
        self.view.disable_play_button()

    def stop(self):
        """
            Stops the application. Equivalent of 'pause'
        """
        self.model.off()
        self.view.disable_pause_button()
        self.view.enable_play_button()

    def new_playlist(self, user_id, playlist_id, clear_playlist=True, clear_favorites=False):
        """
            Initiates a new playlist sampling with provided information.
        :param user_id: Spotify user id for playlist
        :param playlist_id: Spotify playlist id for playlist
        :param clear_playlist: Should the playlist box be cleared? True for yes, otherwise False
        :param clear_favorites: Should the favorites box be cleared? True for yes, otherwise False
        """
        if clear_playlist:
            self.view.clear_playlist_box()
        if clear_favorites:
            self.view.clear_favorites_box()
        self.view.clear_detail_box()
        self.model.new_playlist(user_id, playlist_id)
        self.start()

    def unload_player(self, wait=True):
        """
            Initiates an unload of the player. Removes all resources used for last playlist sampling
        :param wait: Should the player wait for the current track to finish? True for yes, False for no.
        """
        self.model.unload_player(wait)

    def get_playlist_list(self):
        """
            Returns the list of tracks that have already been sampled.
        :return: a list of Spotify track objects that have already been sampled.
        """
        return self.model.get_playlist_list()

    def get_favorites_list(self):
        """
            Returns the current list of favorited tracks
        :return: a list of Spotify track objects that have been favorited
        """
        return self.model.get_favorites_list()

    def get_master_track_list(self):
        """
            Returns the master track list containing all tracks for the current sampling playlist
        :return: the master track list of Spotify track objects containing all tracks for the current sampling playlist
        """
        return self.model.get_master_track_list()

    def get_current_track(self):
        """
            Gets the current playing track of the Model
        :return: the Spotify track object for the current playing track of the Model
        """
        return self.model.get_current_track()

    def get_current_track_number(self):
        """
            Gets the track number of the current track out of all playlist tracks.
        """
        return self.model.get_current_track_number()

    def get_playlist_amount(self):
        """
            Gets the amount of tracks in the current sampling playlist
        """
        return self.model.get_playlist_amount()

    def export_favorites(self, export_type, **kwargs):
        """
            Exports the current favorite list depending on export type.
        :param export_type: The type of the export to be performed. Handled by the Model.
        :param kwargs: Keyword arguments needed for the export type.
        """
        self.model.export_favorites(export_type, **kwargs)

    def get_recent_playlists(self):
        """
            Gets the most recent playlist dictionary loaded by the Model. Used
            to load the Playlist->Recent menu
        :return:
        """
        return self.model.get_recent_playlists()

    def get_user_playlists(self):
        """
            Returns the Spotify playlists owned by the current user.
            Used in a future implementation of Export Existing.
            Incomplete version can be seen in prompts.py
        """
        return self.model.get_user_playlists()

    def get_current_username(self):
        """
            Returns the current, authenticated user for Spotify
            Used in a future implementation of Export Existing.
            Incomplete version can be seen in prompts.py
        """
        return self.model.get_current_username()

