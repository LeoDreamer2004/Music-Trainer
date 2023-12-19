from typing import Literal, Union

Key_Major_T = Literal[
    "C", "Db", "D", "Eb", "E", "F", "F#", "E", "G", "Ab", "A", "Bb", "B"
]
Key_Minor_T = Literal[
    "Cm", "C#m", "Dm", "D#m", "Ebm", "Em", "Fm", "F#m", "Gm", "G#m", "Am", "Bbm", "Bm"
]
Key_T = Union[Key_Major_T, Key_Minor_T]
Pitch_T = int
