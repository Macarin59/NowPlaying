import time
import spotipy
import os
import eyed3
import pandas as pd
from urllib.request import urlopen
from PIL import Image
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv, set_key
from pathlib import Path

# Conditional to create .env file and allows the user to set environment variables on first time setup
if not os.path.isfile(".env"):
    validation = 'N'

    # Creates ,env file
    env_file_path = Path(".env")
    env_file_path.touch(mode=0o600, exist_ok=False)

    while validation == 'N':  # Validation loop to allow the user to verify they input the correct information
        set_key(dotenv_path=env_file_path,  # Sets CLIENT_ID environment variable
                key_to_set='CLIENT_ID',
                value_to_set=input("Please enter Client ID:\n"))
        set_key(dotenv_path=env_file_path,  # Sets CLIENT_SECRET environment variable
                key_to_set='CLIENT_SECRET',
                value_to_set=input("Please enter Client Secret:\n"))
        set_key(dotenv_path=env_file_path,  # Sets REDIRECT_URI environment variable
                key_to_set='REDIRECT_URI',
                value_to_set=input("Please enter Redirect URI:\n"))
        set_key(dotenv_path=env_file_path,  # Sets SCOPE environment variable
                key_to_set='SCOPE',
                value_to_set=input("Please enter Scope:\n"))
        set_key(dotenv_path=env_file_path,  # Sets LOCAL_MUSIC_PATH environment variable
                key_to_set='LOCAL_MUSIC_PATH',
                value_to_set=input("Please enter Local Music Directory Path:\n"))

        load_dotenv()  # Loads .env
        # Print statement to allow the user to confirm if they put the correct information in
        print("You input:\nCLIENT_ID: {0}\nCLIENT_SECRET: {1}\nREDIRECT_URI: {2}\nSCOPE: {3}\nLOCAL_MUSIC_PATH: {4}\n".format(
            os.getenv('CLIENT_ID'),
            os.getenv('CLIENT_SECRET'),
            os.getenv('REDIRECT_URI'),
            os.getenv('SCOPE'),
            os.getenv('LOCAL_MUSIC_PATH')))
        validation = input("Are these correct? [Y or N]\n").upper()  # Allows user to end first time setup
    # Informs user where they can locate their environment variables if they need to be changed
    print("Information can be found at {0}\n".format(os.getcwd()+"\\.env"))

load_dotenv()  # Loads .env for sensitive information
isLocal = False  # Value to handle local files on spotify

LOCAL_MUSIC_PATH = os.getenv('LOCAL_MUSIC_PATH')  # Location of my Spotify Local Music
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv('CLIENT_ID'),  # Spotify API oauth call
                                               client_secret=os.getenv('CLIENT_SECRET'),
                                               redirect_uri=os.getenv('REDIRECT_URI'),
                                               scope=os.getenv('SCOPE')))


# Function to store album information in catalog using pandas Dataframes
# Optional overwrite param allows for refreshing catalog in the case of tag or filepath changes
# noinspection PyShadowingNames
def update_album_catalog(overwrite=False):
    if overwrite:
        df = pd.DataFrame({
            'Album': [],
            'Filepath': []
        })
    else:
        df = pd.read_csv("album_catalog.csv")
    # For every file in the Spotify Local Files directory
    for file in os.listdir(LOCAL_MUSIC_PATH):
        filepath = os.path.join(LOCAL_MUSIC_PATH, file)

        # If file is an .mp3 then the file will be loaded in eyed3
        if file.endswith('.mp3'):
            audiofile = eyed3.load(filepath)
            if audiofile.tag.album in df['Album'].to_numpy():
                continue
            df = pd.concat([df, pd.DataFrame({'Album': [audiofile.tag.album], 'Filepath': [filepath]})],
                           ignore_index=True)

    df.to_csv('album_catalog.csv', index=False)
    print("Successfully updated catalog")


