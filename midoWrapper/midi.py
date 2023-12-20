import os
import mido
from typing import List
from .musicSettings import MusicSettings
from .track import Track


class Midi:
    """A wrapper for mido.Midifile"""

    def __init__(self, settings: MusicSettings = None):
        self.sts = settings if settings is not None else MusicSettings()
        self.tracks: List[Track] = []

    def brief_info(self):
        msg = f"Key: {self.sts.key}\n"
        msg += f"Rhythm: {self.sts.numerator}/{self.sts.denominator}\n"
        msg += f"BPM: {self.sts.bpm}\n"
        msg += f"Bar: {self.sts.bar_number}\n"
        return msg

    def to_mido_midi(self) -> mido.MidiFile:
        """Convert to mido.MidiFile"""
        s = mido.MidiFile()
        meta_track = mido.MidiTrack()
        meta_track.append(
            mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(self.sts.bpm))
        )
        meta_track.append(
            mido.MetaMessage(
                "time_signature",
                numerator=self.sts.numerator,
                denominator=self.sts.denominator,
            )
        )
        if self.sts.key is not None:
            meta_track.append(
                mido.MetaMessage("key_signature", key=self.sts.key, time=0)
            )
        s.tracks.append(meta_track)
        for track in self.tracks:
            s.tracks.append(track.to_mido_track())
        return s

    @staticmethod
    def from_midi(filename: str) -> "Midi":
        midi = mido.MidiFile(filename)
        meta_track = midi.tracks[0]
        ga_midi = Midi()
        parsed = False
        if Midi._is_meta_track(meta_track):
            ga_midi._parse_midi_parameters(meta_track)
            parsed = True
            midi.tracks.pop(0)
        for track in midi.tracks:
            if not parsed:
                ga_midi._parse_midi_parameters(track)
                parsed = True
            ga_midi.tracks.append(Track(ga_midi.sts).from_mido_track(track))
        ga_midi.sts.bar_number = max(track.bar_number for track in ga_midi.tracks)
        return ga_midi

    def save_midi(self, filename: str):
        """Save a midi file."""
        midi = self.to_mido_midi()
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        midi.save(filename)

    @staticmethod
    def _is_meta_track(track: mido.MidiTrack):
        # if there are no notes, it is a meta track
        for msg in track:
            if msg.type == "note_on":
                return False
        return True

    def _parse_midi_parameters(self, track: mido.MidiTrack):
        for msg in track:
            if msg.type == "set_tempo":
                self.sts.bpm = mido.tempo2bpm(msg.tempo)
            elif msg.type == "time_signature":
                self.sts.numerator = msg.numerator
                self.sts.denominator = msg.denominator
            elif msg.type == "key_signature":
                self.sts.key = msg.key
