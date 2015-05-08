__author__ = 'Brycon'

import Tkinter as tk

DEFAULT_CSV_EXPORT_FILE = "export"


class PlaylistPrompt(tk.Toplevel):
    """
        Prompt for sampling a new Playlist. Contains a simple Entry
        for the playlist URL and clear options.
    """
    def __init__(self, parent, controller, *args, **kwargs):
        """
            Constructor for the PlaylistPrompt.
        :param parent:  Parent Container
        :param controller: reference to the Controller object to make requests of the Model.
        """
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.__init_prompt()
        self.parent = parent
        self.controller = controller

        self.parent.wm_attributes("-disabled", 1)
        self.wm_attributes("-topmost", 1)
        self.focus()
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.__close_handler)

    def __close_handler(self):
        """
            Responsible for handling the closing of the Toplevel element
        """
        self.parent.wm_attributes("-disabled", 0)
        self.destroy()

    def __init_prompt(self):
        """
            Initializes the content of the PlaylistPrompt
        """
        self.__init_prompt_label()
        self.__init_url_frame()
        self.__init_clear_frame()
        self.__init_submit_button()

    def __init_prompt_label(self):
        """
            Initializes the prompt label, explaining what to do.
        """
        self.prompt_label = tk.Label(self, text="Please enter the Spotify URL below: ")
        self.prompt_label.pack(pady=10)

    def __init_url_frame(self):
        """
            Initializes the URL entry frame. For the URL of the playlist to be sampled.
        """
        self.url_frame = tk.Frame(self)
        self.url_label = tk.Label(self.url_frame, text="Spotify Url:")
        self.url_entry = tk.Entry(self.url_frame, bd=5)
        self.url_label.pack(side=tk.LEFT)
        self.url_entry.pack(side=tk.RIGHT)
        self.url_frame.pack()

    def __init_clear_frame(self):
        """
            Initializes the clear options frame, containing options for clearing the playlist and favorites frame.
        """
        self.clear_frame = tk.Frame(self)

        self.clear_playlist = tk.IntVar()
        self.clear_favorites = tk.IntVar()
        self.clear_playlist.set(1)
        self.clear_favorites.set(1)
        self.clear_playlist_checkbox = tk.Checkbutton(self.clear_frame, text="Clear Playlist",
                                                      variable=self.clear_playlist)
        self.clear_favorites_checkbox = tk.Checkbutton(self.clear_frame, text="Clear Favorites",
                                                       variable=self.clear_favorites)

        self.clear_playlist_checkbox.pack(side=tk.LEFT)
        self.clear_favorites_checkbox.pack(side=tk.RIGHT)
        self.clear_frame.pack()

    def __init_submit_button(self):
        """
            Initializes the submit button for sampling a new playlist.
        """
        self.submit_button = tk.Button(self, text="Sample", command=self.__validate_new_playlist)
        self.submit_button.pack(pady=(0, 10))

    def __validate_new_playlist(self):
        """
            Validates that the URL entry contains a URL then parses the information out of it
            and tells the Model to start sampling the new playlist:
        """
        user_id, playlist_id = self.__process_url()
        if not user_id or not playlist_id:
            return
        clear_playlist = self.clear_playlist.get()
        clear_favorites = self.clear_favorites.get()
        self.controller.new_playlist(user_id, playlist_id, clear_playlist, clear_favorites)
        self.__close_handler()

    def __process_url(self):
        """
            Parses the information in the URL entry box. And returns the user id and playlist id
        :return: A set in the form (user_id, playlist_id) processed from the URL in the URL Entry Box
        """
        import re

        url = self.url_entry.get()
        if not url:
            return None, None

        regex = r'./user/(?P<user_id>[a-zA-z0-9]+)/playlist/(?P<playlist_id>[a-zA-z0-9]+)'
        regexp = re.compile(regex)
        result = regexp.search(url)
        return result.group('user_id'), result.group('playlist_id')


