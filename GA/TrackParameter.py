import numpy as np
from typing import List
from midi.Track import *
from parameter.pitchParam import *

class TrackParameter:
    """Used to calculate parameters of the tracks"""
    
    def __init__(self, track: Track) -> None:
        self.track = track
        self.bar_number = track.bar_number
        self.bars = self.track.split_into_bars()
        
        # pitch parameters
        self.means = np.zeros(self.bar_number, dtype=float)
        self.standard = np.zeros(self.bar_number, dtype=float)
        self.bad_notes = 0
        self.three_note_score = 0  # the score of three notes in a bar
        # rhythm parameters
        self.strong_beats = 0
        self.echo = 0.
        self.long_notes = 0.
        self.neighboring_notes = 0.
        self.strong_notes_on_weak_beats = 0.
    
    @staticmethod
    def _interval_to_value(interval: int):
        # return interval_value_dict.get(abs(interval), large_interval_value)
        return abs(interval) / 3
    
    def update_pitch_parameters(self):
        self._update_interval_parameters()
        self._update_bad_notes()
        if three_note_fitness:
            self._update_three_note_parameters()
    
    def update_rhythm_parameters(self):
        self._update_beats()
        self._update_echo()
        self._update_long_notes()
    
    def _update_interval_parameters(self):
        for idx, bar in enumerate(self.bars):
            values = []
            for i in range(len(bar) - 1):
                interval = bar[i + 1].pitch - bar[i].pitch
                values.append(self._interval_to_value(interval))
            if idx > 0:
                # add the interval between the last note of the previous bar
                # and the first note of the current bar
                interval = bar[0].pitch - self.bars[idx - 1][-1].pitch
                values.append(self._interval_to_value(interval))
            
            if not values:
                self.means[idx] = 0
                self.standard[idx] = 0
                continue
            
            self.means[idx] = np.mean(values)
            self.standard[idx] = np.std(values)
    
    def _update_three_note_parameters(self):
        """Calculate the score of three notes in a bar.
        If the pitches of three notes is similar to an arithmetic sequence,
        it has better score.
        The more three notes, the lower the score."""
        for bar in self.bars:
            score_in_bar = 0
            for idx in range(len(bar) - 2):
                diff1 = bar[idx + 1].pitch - bar[idx].pitch
                diff2 = bar[idx + 2].pitch - bar[idx + 1].pitch
                if abs(diff1 - diff2) <= 2 and diff1 * diff2 > 0 and (diff1 != 0 or diff2 != 0):
                    # diff1 and diff2 should have the same sign and should not be all 0
                    score_in_bar += 1
            self.three_note_score += len(bar) / ((score_in_bar + 1) * 3)
    
    def _update_bad_notes(self):
        self.bad_notes = 0
        for note in self.track.note:
            if not Note.in_mode(note.pitch, self.track.key):
                self.bad_notes += 1
    
    def _update_beats(self):
        self.strong_beats = 0
        self.strong_notes_on_weak_beats = 0
        for bar in self.bars:
            bad_beats = 0
            for note in bar:
                if note.start_time % HALF == 0:
                    self.strong_beats += 1
                # elif note.start_time % QUARTER == 0:
                # self.weak_beats += 1
                elif note.start_time % note.length != 0:
                    bad_beats += 1
            self.strong_notes_on_weak_beats += bad_beats / len(bar)
    
    def _update_echo(self):
        # Bar 0 and 2; 1 and 3; 4 and 6; 5 and 7 are echo, etc.
        # If they have the similar rhythm, the echo will be higher
        for bar in range(0, self.bar_number, 4):
            self.echo += self._rhythm_similarity_of_bars(
                self.bars[bar], self.bars[bar + 2]
            )
            self.echo += self._rhythm_similarity_of_bars(
                self.bars[bar + 1], self.bars[bar + 3]
            )
    
    def _update_long_notes(self):
        self.long_notes = 0
        for bar in self.bars:
            for note in bar:
                if note.length == HALF:
                    self.long_notes += 1
                elif note.length >= QUARTER:
                    self.long_notes += 0.15
    
    def _update_neighboring_notes(self):
        self.neighboring_notes = 0
        notes = self.track.note
        for idx in range(len(notes) - 1):
            if abs(notes[idx].length - notes[idx + 1].length) == HALF - EIGHTH:
                self.neighboring_notes += 1
    
    @staticmethod
    def _rhythm_similarity_of_bars(bar1: List[Note], bar2: List[Note]):
        """Calculate the similarity of the rhythm of two bars."""
        same = 0
        for note1 in bar1:
            for note2 in bar2:
                if (note1.start_time - note2.start_time) % BAR_LENGTH == 0:
                    same += 1
        return (same ** 2) / (len(bar1) * len(bar2))
