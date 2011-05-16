import os

import helper
import musicAPI.lastFM
import musicAPI.pandora
from song import Song

import mutagen

def tagSong(root, location):
    try:
        song = Song(location)
    except mutagen.id3.ID3NoHeaderError:
        return

    info = {}
    if song.tags['title'][0] and song.tags['artist'][0]:
        trackInfo = musicAPI.lastFM.getTrackInfo(song.tags['title'][0], song.tags['artist'][0])
    if trackInfo:
        if 'album' in trackInfo:
            song.tags['album'] = trackInfo['album']
            song.tags.save()
        info.update(trackInfo)

    if song.tags['album'][0] and song.tags['artist'][0]:
        albumInfo = musicAPI.lastFM.getAlbumInfo(song.tags['album'][0], song.tags['artist'][0])
    if albumInfo:
        info.update(albumInfo)

    try:
        info['tracknumber'] = '%s/%s' % (info['trackPosition'], info['totalTracks'])
    except KeyError:
        pass
    for tag in ['trackPosition', 'totalTracks']:
        if tag in info:
            del info[tag]

    print(info)

    for tag in info:
        song.tags[tag] = info[tag]

    lyrics = musicAPI.pandora.getLyrics(song.tags['artist'][0], song.tags['title'][0])
    if lyrics:
        song.tags['lyrics'] = lyrics

    song.tags.save()

    artist = helper.cleanPath(song.tags['artist'][0])
    album = helper.cleanPath(song.tags['album'][0])
    title = helper.cleanPath(song.tags['title'][0])

    extension = os.path.splitext(location)[1]
    newLocation = os.path.join(root, artist, album, title + extension)
    print(location.encode('utf-8'))
    print(location.encode('utf-8') + 'x')
    print(newLocation.encode('utf-8'))
    if os.path.exists(newLocation) is False or os.path.abspath(location) == os.path.abspath(newLocation) is False or location != newLocation:
        # workaround for inability to rename to already existing file (i.e. case-sensitiviy)
        os.renames(location, location + 'x')
        os.renames(location + 'x', newLocation)

def tagDirectory(root):
    i = 1
    for dir, subdirs, files in os.walk(root, topdown=False):
        for name in files:
            print(i)
            tagSong(root, os.path.join(dir, name))
            i += 1

    # appears to be unneeded since os.renames does all this auto.
    """
        for name in subdirs:
            currDir = os.path.join(dir, name)
            if os.listdir(currDir) == []:
                try:
                    os.rmdir(currDir)
                except OSError:
                    # need error message here in case of permission error
                    pass
    """

