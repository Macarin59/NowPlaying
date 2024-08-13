# NowPlaying

## What is this?

NowPlaying is a Python script that outputs a user's currently playing track information for usage on an external program like OBS. Many programs do this but significantly better than my implementation, but my program solves a particular issue I was facing with all of them. 

Spotify offers the ability to use your **local files** in playlists and when local file information is accessed by API calls it cannot display the album artwork as this artwork is not stored on Spotify's servers. 

This program solves that by scraping your local song directory and pulls the artwork directly from the mp3 file. 

![2024-08-13 02_14_13-song_artist txt - Notepad](https://github.com/user-attachments/assets/23942904-2a74-4af7-94d4-b1e99ec39840)

## How do I use it?

The script will need some information from you to run properly, specifically you will need a client id, secret, redirect uri, and scope from the Spotify Developer page as well as the path of your local music. 

The Spotify information can be gathered here by creating an app here: https://developer.spotify.com/dashboard/create 

You can **name** it and give it any **description** you would like. 

For the **Redirect URI** it is recommended to use this link both in the script and on the app page: http://localhost:5000/callback

Lastly, make sure to check the **Web API** box

For the **SCOPE** of the program you should use *(unless you plan on editing the script)*: **user-read-currently-playing**

The script stores your local music information in a .csv for faster lookup and will ask if you would like to update the catalog, if it is your first time running the script make sure to update it.

Finally, the script will output your song information into three files:

**song_title.txt** - The name of the song

**song_artist.txt** - The name of the song artist

**album_art.jpg** - The artwork of the track

## What did you use to make this?

I used Python 3.12.3 and PyCharm 2023.3.3 to create the script. The individual dependencies I used can be found in the requirements.txt file. 

## Plans for the future 

I am happy with the current version of the script so barring any nasty bugs I have no future plans for the script implementation.

I have developed a prototype version of a GUI implementation written in C#.NET+Python but currently do not have the time (or knowledge) to polish it into a release version. Here are some example screenshots of what a GUI implementation might look like:

![2024-08-13 02_00_36-MainWindow](https://github.com/user-attachments/assets/75cc3a47-577f-4601-87e1-05ebd05c6417)

![2024-08-13 02_02_09-New Tab - Brave](https://github.com/user-attachments/assets/64c86aa2-6f71-4bf0-be52-e816df230875)

The reason for choosing C#.NET is because programs like OBS can capture window transparency which allows for custom song overlays as seen here:
![2024-08-13 02_02_55-OBS 30 1 2 - Profile_ Main - Scenes_ Main](https://github.com/user-attachments/assets/fcd2f6f5-24fd-4e90-83cb-5f2a3755cce3)
