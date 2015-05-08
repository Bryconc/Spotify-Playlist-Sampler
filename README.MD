## Spotify Playlist Sampler ##

**Background/Introduction**

With over 30 million songs in Spotify’s database and around 20,000 being added per day, it can certainly be overwhelming when seeking to discover music (Spotify Press Information, 2015). One of the biggest problems I’ve run into while creating a playlist on Spotify is diversifying my selection. When it comes to internet music streaming, Pandora certainly has an edge with its dynamic playlist generation. However, there’s a great resource available in Spotify that can’t be overlooked: other user’s playlists. Still, searching through these 400+ track playlists by hand is tiring and time consuming.

**Goal**

To solve the aforementioned problem, I proposed the idea of a “playlist sampling” application. The idea of the program would be to scale the typical large Spotify playlist (100+ tracks each around 4-6 minutes on average) to a more manageable and time-efficient sampled version, containing samples of around 30 seconds in length. Rather than having to manually traverse the playlist, we could programmatically navigate the playlist to get the general idea of what’s contained in it. Simultaneously, the program would keep track of which songs the user “favorited” and allow them to export these songs to a new or existing playlist. With this “sampling” process, the user could efficently build a diverse playlist without strenuous work or creativity.


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

**Video Demonstration of Program**

<iframe width="560" height="315" src="https://www.youtube.com/embed/t05h6aVU6Og" frameborder="0" allowfullscreen></iframe>