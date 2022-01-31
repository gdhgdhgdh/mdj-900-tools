#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import ast
import base64
import configparser
import io
import math
import os
import shutil
import sqlite3
import struct
import subprocess
import sys
import tempfile
import mutagen

from sqlite3 import Error

FMT_VERSION = 'BB'
# CREATE TABLE outer_table (id integer PRIMARY KEY, absolute_path text NOT NULL UNIQUE, sync_path text, duration_in_frames integer, 
# cue text, hcue1 text, hcue2 text, hcue3 text, hcue4 text, hcue5 text, hcue6 text, hcue7 text, hcue8 text, 
# loop_in text, loop_out text, have_cue text, have_loop text, title text, artist text, album text, genre text,
# bitrate integer, samplerate integer, bpm float, offset integer, have_cover text, is_unsupported text);

# INSERT INTO "table" VALUES(3,'/Mixxx/brunch_/02 - Lalo Schifrin - Scorpio''s Theme (''Dirty Harry'').mp3','02 - Lalo Schifrin - Scorpio''s Theme (''Dirty Harry'').mp3',
# 14100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Scorpio''s Theme (''Dirty Harry'')','Lalo Schifrin','Dirty Harry Definitive Collection : The Dirty Harry Anthology','Soundtrack',
# 320,44100,99.151123000000005447,4814,'no','no');

def open_db():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect('gemini_bd.sqlite')
        print(sqlite3.version)
    except Error as e:
        print(e)
    return conn


def add_track(conn, filename, track):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM outer_table")
    print(cur.fetchall())
    print(track['TIT2'])
    print(track['TPE1'])
    print("Tempo from ID3 TBPM: " + str(track['TBPM']))
    tempo = str(float(track['GEOB:Serato Autotags'].data[2:7]))
    print("Tempo from Serato Autotags object: " + tempo)
    cur.execute("INSERT INTO outer_table VALUES (NULL,?,?,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,?,?,NULL,NULL,320,44100,?,0,'no','no')", ('/' + os.path.basename(filename), os.path.basename(filename), str(track['TIT2']), str(track['TPE1']), tempo ) )
    conn.commit()
    print(f"done {filename}")


def readbytes(fp):
    for x in iter(lambda: fp.read(1), b''):
        if x == b'\00':
            break
        yield x


class Entry(object):
    def __init__(self, *args):
        assert len(args) == len(self.FIELDS)
        for field, value in zip(self.FIELDS, args):
            setattr(self, field, value)

    def __repr__(self):
        return '{name}({data})'.format(
            name=self.__class__.__name__,
            data=', '.join('{}={!r}'.format(name, getattr(self, name))
                           for name in self.FIELDS))


class UnknownEntry(Entry):
    NAME = None
    FIELDS = ('data',)

    @classmethod
    def load(cls, data):
        return cls(data)

    def dump(self):
        return self.data


class CueEntry(Entry):
    NAME = 'CUE'
    FMT = '>cBIc3s2s'
    FIELDS = ('field1', 'index', 'position', 'field4', 'color', 'field6',
              'name',)

    @classmethod
    def load(cls, data):
        info_size = struct.calcsize(cls.FMT)
        info = struct.unpack(cls.FMT, data[:info_size])
        name, nullbyte, other = data[info_size:].partition(b'\x00')
        assert nullbyte == b'\x00'
        assert other == b''
        return cls(*info, name.decode('utf-8'))

    def dump(self):
        struct_fields = self.FIELDS[:-1]
        return b''.join((
            struct.pack(self.FMT, *(getattr(self, f) for f in struct_fields)),
            self.name.encode('utf-8'),
            b'\x00',
        ))


def get_entry_type(entry_name):
    entry_type = UnknownEntry
    for entry_cls in (UnknownEntry, UnknownEntry, CueEntry, UnknownEntry, UnknownEntry):
        if entry_cls.NAME == entry_name:
            entry_type = entry_cls
            break
    return entry_type


def parse(data):
    versionlen = struct.calcsize(FMT_VERSION)
    version = struct.unpack(FMT_VERSION, data[:versionlen])
    assert version == (0x01, 0x01)

    b64data = data[versionlen:data.index(b'\x00', versionlen)].replace(b'\n', b'')
    padding = b'A==' if len(b64data) % 4 == 1 else (b'=' * (-len(b64data) % 4))
    payload = base64.b64decode(b64data + padding)
    fp = io.BytesIO(payload)
    assert struct.unpack(FMT_VERSION, fp.read(2)) == (0x01, 0x01)
    while True:
        entry_name = b''.join(readbytes(fp)).decode('utf-8')
        if not entry_name:
            break
        entry_len = struct.unpack('>I', fp.read(4))[0]
        assert entry_len > 0

        entry_type = get_entry_type(entry_name)
        yield entry_type.load(fp.read(entry_len))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='FILE')
    args = parser.parse_args(argv)

    tagfile = mutagen.File(args.file)
    if tagfile is not None:
        try:
            data = tagfile['GEOB:Serato Autotags'].data
        except KeyError:
            print('File is missing "GEOB:Serato Autotags" tag')
            return 1
    conn = open_db();
    add_track(conn, args.file, tagfile)

    #entries = list(parse(data))

    #for entry in enumerate(entries):
#            print(entry.index)
    #        print('{!r}'.format(entry))
    #        print('{}'.format(entry))

    return 0


if __name__ == '__main__':
    sys.exit(main())
