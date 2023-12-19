import os
import mido
from typing import List
from .musicSettings import MusicSettings
from .track import Track


class Midi:
    """A wrapper for mido.Midifile"""

    def __init__(self, settings: MusicSettings = None):
        self.settings = settings if settings is not None else MusicSettings()
        self.tracks: List[Track] = []

    def to_mido_midi(self) -> mido.MidiFile:
        """Convert to mido.MidiFile"""
        s = mido.MidiFile()
        meta_track = mido.MidiTrack()
        meta_track.append(
            mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(self.settings.bpm))
        )
        meta_track.append(
            mido.MetaMessage(
                "time_signature",
                numerator=self.settings.numerator,
                denominator=self.settings.denominator,
            )
        )
        if self.settings.key is not None:
            meta_track.append(
                mido.MetaMessage("key_signature", key=self.settings.key, time=0)
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
            ga_midi.tracks.append(Track(ga_midi.settings).from_mido_track(track))
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
                self.settings.bpm = mido.tempo2bpm(msg.tempo)
            elif msg.type == "time_signature":
                self.settings.numerator = msg.numerator
                self.settings.denominator = msg.denominator
            elif msg.type == "key_signature":
                self.settings.key = msg.key
