#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create a python library which gives derivation for given verb and tense.

Example
-------

>>> from prakriya import Generate
>>> g = Generate()
# If you are using the library the first time, be patient.
# This will take a long time.
# Data file (30 MB) is being downloaded.
# If you can spare around 600 MB space, decompress the tar.gz first time.
# Subsequent actions will be very fast. This is one time requirement.
>>> g.decompress()
The format is as follows
>>> g[verb, tense]
Actual usage will be like the following.
>>> g['BU']
>>> g['BU', 'law']

For details of valid values for field, see documentation on prakriya class.
"""
import os.path
import sys
from .utils import appDir, readJson, convert
# import datetime


class Generate():
    """Class to get the verb form from given verb, tense, suffix."""

    def __init__(self):
        self.appdir = appDir('prakriya')
        self.inTran = 'slp1'
        self.outTran = 'slp1'
        self.mapform = 'mapforms.json'
        self.mp = os.path.join(self.appdir, self.mapform)
        # If the file does not exist, download from Github.
        if not os.path.exists(self.appdir):
            os.makedirs(self.appdir)
        if not os.path.isfile(self.mp):
            url = 'https://github.com/drdhaval2785/python-prakriya/releases/download/v0.0.2/mapforms.json'
            import requests
            print('Downloading mapform file. Roughly 8 MB.')
            with open(self.mp, "wb") as f:
                r = requests.get(url)
                f.write(r.content)
        self.data = readJson(os.path.join(self.appdir, 'mapforms.json'))
        self.verbmap = readJson(os.path.join(self.appdir, 'verbmap.json'))

    def inputTranslit(self, tran):
        """Set input transliteration."""
        # If valid transliteration, set transliteration.
        if tran in ['slp1', 'itrans', 'hk', 'iast', 'devanagari', 'velthuis',
                    'wx', 'kolkata', 'bengali', 'gujarati', 'gurmukhi',
                    'kannada', 'malayalam', 'oriya', 'telugu', 'tamil']:
            self.inTran = tran
        # If not valid, throw error.
        else:
            print('Error. Not a valid transliteration scheme.')
            exit(0)

    def outputTranslit(self, tran):
        """Set output transliteration."""
        # If valid transliteration, set transliteration.
        if tran in ['slp1', 'itrans', 'hk', 'iast', 'devanagari', 'velthuis',
                    'wx', 'kolkata', 'bengali', 'gujarati', 'gurmukhi',
                    'kannada', 'malayalam', 'oriya', 'telugu', 'tamil']:
            self.outTran = tran
        # If not valid, throw error.
        else:
            print('Error. Not a valid transliteration scheme.')
            exit(0)

    def __getitem__(self, items):
        """Return the requested data by user."""
        # Initiate without arguments
        arguments = ''
        # print(datetime.datetime.now())
        # If there is only one entry in items, it is treated as verbform.
        if isinstance(items, ("".__class__, u"".__class__)):
            print({'error': 'Provide purusha and vachana or suffix.'})
            exit(0)
        else:
            # Otherwise, first is verbform and the next is argument1.
            verb = items[0]
            # py2
            if len(items) > 1 and sys.version_info[0] < 3:
                arguments = [convert(member.decode('utf-8'), self.inTran, 'slp1') for member in items[1:]]
            # py3
            elif len(items) > 1:
                arguments = [convert(member, self.inTran, 'slp1') for member in items[1:]]
            # Enter user defined values
            for member in arguments:
                if member in ['law', 'liw', 'luw', 'lfw', 'low', 'laN',
                              'viDiliN', 'ASIrliN', 'luN', 'lfN']:
                    tense = member
                if member in ['praTama', 'maDyama', 'uttama']:
                    purusha = member
                if member in ['eka', 'dvi', 'bahu']:
                    vachana = member
                if member in ['tip', 'tas', 'Ji', 'sip', 'Tas', 'Ta', 'mip',
                              'vas', 'mas', 'ta', 'AtAm', 'Ja', 'TAs', 'ATAm',
                              'Dvam', 'iw', 'vahi', 'mahiN']:
                    suffix = member
            if 'suffix' in vars():
                suffices = [suffix]
            elif 'purusha' in vars() and 'vachana' in vars():
                suffices = getsuffix(purusha, vachana)
            else:
                print({'error': 'You must provide suffix or (purusha and vachana).'})
                exit(0)
            if 'tense' not in vars():
                print({'error': 'You must provide lakAra (tense/mood).'})
                exit(0)

        # Convert verbform from desired input transliteration to SLP1.
        if sys.version_info[0] < 3:
            verb = verb.decode('utf-8')
        verb = convert(verb, self.inTran, 'slp1')
        # Read from tar.gz file.
        result = self.getform(verb, tense, suffices)
        # Return the result.
        result = [convert(member, 'slp1', self.outTran) for member in result]
        return result

    def getform(self, verb, tense, suffices):
        data = self.data
        result = []
        mappedverbs = self.verbmap
        # If the verb is in data, directly use it.
        if verb in data:
            for suffix in suffices:
                if suffix in data[verb][tense]:
                    lst = data[verb][tense][suffix]
                    for member in lst:
                        if member[0] not in result:
                            result.append(member[0])
        # Otherwise check whether the verb without anubandha is in data
        elif verb in mappedverbs:
            verbs = mappedverbs[verb]
            for verb1 in verbs:
                for suffix in suffices:
                    if suffix in data[verb1][tense]:
                        lst = data[verb1][tense][suffix]
                        for member in lst:
                            if member[0] not in result:
                                result.append(member[0])
        if len(result) == 0:
            print({'error': 'Data is not available.'})
            exit(0)
        return result


def getsuffix(purusha, vachana):
    if purusha == 'praTama' and vachana == 'eka':
        return ['tip', 'ta']
    elif purusha == 'praTama' and vachana == 'dvi':
        return ['tas', 'AtAm']
    elif purusha == 'praTama' and vachana == 'bahu':
        return ['Ji', 'Ja']
    elif purusha == 'maDyama' and vachana == 'eka':
        return ['sip', 'TAs']
    elif purusha == 'maDyama' and vachana == 'dvi':
        return ['Tas', 'ATAm']
    elif purusha == 'maDyama' and vachana == 'bahu':
        return ['Ta', 'Dvam']
    elif purusha == 'uttama' and vachana == 'eka':
        return ['mip', 'iw']
    elif purusha == 'uttama' and vachana == 'dvi':
        return ['vas', 'vahi']
    elif purusha == 'uttama' and vachana == 'bahu':
        return ['mas', 'mahiN']
