"""
midoWrapper
=====

A wrapper module for `mido`. Provide:
* API for note keys.
* A more convenient way for track management.
* Basic utils for midi file.

tips: the module not include `mido`, you should import it when you need.
"""

# flake8: noqa
from .musicType import *
from .musicSettings import MusicSettings
from .note import Note
from .track import Track, Bar
from .midi import Midi
