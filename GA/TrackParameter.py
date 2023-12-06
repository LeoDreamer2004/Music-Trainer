import numpy as np
from typing import List
from midi.Track import *

class TrackParameter:
    """Used to calculate parameters of the tracks"""
    
    def __init__(self, track: Track) -> None:
        self.track = track
        self.bar_number = track.bar_number
        self.bars: List[List[Note]] = []
        
        self.means = np.zeros(self.bar_number, dtype=float)
        self.standard = np.zeros(self.bar_number, dtype=float)
        self.bad_notes = 0
        self.rhythm_complexity = 0
        self.three_note_score = 0  # the score of three notes in a bar
        
        self.update_parameters()
    
    @staticmethod
    def _interval_to_value(interval: int):
        return interval_value_dict.get(abs(interval), large_interval_value)
    
    def update_parameters(self):
        self.bars = self.track.split_into_bars()
        self._update_interval_parameters()
        self._update_bad_notes()
        if three_note_fitness:
            self._update_three_note_parameters()
    
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
                if abs(diff1 - diff2) <= 2:
                    score_in_bar += 1
            self.three_note_score += len(bar) / ((score_in_bar + 1) * 3)
    
    def _update_bad_notes(self):
        self.bad_notes = 0
        for note in self.track.note:
            if not Note.in_mode(note.pitch, self.track.key):
                self.bad_notes += 1