class ExportCSVPrompt(tk.Toplevel):
    """
        Prompt for exporting the favorited tracks to a CSV file.
    """
    def __init__(self, parent, controller, *args, **kwargs):
        """
            Constructor for the ExportCSVPrompt.
        :param parent:  Parent Container
        :param controller: reference to the Controller object to make requests of the Model.
        """
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.__init_prompt()
        self.parent = parent
        self.controller = controller

        self.parent.wm_attributes("-disabled", 1)
        self.wm_attributes("-topmost", 1)
        self.focus()
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.__close_handler)

    def __close_handler(self):
        """
            Responsible for handling the closing of the Toplevel element
        """
        self.parent.wm_attributes("-disabled", 0)
        self.destroy()

    def __init_prompt(self):
        """
            Initializes the content of the ExportCSVPrompt
        """
        self.__init_export_label()
        self.__init_export_entry()
        self.__init_export_options()
        self.__init_export_button()

    def __init_export_label(self):
        """
            Initializes the export label, explaining what to do.
        """
        self.export_frame = tk.Frame(self)
        self.export_label = tk.Label(self.export_frame, text="Enter the name for the output file below:",
                                     font="Verdana 10 bold")
        self.export_label.pack(pady=10, padx=10)
        self.export_frame.pack()

    def __init_export_entry(self):
        """
            Initializes the Entry element for the name of the CSV file
        """
        self.export_entry_frame = tk.Frame(self)
        self.export_entry = tk.Entry(self.export_entry_frame, bd=5)
        self.export_entry.insert(0, DEFAULT_CSV_EXPORT_FILE)
        self.export_entry.pack()
        self.export_entry_frame.pack()

    def __init_export_options(self):
        """
            Initializes the frame exporting CSV values.
        """
        self.export_options_frame = tk.Frame(self)

        self.export_options_label = tk.Label(self.export_options_frame, text="Export CSV file should include: ",
                                             font="Verdana 10 bold")

        self.export_name = tk.IntVar()
        self.export_name.set(1)
        self.export_album = tk.IntVar()
        self.export_album.set(0)
        self.export_artists = tk.IntVar()
        self.export_artists.set(0)
        self.export_preview_url = tk.IntVar()
        self.export_preview_url.set(0)

        self.export_name_check = tk.Checkbutton(self.export_options_frame, text="Track Name", variable=self.export_name)
        self.export_album_check = tk.Checkbutton(self.export_options_frame, text="Album", variable=self.export_album)
        self.export_artists_check = tk.Checkbutton(self.export_options_frame, text="Artists",
                                                   variable=self.export_artists)
        self.export_preview_url_check = tk.Checkbutton(self.export_options_frame, text="Preview Url",
                                                       variable=self.export_preview_url)

        self.export_options_label.grid(row=0, columnspan=2, pady=10)
        self.export_name_check.grid(row=1, column=0)
        self.export_album_check.grid(row=1, column=1)
        self.export_artists_check.grid(row=2, column=0)
        self.export_preview_url_check.grid(row=2, column=1)

        self.export_options_frame.pack()

    def __init_export_button(self):
        """
            Initializes the button to begin export to CSV
        """
        self.export_button_frame = tk.Frame(self)
        self.export_button = tk.Button(self.export_button_frame, text="Export", command=self.__validate_export)
        self.export_button.pack()
        self.export_button_frame.pack(pady=(0, 10))

    def __validate_export(self):
        """
            Validates that the export is possible, then initiates export.
            Export is possible if a filename is in the entry box and
            at least one option is selected.
        """
        if self.export_entry.get():
            if self.export_name.get() or self.export_artists.get() or self.export_album.get() or self.export_preview_url.get():
                self.__export()

    def __export(self):
        """
            Export method for CSV exporting.
            Gathers what information should be exported
            then makes a call to the Controller
        """
        information = []

        if self.export_name.get():
            information.append('name')

        if self.export_artists.get():
            information.append('artists')

        if self.export_album.get():
            information.append('album')

        if self.export_preview_url.get():
            information.append('preview_url')

        file_name = self.export_entry.get()

        self.controller.export_favorites('csv', file_name=file_name, information=information)
        self.__close_handler()


