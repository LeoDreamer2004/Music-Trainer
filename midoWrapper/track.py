import mido
import math
from copy import deepcopy
from random import choice
from typing import List

from .note import *
from .musicSettings import *


class Track:
    """A wrapper for mido.MidiTrack."""

    def __init__(self, instrument: int = 0, key: Key_T = "C"):
        self.instrument = instrument
        self.key = key
        self.note: List[Note] = []

    def __str__(self):  # used for debug
        meta_msg = f"Key: {self.key}\nInstrument: {self.instrument}\n"
        bars = self.split_into_bars()
        note_msg = ""
        for idx, bar in enumerate(bars):
            note_msg += f"\n-------------------  Bar {idx + 1}\n"
            note_msg += "\n".join(str(note) for note in bar)
        return meta_msg + note_msg

    def print_brief_info(self):
        """Brief information of the track."""
        print(f"Key: {self.key}")
        print(f"Instrument: {self.instrument}")
        print(f"Length: {self.full_length}")
        print(f"Bar: {self.bar_number}")

    @staticmethod
    def from_track(track: mido.MidiTrack):
        """Generate a track from a midi track.
        Available for chords."""

        ga_track = Track()
        time = 0
        note_dict = {}  # pitch -> (start_time, velocity)
        for msg in track:
            if msg.type == "program_change":
                ga_track.instrument = msg.program
            elif msg.type == "key_signature":
                ga_track.key = msg.key
            elif msg.type == "note_on":
                time += msg.time
                note_dict[msg.note] = (time, msg.velocity)
            elif msg.type == "note_off":
                time += msg.time
                start_time, velocity = note_dict.pop(msg.note)
                ga_track.note.append(
                    Note(msg.note, time - start_time, start_time, velocity)
                )
        return ga_track

    def to_track(self) -> mido.MidiTrack:
        """Generate a midi track from a track.
        Available for chords."""

        midi_track = mido.MidiTrack()
        midi_track.append(mido.MetaMessage("key_signature", key=self.key, time=0))
        midi_track.append(
            mido.Message("program_change", program=self.instrument, time=0)
        )

        event_set = set()  # (time, 0/1(note_off/on), note)
        for note in self.note:
            event_set.add((note.start_time, 1, note))
            event_set.add((note.start_time + note.length, 0, note))
        # Sort all the events by time. If the time is same, note_off is before note_on.
        sorted_time = sorted(event_set, key=lambda x: (x[0], x[1]))

        last_time = 0
        for event_time, event_num, note in sorted_time:
            event = "note_on" if event_num else "note_off"
            msg = mido.Message(
                event,
                note=note.pitch,
                velocity=note.velocity,
                time=event_time - last_time,
            )
            midi_track.append(msg)
            last_time = event_time
        return midi_track

    def generate_random_pitch_on_rhythm(self, track: "Track"):
        """Generate random pitches on the given track with rhythm."""
        for note in track.note:
            note.pitch = Note.random_pitch_in_mode(self.key)
        # We want the pitch of the last note is the tonic
        while True:
            pitch = Note.random_pitch_in_mode(self.key)
            if Note.ord_in_mode(self.key, pitch) == 1:
                track.note[-1].pitch = pitch
                return track

    def generate_random_track(self, bar_number: int):
        """Generate a random track with the given bar number"""
        for i in range(bar_number - 1):
            length = BAR_LENGTH
            while length > 0:
                note_length = choice(NOTE_LENGTH)
                if note_length <= length:
                    note = Note(0, note_length, (i + 1) * BAR_LENGTH - length)
                    length -= note_length
                    self.note.append(note)

        # For the last bar, we want to make sure that the last note is a half note
        length = BAR_LENGTH
        while length > HALF:
            note_length = choice(NOTE_LENGTH)
            if note_length <= length - HALF:
                note = Note(0, note_length, bar_number * BAR_LENGTH - length)
                length -= note_length
                self.note.append(note)
        note = Note(0, HALF, bar_number * BAR_LENGTH - HALF)
        self.note.append(note)
        self.generate_random_pitch_on_rhythm(self)
        return self

    def split_into_bars(self) -> List[List[Note]]:
        """Split the track into bars."""
        bars = [[] for _ in range(self.bar_number)]
        for note in self.note:
            idx = note.start_time // BAR_LENGTH

            if note.start_time + note.length <= (idx + 1) * BAR_LENGTH:
                bars[idx].append(note)
            else:
                # The note exceeds the bar, split it into two parts
                note1, note2 = deepcopy(note), deepcopy(note)
                bar_time = (idx + 1) * BAR_LENGTH
                note1.length = bar_time - note.start_time
                note2.length = note.start_time + note.length - bar_time
                note2.start_time = bar_time
                bars[idx].append(note1)
                bars[idx + 1].append(note2)
        return bars

    def join_bars(self, bars: List[List[Note]]):
        """Join the bars into a track."""
        self.note = [note for bar in bars for note in bar]
        return self

    @property
    def full_length(self):
        """The length of the track"""
        return max(note.start_time + note.length for note in self.note)

    @property
    def bar_number(self):
        """The number of bars"""
        return math.ceil(self.full_length / WHOLE)

    def transpose(self, interval):
        """Transpose the track by the given interval"""
        for note in self.note:
            note.pitch += interval

    def inverse(self, center):
        """Inverse the track by the given center"""
        for note in self.note:
            note.pitch = 2 * center - note.pitch

    def retrograde(self):
        """Retrograde the track"""
        for note in self.note:
            note.start_time = self.full_length - note.end_time
        self.note.reverse()
