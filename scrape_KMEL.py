import pandas as pd
import numpy as np
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import time
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
#Function Definitions
def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


url = 'https://kmel.iheart.com/music/recently-played/'

#Start with trying to get song name, artist name, time played
#This function will do this
def get_recent(url):
    response = get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    #Get Time Played
    times = soup.select("time")
    i = 0
    lst_init = []
    for t in times:
        if "datetime" in str(t):
            lst_init.append(str(t))
    times = []
    gap = len("datetime=") + 1
    for t in lst_init:
        if "song-time" in t:
            first = t.find("datetime=")
            last = t.find("-07:00")
            time = t[first+ gap : last]
            times.append(time)
    #Get Song Name
    potential = soup.findAll("a")
    names_init = []
    for p in potential:
        if "song-title" in str(p):
            names_init.append(str(p))
    names = []
    gap = len("_blank>") + 1
    for p in names_init:
        start = p.find('_blank">')
        end = p.find("</a>")
        name = p[start + gap: end]
        names.append(name)
    #Get Artist Name
    potential = soup.findAll("a")
    artists_init = []
    for p in potential:
        if "artist-name" in str(p):
            artists_init.append(str(p))
    artists = []
    for p in artists_init:
        start = p.find('_blank">')
        end = p.find("</a>")
        artist = p[start + gap: end]
        artists.append(artist)
    return times, names, artists

timesMaster = np.array([])
artistsMaster = np.array([])
songsMaster = np.array([])

#count = 0
#Try just keep running this and updating the csv
while True:
    times, artists, songs = get_recent(url)
    newTimes = []
    newArtists = []
    newSongs = []
    for i in range(len(times)):
        if times[i] not in timesMaster:
            newTimes.append(times[i])
            newArtists.append(artists[i])
            newSongs.append(songs[i])
    newTimes = np.array(newTimes)
    newArtists = np.array(newArtists)
    newSongs = np.array(newSongs)
    timesMaster = np.append(newTimes, timesMaster)
    artistsMaster = np.append(newArtists, artistsMaster)
    songsMaster = np.append(newSongs, songsMaster)
    total = pd.DataFrame({'Time': timesMaster, 'Artist': artistsMaster, 'Song': songsMaster})
    total.to_csv("KMEL_scraped.csv")
    time.sleep(60)