# class ExportExistingPlaylistPrompt(tk.Toplevel):
# import urllib
#
# from PIL import Image, ImageTk
# def __init__(self, parent, controller, *args, **kwargs):
#         tk.Toplevel.__init__(self, *args, **kwargs)
#         self.parent = parent
#         self.controller = controller
#         self.__init_prompt()
#
#         self.parent.wm_attributes("-disabled", 1)
#         self.wm_attributes("-topmost", 1)
#         self.focus()
#         self.transient(parent)
#         self.protocol("WM_DELETE_WINDOW", self.__close_handler)
#
#     def __close_handler(self):
#         self.parent.wm_attributes("-disabled", 0)
#         self.destroy()
#
#     def __init_prompt(self):
#         self.__init_export_label()
#         self.__init_export_entry()
#         self.__init_export_button()
#
#     def __init_export_label(self):
#         self.export_frame = tk.Frame(self)
#         self.export_label = tk.Label(self.export_frame, text="Existing playlists for:" + self.controller.get_current_username(),
#                                      font="Verdana 10 bold")
#         self.export_label.pack(pady=10, padx=10)
#         self.export_frame.pack()
#
#     def __init_export_entry(self):
#         self.export_entry_frame = tk.Frame(self)
#         playlists = self.controller.get_user_playlists()
#         from pprint import pprint
#
#         if playlists:
#             for playlist in playlists['items']:
#                 if playlist['owner']['id'] == self.controller.get_current_username():
#                     pprint(playlist)
#                     self.__add_playlist_frame(playlist)
#
#         self.export_entry_frame.pack()
#
#     def __add_playlist_frame(self, playlist):
#         playlist_frame = tk.Frame(self.export_entry_frame)
#         playlist_name_label = tk.Label(playlist_frame, text=playlist['name'])
#
#         artwork = ExportExistingPlaylistPrompt.image_from_url(playlist['images'][0]['url'])
#         playlist_artwork_image = tk.Label(playlist_frame, image=artwork)
#         playlist_artwork_image.image = artwork
#
#         playlist_name_label.pack()
#         playlist_artwork_image.pack()
#         playlist_frame.pack()
#
#     def __init_export_button(self):
#         self.export_button_frame = tk.Frame(self)
#         self.export_button = tk.Button(self.export_button_frame, text="Exit", command=self.__close_handler)
#         self.export_button.pack()
#         self.export_button_frame.pack(pady=(10, 10))
#
#     def __validate_export(self):
#         if self.export_entry.get():
#             self.__export()
#
#     def __export(self, user_id, playlist_id):
#         self.controller.export_favorites('existing', playlist=playlist_id, user=user_id)
#         self.__close_handler()
#
#     @staticmethod
#     def image_from_url(url):
#         image_file, headers = urllib.urlretrieve(url, 'util/Temp_Directory/temp_art3.jpg')
#         img = Image.open(image_file)
#         maxsize = (240, 240)
#         img.thumbnail(maxsize, Image.ANTIALIAS)
#         pic = ImageTk.PhotoImage(img)
#         return pic