# Function to locate song art from local files
# Searches for album through album_catalog.csv and saves the artwork from the .mp3 metadata
# Returns the image name as a string
def locate_song_art(album):
    catalog = pd.read_csv("album_catalog.csv")

    # Conditional to check is the album is in the catalog
    if album in catalog['Album'].to_numpy():
        artwork = catalog.loc[catalog['Album'] == album, 'Filepath'].iloc[0]  # Returns the filepath of the album art
    else:  # Raises Exception if the album is not found
        raise Exception("Album not found in local files")

    file = eyed3.load(artwork)
    # Obtains image from .mp3 metadata and stores it as local_image.jpg
    for image in file.tag.images:
        image_file = open("local_image.jpg", "wb")
        image_file.write(image.image_data)
        image_file.close()
    return "local_image.jpg"


# Function to get currently playing track from the Spotify API
# Returns a dictionary of various different track information
def get_current_track():
    global isLocal  # Global scope to allow for proper image handling
    results = sp.current_user_playing_track()  # Gets information from the Spotify API
    if not results:
        raise Exception("No track is currently playing")

    track_id = results['item']['id']  # Spotify Track ID
    track_name = results['item']['name']  # Spotify Track Name
    album = results['item']['album']['name']  # Spotify Album Name

    # Obtains the artist information from Spotify API and formats information to be usable
    artists = results['item']['artists']
    artist_names = ", ".join(  # Spotify Artist Names
        [artists[index]['name'] for index in range(len(artists))]
    )

    # If the track is a local file sets values to empty string
    if not results['item']['album']['images']:
        artwork = ""
        link = ""
        isLocal = True
    # Else sets the artwork and link information to the information provided from the Spotify API
    else:
        artwork = results['item']['album']['images'][0]['url']  # Spotify Artwork URL
        link = results['item']['external_urls']['spotify']  # Spotify Link to track
        isLocal = False

    current_track_info = {  # Track Info Dict
        "id": track_id,
        "name": track_name,
        "artists": artist_names,
        "album": album,
        "link": link,
        "artwork": artwork
    }
    return current_track_info


if __name__ == '__main__':
    last_track = ""  # Previous track name
    last_album = ""  # Previous track album

    response = input(
        "Would you like to update catalog? \n[Y for Yes]   [N for No]   [A for Yes with Overwrite]\n").upper()
    if response == 'Y':
        update_album_catalog()
    elif response == 'A':
        update_album_catalog(True)
    response = 'Y'

    while response == 'Y':  # Main Application Loop
        try:
            track = get_current_track()  # Gets current track info from Spotify API

            # Conditional updates track information if the track has been changed
            if not track['name'] == last_track:
                last_track = track  # Stores the track name

                # Conditional that checks if the album changed to conserve resources
                if not track['album'] == last_album:
                    last_album = track['album']  # Stores the album name
                    # Cleans up previous image
                    if os.path.isfile("album_art.jpg"):
                        os.remove("album_art.jpg")
                    # Conditional to locate image depending on if it is local or from Spotify API
                    if isLocal:
                        img = Image.open(locate_song_art(track['album']))  # Opens local image
                        if img.mode != 'RGB':  # Conditional for the occasions when jpg mode is not correct
                            img = img.convert('RGB')
                    else:
                        img = Image.open(urlopen(track['artwork']))  # Opens web image from Spotify API
                    img = img.resize((500, 500))  # Resizes the image to 500x500
                    img.save('album_art.jpg', 'JPEG')  # Saves the image

                # Write song title to song_title.txt
                f = open("song_title.txt", "w", encoding='utf-8')
                f.write("{0}    ".format(track['name']))
                f.close()

                # Write artists to song_artists.txt
                f = open("song_artist.txt", "w", encoding='utf-8')
                f.write("{0}    ".format(track['artists']))
                f.close()

                # Let C# know file writing is done
                f = open("sync.txt", "w", encoding='utf-8')
                f.write("Updated")
                f.close()

            time.sleep(0.5)  # Half-second delay to save on resources
        except Exception as e:  # Exception handling for when nothing is playing
            print(repr(e))
            response = input("Try again? [Y or N]\n").upper()
