import pandas as pd
import numpy as np
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import time
import warnings
import os
import html
from os import path
warnings.simplefilter(action='ignore', category=FutureWarning)

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

if path.exists("KMEL_scraped.csv"):
    total = pd.read_csv("KMEL_scraped.csv")
    timesMaster = np.array(total.Time)
    artistsMaster = np.array(total.Artist)
    songsMaster = np.array(total.Song)
else:
    timesMaster = np.array([])
    artistsMaster = np.array([])
    songsMaster = np.array([])

if path.exists("KMEL_unique.csv"):
    unique = pd.read_csv("KMEL_unique.csv")
    songsUnique = np.array(unique.Song)
    artistsUnique = np.array(unique.Artist)
    timesUnique = np.array(unique.Time)
else:
    songsUnique = np.array([])
    artistsUnique = np.array([])
    timesUnique = np.array([])
#count = 0
#Try just keep running this and updating the csv
while True:
    times, songs, artists = get_recent(url)
    newTimes = []
    newArtists = []
    newSongs = []
    for i in range(len(times)):
        if times[i] not in timesMaster:
            newTimes.append(times[i])
            newArtists.append(html.unescape(artists[i]).replace("&",","))
            newSongs.append(html.unescape(songs[i]))
        if songs[i] not in songsUnique:
            timesUnique = np.append(times[i], timesUnique)
            artistsUnique = np.append(html.unescape(artists[i]).replace("&",","), artistsUnique)
            songsUnique = np.append(songs[i], songsUnique)
    newTimes = np.array(newTimes)
    newArtists = np.array(newArtists)
    newSongs = np.array(newSongs)
    timesMaster = np.append(newTimes, timesMaster)
    artistsMaster = np.append(newArtists, artistsMaster)
    songsMaster = np.append(newSongs, songsMaster)
    total = pd.DataFrame({'Time': timesMaster, 'Artist': artistsMaster, 'Song': songsMaster})
    unique = pd.DataFrame({'Time': timesUnique, 'Artist': artistsUnique, 'Song': songsUnique})
    total.to_csv("KMEL_scraped.csv")
    unique.to_csv("KMEL_unique.csv")
    time.sleep(60)
