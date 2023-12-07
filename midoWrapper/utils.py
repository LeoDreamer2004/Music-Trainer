import os
import mido

from .note import Key_T
from .track import Track
from .musicSettings import *


def generate_midi(key: Key_T = None):
    """Generate a midi file with meta messages."""
    s = mido.MidiFile()
    meta_track = mido.MidiTrack()
    meta_track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM)))
    meta_track.append(
        mido.MetaMessage("time_signature", numerator=NUMERATOR, denominator=DENOMINATOR)
    )
    if key is not None:
        meta_track.append(mido.MetaMessage("key_signature", key=key, time=0))
    s.tracks.append(meta_track)
    return s


def parse_midi(filename: str):
    """Read a midi file, and return a list of tracks"""
    s = mido.MidiFile(filename)
    return [Track.from_track(track) for track in s.tracks]


def save_midi(s: mido.MidiFile, filename: str):
    """Save a midi file."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    s.save(filename)
