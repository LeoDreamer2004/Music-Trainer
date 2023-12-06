import mido
import math
from copy import deepcopy
from random import choice
from typing import List

from midi.Note import *
from param import *

class Track:
    """A wrapper for mido.MidiTrack."""
    
    def __init__(self, instrument: int = 0, key: Key_T = 'C'):
        self.instrument = instrument
        self.key = key
        self.note: list[Note] = []
    
    def __str__(self):  # used for debug
        meta_msg = f"Key: {self.key}\nInstrument: {self.instrument}\n"
        note_msg = '\n'.join([str(note) for note in self.note])
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
            if msg.type == 'program_change':
                ga_track.instrument = msg.program
            elif msg.type == 'key_signature':
                ga_track.key = msg.key
            elif msg.type == 'note_on':
                time += msg.time
                note_dict[msg.note] = (time, msg.velocity)
            elif msg.type == 'note_off':
                time += msg.time
                start_time, velocity = note_dict.pop(msg.note)
                ga_track.note.append(
                    Note(msg.note, time - start_time, start_time, velocity))
        return ga_track
    
    def to_track(self) -> mido.MidiTrack:
        """Generate a midi track from a track.
        Available for chords."""
        
        midi_track = mido.MidiTrack()
        midi_track.append(mido.MetaMessage(
            'key_signature', key=self.key, time=0))
        midi_track.append(mido.Message(
            'program_change', program=self.instrument, time=0))
        
        event_set = set()  # (time, 0/1(note_off/on), note)
        for note in self.note:
            event_set.add((note.start_time, 1, note))
            event_set.add((note.start_time + note.length, 0, note))
        # Sort all the events by time. If the time is same, note_off is before note_on.
        sorted_time = sorted(event_set, key=lambda x: (x[0], x[1]))
        
        last_time = 0
        for time, event_num, note in sorted_time:
            event = 'note_on' if event_num else 'note_off'
            msg = mido.Message(
                event, note=note.pitch, velocity=note.velocity, time=time - last_time)
            midi_track.append(msg)
            last_time = time
        return midi_track
    
    def generate_random_track(self, bar: int):
        """Generate a random track with the given bar length."""
        for i in range(bar):
            length = BAR_LENGTH
            while length > 0:
                l = choice(NOTE_LENGTH)
                if l <= length:
                    pitch = Note.random_pitch_in_mode(self.key)
                    note = Note(pitch, l, (i + 1) * BAR_LENGTH - length)
                    length -= l
                    self.note.append(note)
        return self
    
    def _recommend_length(left_length: int):
        # Recommend a length for the note with the given left length.
        # For example, if left_length is 3.5, it's better to give a eighth note,
        # because it can align with the beat.
        pass
    
    def generate_random_track_plus(self, bar: int):
        """Generate a random track with the given bar length.
        The track has a better rhythm."""
        for i in range(bar - 1):
            length = BAR_LENGTH
            while length > 0:
                if length % QUARTER != 0:
                    # if the beat is not full, we recommend a quarter note or a eighth note
                    l = choice([QUARTER, EIGHTH])
                else:
                    l = choice(NOTE_LENGTH)
                if l <= length:
                    pitch = Note.random_pitch_in_mode(self.key)
                    note = Note(pitch, l, (i + 1) * BAR_LENGTH - length)
                    length -= l
                    self.note.append(note)
        
        # For the last bar, we need to make sure that the last note is a half note
        # We also want the pitch of the last note is the tonic
        length = BAR_LENGTH
        while length > HALF:
            l = choice(NOTE_LENGTH)
            if l <= length - HALF:
                pitch = Note.random_pitch_in_mode(self.key)
                note = Note(pitch, l, bar * BAR_LENGTH - length)
                length -= l
                self.note.append(note)
        while True:
            pitch = Note.random_pitch_in_mode(self.key)
            if Note.ord_in_mode(self.key, pitch) == 1:
                break
        note = Note(pitch, HALF, bar * BAR_LENGTH - HALF)
        self.note.append(note)
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
            note.start_time = self.full_length - note.start_time - note.length
        self.note.reverse()
