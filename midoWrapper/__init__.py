"""
midoWrapper
=====

A wrapper module for mido. Provide:
* API for note keys.
* A more convenient way for track management.
* Basic utils for midi file.
"""

# flake8: noqa
from .musicSettings import *
from .note import Note
from .note import Key_Major_T, Key_Minor_T, Key_T, Pitch_T
from .track import Track
from .utils import get_midi, save_midi