class ExportExistingPlaylistPrompt(tk.Toplevel):
    """
        Prompt for exporting the favorited tracks to an Existing Playlist
    """

    def __init__(self, parent, controller, *args, **kwargs):
        """
            Constructor for the ExportExistingPlaylistPrompt
        :param parent:  Parent Container
        :param controller: reference to the Controller object to make requests of the Model.
        """
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.__init_prompt()
        self.parent = parent
        self.controller = controller

        self.parent.wm_attributes("-disabled", 1)
        self.wm_attributes("-topmost", 1)
        self.focus()
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.__close_handler)

    def __close_handler(self):
        """
            Responsible for handling the closing of the Toplevel element
        """
        self.parent.wm_attributes("-disabled", 0)
        self.destroy()

    def __init_prompt(self):
        """
            Initializes the content of the ExportExistingPlaylist Prompt
        """
        self.__init_export_label()
        self.__init_export_entry()
        self.__init_export_button()

    def __init_export_label(self):
        """
            Initializes the export label, explaining what to do.
        """
        self.export_frame = tk.Frame(self)
        self.export_label = tk.Label(self.export_frame, text="Enter the url of your playlist to extend:",
                                     font="Verdana 10 bold")
        self.export_label.pack(pady=10, padx=10)
        self.export_frame.pack()

    def __init_export_entry(self):
        """
            Initializes the entry frame for the URL of the existing playlist
        """
        self.export_entry_frame = tk.Frame(self)
        self.export_entry = tk.Entry(self.export_entry_frame, bd=5)
        self.export_entry.pack()
        self.export_entry_frame.pack()

    def __init_export_button(self):
        """
            Initializes the export button, which initializes the export when clicked.
        """
        self.export_button_frame = tk.Frame(self)
        self.export_button = tk.Button(self.export_button_frame, text="Export", command=self.__validate_export)
        self.export_button.pack()
        self.export_button_frame.pack(pady=(10, 10))

    def __validate_export(self):
        """
            Checks to make sure a URL is supplied for export. Then exports.
        """
        if self.export_entry.get():
            self.__export()

    def __parse_url(self):
        """
            Parses the information in the URL entry box. And returns the user id and playlist id
        :return: A set in the form (user_id, playlist_id) processed from the URL in the URL Entry Box.
        """
        import re

        url = self.export_entry.get()
        if not url:
            return None, None
        regex = r'./user/(?P<user_id>[a-zA-z0-9]+)/playlist/(?P<playlist_id>[a-zA-z0-9]+)'
        regexp = re.compile(regex)
        result = regexp.search(url)
        return result.group('user_id'), result.group('playlist_id')

    def __export(self):
        """
            Export method for existing playlist exporting
            Makes a call to the Controller applying specific information
        """
        user_id, playlist_id = self.__parse_url()
        self.controller.export_favorites('existing', playlist=playlist_id, user=user_id)
        self.__close_handler()


class ExportNewPlaylistPrompt(tk.Toplevel):
    """
        Prompt for exporting the favorited tracks to a new playlist
    """

    def __init__(self, parent, controller, *args, **kwargs):
        """
            Constructor for the ExportNewPlaylistPrompt
        :param parent:  Parent Container
        :param controller: reference to the Controller object to make requests of the Model.
        """
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.__init_prompt()
        self.parent = parent
        self.controller = controller

        self.parent.wm_attributes("-disabled", 1)
        self.wm_attributes("-topmost", 1)
        self.focus()
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.__close_handler)

    def __close_handler(self):
        """
            Responsible for handling the closing of the Toplevel element
        """
        self.parent.wm_attributes("-disabled", 0)
        self.destroy()

    def __init_prompt(self):
        """
            Initializes the content of the ExportNewPlaylistPrompt
        """
        self.__init_export_label()
        self.__init_export_entry()
        self.__init_export_button()

    def __init_export_label(self):
        """
            Initializes the export label, explaining what to do
        """
        self.export_frame = tk.Frame(self)
        self.export_label = tk.Label(self.export_frame, text="Enter the name of your new playlist:",
                                     font="Verdana 10 bold")
        self.export_label.pack(pady=10, padx=10)
        self.export_frame.pack()

    def __init_export_entry(self):
        """
            Initializes the Entry box for the name of the new playlist
        """
        self.export_entry_frame = tk.Frame(self)
        self.export_entry = tk.Entry(self.export_entry_frame, bd=5)
        self.export_entry.pack()
        self.export_entry_frame.pack()

    def __init_export_button(self):
        """
            Initializes the export button to initiate export
        """
        self.export_button_frame = tk.Frame(self)
        self.export_button = tk.Button(self.export_button_frame, text="Export", command=self.__validate_export)
        self.export_button.pack()
        self.export_button_frame.pack(pady=(10, 10))

    def __validate_export(self):
        """
            Checks to be sure the Export Entry has a name then exports.
        """
        if self.export_entry.get():
            self.__export()

    def __export(self):
        """
            Export method for new playlist exporting
            Makes a call to the Controller applying specific information
        """
        playlist_name = self.export_entry.get()
        self.controller.export_favorites('new', playlist=playlist_name)
        self.__close_handler()