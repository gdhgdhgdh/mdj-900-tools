#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import configparser
import io
import shutil
import subprocess
import os
import tempfile
import struct
import sys
import mutagen

FMT_VERSION = 'BB'

camelot_keys = {
  'Abm': '1A',
  'G#m': '1A',
  'B':   '1B',
  'Ebm': '2A',
  'F#':  '2B',
  'Bbm': '3A',
  'Db':  '3B',
  'Fm':  '4A',
  'Ab':  '4B',
  'Cm':  '5A',
  'Eb':  '5B',
  'Gm':  '6A',
  'Bb':  '6B',
  'Dm':  '7A',
  'F':   '7B',
  'Am':  '8A',
  'C':   '8B',
  'Em':  '9A',
  'G':   '9B',
  'Bm':  '10A',
  'D':   '10B',
  'F#m': '11A',
  'A':   '11B',
  'C#m': '12A',
  'Dbm': '12A',
  'E':   '12B',
}

def readbytes(fp):
    for x in iter(lambda: fp.read(1), b''):
        if x == b'\00':
            break
        yield x


def parse(fp):
    version = struct.unpack(FMT_VERSION, fp.read(2))
    assert version == (0x01, 0x01)

    for i in range(3):
        data = b''.join(readbytes(fp))
        yield float(data.decode('ascii'))


def renamefile(filename, bpm, music_key, tag):
    newname = f'/Users/gdh/Desktop/qwe2/{bpm} {music_key} {tag["TPE1"][0][:15]} % {tag["TIT2"]}.mp3'
    print('New name: ', newname)
    os.rename(filename, newname)
    return


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='FILE')
    args = parser.parse_args(argv)

    tagfile = mutagen.File(args.file)
    if tagfile is not None:
        try:
            tag = tagfile['GEOB:Serato Autotags']
            music_key = tagfile['TKEY']
        except KeyError:
            print('File is missing "GEOB:Serato Autotags" or "TKEY" tag')
            return 1
        else:
            fp = io.BytesIO(tag.data)
    else:
        fp = open(args.file, mode='rb')

    with fp:
        bpm, autogain, gaindb = parse(fp)

    print('BPM: {}'.format(int(bpm)))
    music_key = format(music_key)
    if not music_key[0].isnumeric(): 
        music_key = camelot_keys[music_key]
    print('Key: {}'.format(music_key))
    renamefile(args.file, int(bpm), music_key, tagfile)
    return 0


if __name__ == '__main__':
    sys.exit(main())
