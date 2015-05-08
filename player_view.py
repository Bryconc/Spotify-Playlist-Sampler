__author__ = 'Brycon'

import os
import Tkinter as tk
import tkMessageBox
import ttk
import urllib
import webbrowser
from functools import partial

from PIL import Image, ImageTk

import prompts
from util.observer import Observer
from util.SynchronizedListbox import SynchronizedListbox


FRAME_WIDTH = 50
FRAME_HEIGHT = 20
BACKGROUND_COLOR = "#383b38"
TEXT_COLOR = "#FFF"

WINDOW_WIDTH = 670
WINDOW_HEIGHT = 540

DEFAULT_PLAYLISTS = {
    'Movie': ['1139683356', '6sNDAFPubg3k4CuyH1fqrR'],
    'Disney': ['bryconc', '4yumoVCxw7K4roD5POtqCP'],
    'Video Game': ['george_spv', '6nhiBJot8yHf2BHoRrBUmJ']
}


class View(Observer):
    """
        View Object in MVC pattern. Acts on behalf of the User to interface with the Model via the Controller.
    """
    def __init__(self, controller, title="Spotify Playlist Sampler"):
        """
            Constructor for the View object
        :param controller: A reference to the Controller component of the MVC
        :param title: The title for the GUI. Defaults to "Spotify Playlist Sampler"
        """
        super(View, self).__init__()
        self.controller = controller

        self.root = tk.Tk()
        self.root.title(title)
        self.root.maxsize(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.root.minsize(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.root.resizable(height=False, width=False)
        self.root.config(bg=BACKGROUND_COLOR)
        self.root.protocol("WM_DELETE_WINDOW", self.__close_handler)
        self.root.iconbitmap(r'util/Temp_Directory/Spotify.ico')

        self.setup()

    def setup(self):
        """
            Sets up the GUI graphically.
        """
        self.__init_frames()

    def disable_play_button(self):
        """
            Disables the play button so it cannot be clicked.
        """
        self.player_tab.disable_play_button()

    def enable_play_button(self):
        """
            Enables the play button so it can be clicked.
        """
        self.player_tab.enable_play_button()

    def disable_pause_button(self):
        """
            Disables the pause button so it cannot be clicked.
        """
        self.player_tab.disable_pause_button()

    def enable_pause_button(self):
        """
            Enables the pause button so it can be clicked.
        """
        self.player_tab.enable_pause_button()

    def clear_playlist_box(self):
        """
            Clears the Played Songs box of the GUI.
        """
        self.player_tab.clear_playlist_box()

    def clear_favorites_box(self):
        """
            Clears the Favorited Songs box of the GUI.
        """
        self.player_tab.clear_favorites_box()

    def clear_detail_box(self):
        """
            Clears the playlist details box of the GUI.
        """
        self.detail_tab.clear_detail_box()

    def update(self, *args, **kwargs):
        """
            Update method of the Observer pattern. Action will be taken based on the named parameters.

            If track is specified, we have encountered a new track.
            If load is specified we are loading a new playlist.
            If count is specified we are updating the track counter.
        """
        if 'track' in kwargs:
            self.player_tab.new_track()

        if 'load' in kwargs:
            self.detail_tab.load_playlist()
            self.__update_recent_playlists()

        if 'count' in kwargs:
            self.player_tab.update_track_count(kwargs['count'])

    def show(self):
        """
            Displays the view. Enters the mainloop of the Tkinter object. Will not return from this call until the GUI
            exits.
        """
        self.root.mainloop()

    ###################################
    # #
    #  BEGIN PRIVATE UTILITY METHODS  #
    #                                 #
    ###################################

    def __init_frames(self):
        """
            Initializes the frames for the GUI.
        """
        self.__init_menu()
        self.__init_notebook()

    def __close_handler(self):
        """
            Close handler for closing the application.
        """
        if tkMessageBox.askokcancel("Quit?", "Are you sure you want to quit?"):
            self.controller.unload_player(wait=False)
            self.root.quit()
            os._exit(-1)

    def __init_menu(self):
        """
            Initializes the components of the MenuBar of the application.
        """
        self.menu_bar = tk.Menu(self.root)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.__close_handler)

        self.export_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.export_menu.add_command(label="Export to CSV file.", command=self.__prompt_for_export_csv)
        self.export_menu.add_separator()
        self.export_menu.add_command(label="Export to existing playlist",
                                     command=self.__prompt_for_export_existing_playlist)
        self.export_menu.add_command(label="Export to new playlist", command=self.__prompt_for_export_new_playlist)

        self.playlist_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.playlist_menu.add_command(label="Sample new playlist", command=self.__prompt_for_playlist_input)
        self.playlist_menu.add_separator()

        self.default_playlists_menu = tk.Menu(self.menu_bar, tearoff=0)

        for name, keys in DEFAULT_PLAYLISTS.iteritems():
            self.default_playlists_menu.add_command(label=name,
                                                    command=partial(self.controller.new_playlist, keys[0], keys[1]))

        self.playlist_menu.add_cascade(label="Defaults", menu=self.default_playlists_menu)

        self.recent_playlists_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.__update_recent_playlists()
        self.playlist_menu.add_cascade(label="Recents", menu=self.recent_playlists_menu)

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Playlist", menu=self.playlist_menu)
        self.menu_bar.add_cascade(label="Export", menu=self.export_menu)
        self.root.config(menu=self.menu_bar)

    def __init_notebook(self):
        """
            Initializes the Notebook component of the application.
        """
        self.notebook = ttk.Notebook(self.root)

        self.player_tab = PlayerFrame(self.controller, self.notebook, bg=BACKGROUND_COLOR, highlightbackground="#000")
        self.detail_tab = DetailFrame(self.controller, self.notebook)

        self.notebook.add(self.player_tab, text="Player")
        self.notebook.add(self.detail_tab, text="Detail")
        ttk.Style().configure("TNotebook", background=BACKGROUND_COLOR)
        ttk.Style().map("TNotebook.Tab", background=[("selected", BACKGROUND_COLOR)],
                        foreground=[("selected", BACKGROUND_COLOR)])
        ttk.Style().configure("TNotebook.Tab", background=BACKGROUND_COLOR, foreground=BACKGROUND_COLOR)

        self.notebook.pack()

    def __prompt_for_playlist_input(self):
        """
            Creates the prompt for sampling a new playlist. Action will be directed from the new prompt.
        """
        prompts.PlaylistPrompt(self.root, self.controller)

    def __prompt_for_export_csv(self):
        """
            Creates the prompt for exporting the favorited tracks to a CSV file. Action will be directed from the new
            prompt.
        """
        prompts.ExportCSVPrompt(self.root, self.controller)

    def __prompt_for_export_existing_playlist(self):
        """
            Creates the prompt for exporting the favorited tracks to an existing Spotify Playlist. Action will be
            directed from the new prompt.
        """
        prompts.ExportExistingPlaylistPrompt(self.root, self.controller)

    def __prompt_for_export_new_playlist(self):
        """
            Creates the prompt for exporting the favorited tracks to a new Spotify Playlist. Action will be directed
            from the new prompt.
        """
        prompts.ExportNewPlaylistPrompt(self.root, self.controller)

    def __update_recent_playlists(self):
        """
            Handles creating the submenu for recently sampled playlists.
        """
        recent_playlists = self.controller.get_recent_playlists()
        sorted_keys = sorted(recent_playlists, key=lambda k: recent_playlists[k]['added'], reverse=True)
        self.recent_playlists_menu.delete(0, tk.END)

        for key in sorted_keys:
            playlist = recent_playlists[key]
            self.recent_playlists_menu.add_command(label=playlist['name'],
                                                   command=partial(self.controller.new_playlist, playlist['owner'],
                                                                   playlist['id']))


class PlayerFrame(tk.Frame):
    """
        Frame for holding components related to playing and favoriting the current Playlist.
        "Player" tab of the Notebook.
    """
    def __init__(self, controller, master, **kwargs):
        """
            Constructor for the PlayerFrame object.

        :param controller: A reference to the Controller object of the MVC.
        :param master: A reference to the parent component that will contain the PlayerFrame
        """
        tk.Frame.__init__(self, master, **kwargs)
        self.controller = controller
        self.__init_playlist_frame()
        self.__init_mid_playlist_buttons()
        self.__init_favorite_frame()
        self.__init_album_frame()
        self.__init_player_frame()

    def __init_playlist_frame(self):
        """
            Initializes the frame that holds the "Played Songs" ListBox.
        """
        self.playlist_frame = tk.Frame(self, width=FRAME_WIDTH, height=FRAME_HEIGHT, bg=BACKGROUND_COLOR)

        playlist_label = tk.Label(self.playlist_frame, text="Played Songs:", fg=TEXT_COLOR, bg=BACKGROUND_COLOR, pady=5)
        playlist_label.pack()

        self.playlist_list = SynchronizedListbox(self.playlist_frame, self.controller.get_playlist_list(), width=40,
                                                 height=13, highlightbackground=BACKGROUND_COLOR)
        self.playlist_list.pack()

        self.playlist_frame.grid(row=1, column=0, padx=20)

    def __init_mid_playlist_buttons(self):
        """
            Initializes the frame that holds the buttons to move tracks to and from the Favorited Songs ListBox.
        """
        self.button_frame = tk.Frame(self, width=10, height=20, bg=BACKGROUND_COLOR)

        to_playlist_btn = tk.Button(self.button_frame, text="<<", width=4, command=self.moveto_playlist,
                                    bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        to_favorite_btn = tk.Button(self.button_frame, text=">>", width=4, command=self.moveto_favorites,
                                    bg=BACKGROUND_COLOR, fg=TEXT_COLOR)

        to_playlist_btn.pack(pady=10)
        to_favorite_btn.pack()

        self.button_frame.grid(row=1, column=1)

    def __init_favorite_frame(self):
        """
            Initializes the frame that holds the "Favorited Songs" ListBox.
        """
        self.favorite_frame = tk.Frame(self, width=FRAME_WIDTH, height=FRAME_HEIGHT, bg=BACKGROUND_COLOR)

        favorite_label = tk.Label(self.favorite_frame, text="Favorite Songs:", fg=TEXT_COLOR, bg=BACKGROUND_COLOR,
                                  pady=5)
        favorite_label.pack()

        self.favorite_list = SynchronizedListbox(self.favorite_frame, self.controller.get_favorites_list(), width=40,
                                                 height=13, highlightbackground=BACKGROUND_COLOR)
        self.favorite_list.pack()
        self.favorite_frame.grid(row=1, column=2, padx=20)

    def __init_player_frame(self):
        """
            Initializes the frame that holds the information about the current song being played and Play and Pause
            buttons.
        """
        BACKGROUND_COLOR = "black"
        self.player_frame = tk.Frame(self, width=FRAME_WIDTH, height=FRAME_HEIGHT, bg=BACKGROUND_COLOR)
        self.track_number_label = tk.Label(self.player_frame, text="Track 0 of 0", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        self.track_number_label.pack()
        self.track_name_label = tk.Label(self.player_frame, text="No song name", width=40, bg=BACKGROUND_COLOR,
                                         fg=TEXT_COLOR)
        self.track_name_label.pack()
        self.timer_label = tk.Label(self.player_frame, text="0/30", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        self.timer_label.pack()

        btn_frame = tk.Frame(self.player_frame, bg=BACKGROUND_COLOR)
        self.play_button = tk.Button(btn_frame, text="PLAY", bg="red", fg=TEXT_COLOR, command=self.controller.start)
        self.pause_button = tk.Button(btn_frame, text="PAUSE", bg="green", fg=TEXT_COLOR, command=self.controller.stop)
        self.play_button.pack(side=tk.LEFT, padx=5)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        btn_frame.pack(pady=10)

        self.player_frame.grid(row=2, column=0, padx=20)

    def __init_album_frame(self):
        """
            Initializes the frame that holds the artwork of the current track.
        """
        self.album_frame = tk.Frame(self, width=FRAME_WIDTH, height=FRAME_HEIGHT, bg=BACKGROUND_COLOR)
        self.album_image = tk.Label(self.album_frame, bg=BACKGROUND_COLOR)
        self.album_image.pack()
        self.album_frame.grid(row=2, column=2, pady=10)

    def __update_album_art(self):
        """
            Handles updating the artwork of the album frame to the current track.
        """
        current_track = self.controller.get_current_track()
        if current_track:
            image_file, headers = urllib.urlretrieve(current_track['track']['album']['images'][0]['url'],
                                                     'util/Temp_Directory/temp_art.jpg')
            img = Image.open(image_file)
            maxsize = (240, 240)
            img.thumbnail(maxsize, Image.ANTIALIAS)
            pic = ImageTk.PhotoImage(img)
            self.album_image.config(image=pic)
            self.album_image.image = pic

    def __update_track_name(self):
        """
            Handles updating the name of the current track.
        """
        self.track_name_label.config(text=self.controller.get_current_track()['track']['name'])

    def __update_track_number(self):
        """
            Handles the updating of the track number of the current track.
        """
        self.track_number_label.config(text="Track {0} of {1}".format(
            self.controller.get_current_track_number(), self.controller.get_playlist_amount()))

    def __add_to_list(self):
        """
            Inserts a new track into the "Played Songs" Listbox.
        """
        self.playlist_list.insert(0, self.controller.get_current_track())

    def moveto_favorites(self):
        """
            Handles moving songs from the "Played Songs" Listbox to the "Favorites Songs" Listbox
        """
        tracks = self.playlist_list.curselection()
        tracks = tracks[::-1]

        for track in tracks:
            t = self.playlist_list.get(track)
            self.favorite_list.insert(0, t)
            self.playlist_list.delete(track)

    def moveto_playlist(self):
        """
            Handles moving songs from the "Favorites Songs" Listbox to the "Played Songs" Listbox
        """
        tracks = self.favorite_list.curselection()
        tracks = tracks[::-1]

        for track in tracks:
            t = self.favorite_list.get(track)
            self.playlist_list.insert(0, t)
            self.favorite_list.delete(track)

    def disable_play_button(self):
        """
            Sets the Play button to disabled. It can no longer be clicked.
        """
        self.play_button.config(state='disabled', bg='red')

    def enable_play_button(self):
        """
            Sets the Play button to normal. It can be clicked again.
        """
        self.play_button.config(state='normal', bg='green')

    def disable_pause_button(self):
        """
            Sets the Pause button to disabled. It can no longer be clicked.
        """
        self.pause_button.config(state='disabled', bg='red')

    def enable_pause_button(self):
        """
            Sets the Pause button to normal. It can be clicked again.
        """
        self.pause_button.config(state='normal', bg='green')

    def clear_playlist_box(self):
        """
            Clears the "Played Songs" Listbox
        """
        self.playlist_list.delete(0, self.playlist_list.length())

    def clear_favorites_box(self):
        """
            Clears the "Favorited Songs" Listbox
        """
        self.favorite_list.delete(0, self.favorite_list.length())

    def update_track_count(self, count):
        """
            Updates the current track counter to the specified count.
        :param count: Count that the counter will reflect
        """
        self.timer_label.config(text='{0}/30'.format(str(count)))

    def new_track(self):
        """
            Handles the appearance of a new track.
        """
        self.__update_track_number()
        self.__update_track_name()
        self.__update_album_art()
        self.__add_to_list()


class DetailFrame(tk.Frame):
    """
        Frame for holding components related to the details of the current sampling playlist
        "Detail" tab of the Notebook.
    """
    def __init__(self, controller, master, **kwargs):
        """
            Constructor for the PlayerFrame object.

        :param controller: A reference to the Controller object of the MVC.
        :param master: A reference to the parent component that will contain the PlayerFrame
        """
        tk.Frame.__init__(self, master, **kwargs)
        self.controller = controller
        self.__init_track_list_frame()
        self.__init_detail_album_art()
        self.__init_detail_information()

    def __init_track_list_frame(self):
        """
            Initializes the Listbox that holds the details about every track of the playlist.
        """
        self.track_list_frame = tk.Frame(self, width=FRAME_WIDTH, height=FRAME_HEIGHT, bg=BACKGROUND_COLOR)
        scrollbar = tk.Scrollbar(self.track_list_frame)
        self.track_list = SynchronizedListbox(self.track_list_frame, [], width=80, height=13,
                                              highlightbackground=BACKGROUND_COLOR, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.track_list.yview)

        self.track_list.bind('<<ListboxSelect>>', self.__update_detail)

        scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.track_list.pack(side=tk.LEFT)
        self.track_list_frame.grid(row=0, columnspan=2, padx=(80, 0), pady=(20, 0))

    def __init_detail_album_art(self):
        """
            Initializes the album artwork frame to show on detail of each track.
        """
        self.detail_album_frame = tk.Frame(self, width=FRAME_HEIGHT, height=FRAME_HEIGHT)
        self.detail_album_image = tk.Label(self.detail_album_frame)

        self.detail_album_image.pack()
        self.detail_album_frame.grid(row=1, column=0, pady=(10, 0))

    def __init_detail_information(self):
        """
            Initializes the detail information box that will hold the information about every track.
        """
        self.detail_info_frame = tk.Frame(self, width=FRAME_WIDTH, height=FRAME_HEIGHT)
        self.detail_text = tk.Message(self.detail_info_frame, font="Helvetica 12 bold", width=FRAME_WIDTH * 5)
        self.detail_album_link = tk.Label(self.detail_info_frame, font="Helvetica 12 bold underline",
                                          text="Link to Album", fg="blue", cursor="hand2")
        self.album_url = None
        self.detail_album_link.bind("<Button-1>", self.__open_album_url)

        self.detail_text.pack()
        self.detail_album_link.pack()
        self.detail_info_frame.grid(row=1, column=1)

    def load_playlist(self):
        """
            Loads the details of the current playlist into the DetailFrame
        """
        master_list = self.controller.get_master_track_list()[:]
        master_list.sort(key=lambda track_i: track_i['track']['name'], reverse=True)
        for track in master_list:
            try:
                self.track_list.insert(0, track)
            except UnicodeEncodeError:
                track['track']['name'] = track['track']['name'].encode('utf-8')
                self.track_list.insert(0, track)

    def __update_detail(self, event):
        """
            Click handler for updating the DetailFrame about the clicked track in the Listbox.
        :param event: Click event that triggered the update.
        """
        track = self.track_list.get(self.track_list.curselection()[0])
        self.album_url = track['track']['album']['external_urls']['spotify']
        self.__update_detail_album(track)
        self.__update_detail_text(track)

    def __update_detail_album(self, track):
        """
            Updates the detail frame with the artwork of the specified track.
        :param track: The track whose artwork is being fetched.
        """
        image_file, headers = urllib.urlretrieve(track['track']['album']['images'][0]['url'],
                                                 'util/Temp_Directory/temp_art2.jpg')
        img = Image.open(image_file)
        maxsize = (240, 240)
        img.thumbnail(maxsize, Image.ANTIALIAS)
        pic = ImageTk.PhotoImage(img)
        self.detail_album_image.config(image=pic)
        self.detail_album_image.image = pic

    def __update_detail_text(self, track):
        """
            Updates the detail frame with the text about the specified track.
        :param track: The track whose information is being fetched.
        """
        text = "Name: %s\n\nAlbum: %s\n\nArtists: " % (
        track['track']['name'].decode('utf-8'), track['track']['album']['name']) + self.__get_artist_text(track)
        self.detail_text.config(text=text)

    def __get_artist_text(self, track):
        """
            Produces the String of artists for a specified track
        :param track: The track whose artist is being fetched.
        :return: Returns the String listing the artists for a given track.
        """

        artists = [x['name'] for x in track['track']['artists']]
        return ", ".join(artists)

    def __open_album_url(self, event):
        """
            Click handler for opening the link to the tracks album on Spotify.
        :param event: Click event for clicking on the hyperlink.
        """
        if self.album_url:
            webbrowser.open_new(self.album_url)

    def clear_detail_box(self):
        """
            Clears the detailed information box about the current playlist.
        """
        self.track_list.delete(0, self.track_list.length())





