import os
import mido

from .note import Key_T
from .musicSettings import *


def get_midi(key: Key_T = None):
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


def save_midi(s: mido.MidiFile, filename: str):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    s.save(filename)
