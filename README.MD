## Spotify Playlist Sampler - Player GUI V2 (MVC) ##

The application has reached the final stage of development. I have redesigned the GUI with the help of the MVC. Now it should be more stable and expandable.

<img src="https://github.com/Bryconc/CS3535/blob/master/Research%20Module%206%20-%20Player%20GUI%20V2%20(MVC)/Model%20View%20Controller.gif?raw=true">

**Process**

The GUI works off the principles of the MVC. Other features include:

*	Exporting to an existing playlist
      *	Must be a playlist you created
*	Exporting to CSV file
      *	Values to be exported decided by checkboxes (e.g. Track name, artists, etc.)
*	Description page for all tracks in the playlist
      *	Includes links to all songs on Spotify
*	Default playlists for sampling.
      *	Example playlists. Used a lot for testing but still handy and expandable
*	Recent playlists for sampling
      *	Program maintains a local database of 5 most recent playlist requests.


**Dependencies**

At the moment this MUST be done on a Windows computer. Mac support will come later.

You also need a Spotify account as it will prompt you to log in to access public information.

To use spotify_playlist_sampler.py, you will need:

      - spotipy
      - echonest.remix

**Future Use**

In the future I would like to:

* Port to MAC. Audio player prevents use on MAC or Linux
* Move prompt for Spotify login from Python console to UI
* Provide list of possible playlists to export to rather than ask for link


<img src="https://github.com/Bryconc/CS3535/blob/master/Research%20Module%206%20-%20Player%20GUI%20V2%20(MVC)/Playlist%20Sampler%20Favorites.jpg?raw=true">
